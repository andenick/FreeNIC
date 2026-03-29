"""Phase 12: Export all tables to Parquet with ZSTD compression.

Outputs to Outputs/parquet/{table}.parquet for language-agnostic access.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_db, log_ingestion, timer, OUTPUTS_DIR


def main():
    elapsed = timer()
    print("=== Phase 12: Export Parquet ===")

    parquet_dir = OUTPUTS_DIR / "parquet"
    parquet_dir.mkdir(exist_ok=True)

    con = get_db(read_only=True)

    # Tables to export (schema, table_name)
    tables = [
        ('main', 'mdrm'),
        ('main', 'reporting_forms'),
        ('main', 'institutions'),
        ('main', 'institution_attributes'),
        ('main', 'branches'),
        ('main', 'relationships'),
        ('main', 'transformations'),
        ('main', 'crsp_mapping'),
        ('main', 'bhcf_filings'),
        ('main', 'call_report_filings'),
        ('main', 'luck_call_reports'),
        ('main', 'occ_historical'),
        ('main', 'filing_metadata'),
        ('main', 'bank_failures'),
        ('main', 'fdic_financials'),
        ('main', 'fdic_sod'),
        ('main', 'dfast_results'),
        ('main', 'pillar3_disclosures'),
        ('main', 'variable_crosswalk'),
        ('main', 'fdic_history'),
        ('main', 'fred_series'),
        ('main', 'robin_panel'),
        ('main', 'robin_deposits_historical'),
        ('main', 'robin_deposits_modern'),
        ('main', 'robin_crosswalk'),
        ('main', 'bhc_ownership'),
        ('main', 'sector_groupings'),
        ('main', 'stress_scenarios_domestic'),
        ('main', 'stress_scenarios_international'),
        ('catalog', 'variables'),
        ('catalog', 'filing_coverage'),
        ('catalog', 'entity_coverage'),
        ('catalog', 'schema_evolution'),
        ('catalog', 'data_sources'),
    ]

    # Sort keys for sorted Parquet export (B1.2 quick win: ~10x faster selective queries)
    SORT_KEYS = {
        'bhcf_filings': 'rssd_id, period_end',
        'call_report_filings': 'rssd_id, period_end',
        'luck_call_reports': 'entity_id, period_end',
        'fdic_financials': 'rssd_id, period_end',
        'fdic_sod': 'fdic_cert, year',
        'occ_historical': 'bank_id, report_date',
        'dfast_results': 'rssd_id, year',
        'pillar3_disclosures': 'rssd_id, period_end',
        'institutions': 'rssd_id',
        'relationships': 'rssd_parent, rssd_offspring',
        'transformations': 'rssd_successor, dt_trans',
        'bank_failures': 'closing_date',
        'crsp_mapping': 'rssd_id, dt_start',
        'robin_panel': 'bank_id, year',
        'robin_crosswalk': 'bank_id_robin',
        'bhc_ownership': 'rssd_id_bhc, rssd_id_bank',
    }

    total_size = 0
    for schema, table in tables:
        qualified = f"{schema}.{table}" if schema != 'main' else table
        out_name = f"catalog_{table}" if schema == 'catalog' else table
        out_path = parquet_dir / f"{out_name}.parquet"
        out_str = str(out_path).replace('\\', '/')

        try:
            count = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
            if count == 0:
                print(f"  {qualified}: empty, skipping")
                continue

            sort_key = SORT_KEYS.get(table, '')
            order_clause = f" ORDER BY {sort_key}" if sort_key else ""
            con.execute(f"""
                COPY (SELECT * FROM {qualified}{order_clause}) TO '{out_str}'
                (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 122880)
            """)

            size_mb = out_path.stat().st_size / (1024 ** 2)
            total_size += size_mb
            print(f"  {qualified:<30} {count:>15,} rows -> {size_mb:>8.1f} MB")

        except Exception as e:
            print(f"  {qualified}: ERROR - {e}")

    con.close()

    total_gb = total_size / 1024
    print(f"\n  Total Parquet: {total_size:,.1f} MB ({total_gb:.2f} GB)")
    print(f"  Output: {parquet_dir}")

    secs = elapsed()
    log_ingestion("12", f"Parquet export: {len(tables)} tables, {total_size:,.1f} MB total. {secs:.1f}s")
    print(f"\nPhase 12 complete in {secs:.1f}s ({secs/60:.1f} minutes).")


if __name__ == "__main__":
    main()
