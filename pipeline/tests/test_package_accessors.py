"""Package-layer tests (Step 10, added 2026-06-07): exercise the freenic_py read layer
(accessors) against the warehouse parquet — the layer users actually call, previously untested.

Probe verified all 13 accessors functional (coverage_analysis/step10_probe.py). These assert sane
results for known inputs. Run locally / wherever the parquet is present (the CI smoke job covers the
no-data import checks). FOLLOW-UP: the package table-map predates ncua/edgar/hmda — add accessors
for the new tables; and silence the verify_* pd.concat FutureWarning.
"""
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).parent.parent.parent.parent / "Outputs" / "freenic_py" / "src"
sys.path.insert(0, str(_SRC))

freenic = pytest.importorskip("freenic")
JPM = 1039502  # JPMorgan Chase & Co. (HC rssd)


@pytest.fixture(scope="module", autouse=True)
def _data_dir(parquet_dir):
    freenic.set_data_dir(str(parquet_dir))
    yield
    try:
        freenic.close()
    except Exception:
        pass


def test_list_tables():
    assert len(freenic.list_tables()) >= 30


def test_query_institutions_count():
    n = freenic.query("SELECT COUNT(*) AS n FROM institutions")["n"].iloc[0]
    assert n > 200_000


def test_lookup_institution_name():
    df = freenic.lookup_institution("jpmorgan")
    assert len(df) >= 1 and "rssd_id" in df.columns


def test_lookup_rssd_exact():
    df = freenic.lookup_rssd(rssd_id=JPM)
    assert len(df) == 1
    assert "JPMORGAN" in str(df["name_legal"].iloc[0]).upper()


def test_get_financials_bhcf():
    df = freenic.get_financials(JPM, "BHCK2170", source="bhcf")
    assert len(df) >= 1 and "value" in df.columns


def test_get_hierarchy_down():
    df = freenic.get_hierarchy(JPM, direction="down")
    assert len(df) >= 1  # JPM has many subsidiaries


def test_get_failures_gfc():
    df = freenic.get_failures(start_year=2008, end_year=2010)
    assert len(df) >= 1 and "closing_date" in df.columns


def test_verify_rssds_found_and_missing():
    df = freenic.verify_rssds(JPM, 9999999)
    found = dict(zip(df["rssd_id"], df["found"]))
    assert found.get(JPM) == True and found.get(9999999) == False


def test_verify_mdrm_found_and_missing():
    df = freenic.verify_mdrm_codes("RCFD2170", "FAKE9999")
    byid = dict(zip(df["variable_id"], df["found"]))
    assert byid.get("RCFD2170") == True and byid.get("FAKE9999") == False
