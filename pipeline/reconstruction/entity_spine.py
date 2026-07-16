"""Era-aware entity spine for the Luck / finhist reconstruction — the shared library.

Every builder in this module (build_luck_equivalent / build_luck_core /
build_finhist_equivalent / build_clv_analysis_panel) forms and links entity ids the
same way, so entity construction lives here once. All functions are **pure functions
over pandas DataFrames / Series** (a DuckDB relation should be materialised to a frame
or expressed in SQL by the caller) — this module NEVER writes to the warehouse.

Authority: RECONSTRUCTION_SPEC.md **§6.1 "Entity spine — how IDs are formed and linked
across eras"**, which cites the CLV do-files `04_create-historical-dataset.do`,
`05_create-modern-dataset.do`, and `07_combine-*.do`, plus freeNIC's
`45_build_clean_bank_panel.py`.

Spec anchors are tagged on each function as ``SPEC-ANCHOR:`` so the Batch-3 refresh
(after the G-SPEC adversarial checker may amend §6.1) is mechanical — grep the anchors,
re-diff against the amended section.

Citation posture (D3, plan §R4b + LICENSE_POSTURE.md §2b): this is **original Python
implementing the documented method**. Do-file lines are cited as loci ("implements
05 L66-77"); no CLV code is copied.

The three era rules (SPEC §6.1), each with its own key builder:

  * **HIST 1863-1941** — OCC charter. ``hist_version`` / ``hist_entity_id`` implement
    04's ``10*bank_id+version`` (04 L14-18). **G-SPEC note:** that version-id is a
    *transient* xtset id, dropped before delivery (04 L133-139 keep-list); the delivered
    HIST panel keys on ``bank_id`` (the charter), so a bank that re-enters receivership is
    **pooled under one charter entity, not split**. ``hist_panel_key`` returns the
    charter — use it for the persistent HIST entity key.
  * **1959Q4-1975Q4 (MODL)** — FDIC-certificate keyed, with the ``-id_rssd`` negative
    surrogate fallback + post-failure pseudo-id. ``resolve_fdic_cert`` /
    ``modern_bank_id`` (implements 05 L53-81).
  * **1976-2026 (MODC)** — RSSD-native (Fed-direct raw carries ``rssd_id``).
    ``modc_rssd_key`` (implements 30_build one-row-per rssd_id x period_end).

The eras are **APPENDED, never joined** — no entity persists across the 1942-1958 gap
(SPEC §6.1 header, ``07 L11-12``). ``assert_eras_disjoint`` enforces the numeric
range-disjointness (``05 L77`` scaling) that makes the append safe. Cell-level
validation aligns on the natural key ``(id_rssd, period_end)`` — ``alignment_key``.

Runtime deps: pandas (+ numpy, via pandas). No warehouse access.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Era constants (SPEC §0 boundary table + §6.1). Period boundaries are inclusive
# of the named quarters. 1942-1958 is a GENUINE GAP, kept absent (SPEC §0).
# ---------------------------------------------------------------------------
HIST = "HIST"   # 1863-1941  (OCC historical / finhist)
MODL = "MODL"   # 1959Q4-1975Q4  (the .dta modern-legacy era)
MODC = "MODC"   # 1976-2026  (Fed-direct MDRM re-derivation)
GAP = "GAP"     # 1942-1958  (genuine gap; no entities)

HIST_YEAR_MAX = 1941
GAP_YEAR_MIN = 1942
GAP_YEAR_MAX = 1958
MODL_YEAR_MIN = 1959
MODL_YEAR_MAX = 1975
MODC_YEAR_MIN = 1976

#: The range-disjointness scale (SPEC §6.1 "MODERN spine", ``05 L77``:
#: ``bank_id = bank_id*1e5``). Multiplying the FDIC-cert-derived modern id by this
#: lifts it clear of the 5-digit OCC charter range so HIST and MODERN ids can share
#: one column without ever colliding — the mechanism that makes append-not-join safe.
MODERN_DISJOINT_SCALE = 100_000  # 1e5 (the literal 05 L77 multiplier)

#: OCC charter numbers are 5-digit (<= 99999); the HIST entity id is ``10*charter+version``,
#: so HIST ids stay below 1e6.
OCC_CHARTER_CEILING = 100_000

#: The era-partition boundary (SPEC §6.1 G-SPEC note: "modern ids (>= 1e6 scale) cannot
#: collide with 5-digit OCC charter numbers"). A modern id is ``cert*10*1e5 = cert*1e6``,
#: so |modern id| >= 1e6 for any cert; HIST ids (10*charter+version) stay below 1e6. This
#: is the number ``assert_eras_disjoint`` partitions on.
MODERN_ID_FLOOR = 1_000_000  # 1e6

#: The cell-level validation alignment key (SPEC §6.1 recommendation): both the CLV
#: .dta and ``call_report_filings`` carry an RSSD id and a period end.
ALIGNMENT_KEY = ("id_rssd", "period_end")


def era_of_year(year) -> str:
    """Map a calendar year to its reconstruction era group (SPEC §0 / §6.1).

    Returns one of HIST / MODL / MODC / GAP. The GAP (1942-1958) is returned
    explicitly so callers can assert it stays empty rather than silently coercing it.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §0 (boundary table).
    """
    y = int(year)
    if y <= HIST_YEAR_MAX:
        return HIST
    if y <= GAP_YEAR_MAX:
        return GAP
    if y <= MODL_YEAR_MAX:
        return MODL
    return MODC


def era_series(years: Iterable) -> pd.Series:
    """Vectorised :func:`era_of_year` over a year-like Series/array. SPEC §0/§6.1."""
    s = pd.Series(list(years)) if not isinstance(years, pd.Series) else years
    y = s.astype("Int64")
    out = pd.Series(np.where(y <= HIST_YEAR_MAX, HIST,
                    np.where(y <= GAP_YEAR_MAX, GAP,
                    np.where(y <= MODL_YEAR_MAX, MODL, MODC))),
                    index=s.index, dtype=object)
    out[y.isna()] = pd.NA
    return out


# ===========================================================================
# HIST spine — OCC charter + receiver-restart versioning
# SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 "HIST spine" (implements 04 L10-20)
# ===========================================================================
def hist_version(
    df: pd.DataFrame,
    bank_id_col: str = "bank_id",
    year_col: str = "year",
    end_date_col: str = "end_date",
) -> pd.Series:
    """Receiver-restart version number per OCC bank history (the TRANSIENT 04 id).

    Implements ``04 L14-18``: within each ``bank_id`` history ordered by year, a new
    version is minted **each time the bank's ``end_date`` changes** —
    ``version = sum(end_date != end_date[_n-1])`` (a running count of changes). The
    first record in a history counts as version 1 (its end_date differs from the missing
    predecessor), matching the Stata running ``sum()``.

    **G-SPEC correction (SPEC §6.1):** the resulting ``id = 10*bank_id+version`` is a
    *transient* xtset id — it is dropped before the panel is delivered (not in the
    ``04 L133-139`` keep-list) and no time-series operator runs against it, so it has no
    downstream effect. The delivered HIST panel keys on ``bank_id`` (charter), which
    **pools** a re-entering bank under one entity rather than splitting it. This function
    is retained because the builders reproduce 04's intermediate xtset; for the persistent
    entity key use :func:`hist_panel_key`.

    Returns an int Series (aligned to ``df.index``) of version numbers >= 1.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 HIST spine / 04 L14-18 (+ G-SPEC correction).
    """
    order = df.sort_values([bank_id_col, year_col]).index
    d = df.loc[order]
    grp = d.groupby(bank_id_col, sort=False)[end_date_col]
    changed = d[end_date_col].ne(grp.shift())          # True on the first row and on each change
    version = changed.groupby(d[bank_id_col], sort=False).cumsum().astype("int64")
    return version.reindex(df.index)


def hist_entity_id(bank_id, version) -> "pd.Series | int":
    """OCC transient xtset id = ``10*bank_id + version`` (``04 L18``).

    Scalar-in / scalar-out, or elementwise over Series. This is 04's *transient* id (see
    :func:`hist_version` — dropped before delivery per the G-SPEC correction). A 5-digit
    charter (<= 99999) with a small version yields an id below :data:`MODERN_ID_FLOOR`
    (1e6), so it stays disjoint from the modern range; the persistent HIST entity key is
    the charter itself (:func:`hist_panel_key`).

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 HIST spine / 04 L18 (transient id).
    """
    if isinstance(bank_id, pd.Series) or isinstance(version, pd.Series):
        return 10 * pd.Series(bank_id) + pd.Series(version)
    return 10 * int(bank_id) + int(version)


def hist_panel_key(bank_id) -> pd.Series:
    """The persistent HIST entity key = the OCC ``bank_id`` (charter) itself.

    G-SPEC correction (SPEC §6.1): the delivered combined panel keys HIST on ``bank_id``
    (``07 L111`` ``xtset bank_id quarter``; ``failed_bank`` is ``by(bank_id)`` at
    ``04 L33``), NOT on the transient ``10*bank_id+version`` id. A bank that re-enters
    receivership is therefore pooled under its one charter. Returns the charter as an
    ``Int64`` Series.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 HIST spine G-SPEC correction / 04 L133-139, 07 L111.
    """
    return pd.Series(bank_id, dtype="Int64")


# ===========================================================================
# MODERN spine (MODL, 1959-75 .dta) — FDIC cert, -id_rssd fallback, failure pseudo-id
# SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 "MODERN spine" (implements 05 L53-81)
# ===========================================================================
def resolve_fdic_cert(id_fdic_cert: pd.Series, id_rssd: pd.Series) -> pd.Series:
    """Resolve the FDIC-certificate linking key with the ``-id_rssd`` fallback.

    Implements ``05 L54-59`` ID hygiene:
      * a **zero** cert -> missing (``05 L54-55``);
      * a **missing** cert -> filled with ``-id_rssd`` (the negative RSSD surrogate,
        ``05 L58``) so the FDIC-failure merge is complete;
      * a row still missing a cert (rssd also absent) -> NA, and the caller DROPS it
        (``05 L59``; see :func:`drop_unkeyed`).

    Returns a nullable ``Int64`` Series of resolved certs (negative == RSSD surrogate,
    NA == drop).

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 MODERN spine / 05 L54-59.
    """
    cert = pd.Series(id_fdic_cert, dtype="Float64").copy()
    rssd = pd.Series(id_rssd, dtype="Float64")
    cert = cert.mask(cert == 0, other=pd.NA)                 # zero -> missing (05 L54-55)
    need = cert.isna() & rssd.notna() & (rssd != 0)
    cert = cert.mask(need, other=-rssd)                      # missing -> -id_rssd (05 L58)
    return cert.astype("Int64")


def drop_unkeyed(df: pd.DataFrame, cert_col: str = "id_fdic_cert_resolved") -> pd.DataFrame:
    """Drop rows still missing a resolved cert (``05 L59``). Returns a filtered copy.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 MODERN spine / 05 L59.
    """
    return df[df[cert_col].notna()].copy()


def modern_bank_id(
    resolved_cert,
    past_fail_1=0,
    past_fail_2=0,
    disjoint_scale: int = MODERN_DISJOINT_SCALE,
):
    """Modern entity id with post-failure pseudo-id bump + range-disjoint scaling.

    Implements ``05 L66-77``:
        ``bank_id = id_fdic_cert*10 + (qofd(fail_day)<=quarter) + (qofd(fail_day2)<=quarter)``
        then ``bank_id = bank_id*1e5``.

    The two ``past_fail_*`` flags are the already-evaluated quarter comparisons
    ``(fail-quarter <= this quarter)`` as 0/1 (Stata's ``qofd(...)<=quarter``). Passing
    them in (rather than doing date arithmetic here) keeps this a pure, unit-testable
    function. Quarters **after** a failure event get a bumped id, so an acquirer that
    later fails becomes a **new entity**, and the rare multiple-failure case is handled
    by the second flag (SPEC §6.1). The final ``*1e5`` lifts the id clear of OCC
    charters (|modern id| >= 1e6) so eras append without collision (``05 L77``).

    **G-SPEC note (SPEC §6.1):** a cert-missing bank carries the negative surrogate
    ``cert = -id_rssd`` (from :func:`resolve_fdic_cert`), which flows through here to a
    **negative bank_id** — this is legitimate and still disjoint (positive HIST charters
    and positive modern certs on one side, |value| >= 1e6 on the modern side).

    Scalar-in / scalar-out, or elementwise over Series.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 MODERN spine / 05 L66-77 (+ negative-surrogate note).
    """
    if isinstance(resolved_cert, pd.Series):
        # A scalar flag broadcasts; a Series/array flag aligns BY POSITION (via np.asarray,
        # which drops any foreign index) so it can't silently misalign to NA.
        pf1 = past_fail_1 if np.isscalar(past_fail_1) else np.asarray(past_fail_1)
        pf2 = past_fail_2 if np.isscalar(past_fail_2) else np.asarray(past_fail_2)
        base = resolved_cert.astype("Int64") * 10 + pf1 + pf2
        return base * disjoint_scale
    return (int(resolved_cert) * 10 + int(past_fail_1) + int(past_fail_2)) * disjoint_scale


# ===========================================================================
# MODC spine (1976-2026) — RSSD-native (Fed-direct raw carries rssd_id)
# SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 + §5 (30_build: one row per rssd_id x period_end)
# ===========================================================================
def modc_rssd_key(rssd_id, period_end=None) -> pd.Series:
    """RSSD-native entity key for the 1976+ Fed-direct re-derivation.

    ``30_build_public_luck_panel.py`` builds one row per ``rssd_id x period_end``
    directly from ``call_report_filings`` (SPEC §5). For 1976+ the entity IS the RSSD;
    there is no cert remapping. Returns the rssd id as an ``Int64`` Series (period_end
    is accepted for signature symmetry with the other era builders and is not folded
    into the key — the key is the entity, the period is the alignment axis).

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 (freeNIC spine, MODERN on rssd_id) / §5.
    """
    return pd.Series(rssd_id, dtype="Int64")


# ===========================================================================
# freeNIC unified entity key (METHOD-CHOICE vs CLV's FDIC-cert bank_id) — 45_build
# SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 "freeNIC spine" (45_build add_growth L495-498)
# ===========================================================================
def freenic_entity_key(
    era_group: pd.Series,
    bank_id: pd.Series,
    rssd_id: pd.Series,
    src_vintage: pd.Series | None = None,
) -> pd.Series:
    """freeNIC's string entity key: ``"H"+bank_id`` for HIST else ``"M"+vintage+"_"+rssd``.

    Implements ``45_build add_growth L495-498``. This is a documented **METHOD-CHOICE**
    vs CLV's FDIC-cert ``bank_id`` (SPEC §6.1): freeNIC keys MODERN on ``rssd_id``, so
    freeNIC entity ids will NOT equal CLV's cert-derived ids. Use this for freeNIC's own
    panel identity; use :func:`modern_bank_id` (05's rule) only when reproducing CLV's
    entity-level regressions for the tri-engine anchor (Part V).

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 freeNIC spine / 45_build add_growth L495-498.
    """
    era = pd.Series(era_group).astype(object)
    bid = pd.Series(bank_id).astype("string")
    rssd = pd.Series(rssd_id).astype("string")
    if src_vintage is None:
        vint = pd.Series([""] * len(era), index=era.index, dtype="string")
    else:
        vint = pd.Series(src_vintage).astype("string")
    modern = "M" + vint + "_" + rssd
    return pd.Series(np.where(era == HIST, "H" + bid, modern), index=era.index, dtype=object)


# ===========================================================================
# Append-not-join invariants + the validation alignment key
# ===========================================================================
def alignment_key(df: pd.DataFrame, key: Iterable[str] = ALIGNMENT_KEY) -> pd.DataFrame:
    """Return the ``(id_rssd, period_end)`` cell-level validation alignment key columns.

    SPEC §6.1 recommendation: validation aligns on this natural key (present in both the
    CLV .dta and ``call_report_filings``), NOT on the divergent entity ids. Raises if a
    key column is absent so the harness can't silently mis-align.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 (alignment recommendation).
    """
    missing = [c for c in key if c not in df.columns]
    if missing:
        raise KeyError(f"alignment key column(s) absent: {missing}; have {list(df.columns)}")
    return df.loc[:, list(key)]


def assert_eras_disjoint(hist_ids: pd.Series, modern_ids: pd.Series) -> None:
    """Assert HIST and MODERN entity ids occupy disjoint numeric ranges (append-safe).

    SPEC §6.1: the eras are APPENDED not joined (``07 L11-12``); the ``05 L77`` ``*1e5``
    scaling guarantees ``|modern id| >= 1e6`` while HIST ids (``10*charter+version``, 5-digit
    charter) stay below 1e6 — the G-SPEC-corrected boundary is :data:`MODERN_ID_FLOOR`.
    Enforceable invariant: HIST ids are **positive and below** ``MODERN_ID_FLOOR``; MODERN
    ids have ``abs(id) >= MODERN_ID_FLOOR`` (a **negative** modern id from the ``-id_rssd``
    surrogate is legitimate, SPEC §6.1); the two id sets must not intersect. Raises
    AssertionError with a diagnostic on any violation.

    SPEC-ANCHOR: RECONSTRUCTION_SPEC.md §6.1 (append-not-join / range-disjointness, 05 L77 / 07 L11-12; G-SPEC 1e6 + negative-surrogate).
    """
    h = pd.Series(hist_ids).dropna().astype("int64")
    m = pd.Series(modern_ids).dropna().astype("int64")
    bad_h = h[(h >= MODERN_ID_FLOOR) | (h <= 0)]
    if not bad_h.empty:
        raise AssertionError(
            f"{len(bad_h)} HIST id(s) out of the positive charter range "
            f"(0 < id < {MODERN_ID_FLOOR}); e.g. {bad_h.head().tolist()} — a HIST id "
            f"reaching modern scale would collide with modern entities"
        )
    bad_m = m[m.abs() < MODERN_ID_FLOOR]
    if not bad_m.empty:
        raise AssertionError(
            f"{len(bad_m)} MODERN id(s) below modern floor (|id| < {MODERN_ID_FLOOR}); "
            f"e.g. {bad_m.head().tolist()} — the 05 L77 *1e5 scaling was not applied"
        )
    overlap = set(h.tolist()) & set(m.tolist())
    if overlap:
        raise AssertionError(
            f"HIST/MODERN entity-id ranges overlap ({len(overlap)} ids), e.g. "
            f"{sorted(overlap)[:5]} — append-not-join would silently link distinct entities"
        )
