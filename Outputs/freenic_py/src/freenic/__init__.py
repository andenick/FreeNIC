"""freenic: Python interface to the freenic US banking regulatory database.

1.5 billion rows spanning 1863-2026, covering 217,210 institutions from
20 data sources including FFIEC, FDIC, Federal Reserve, and more.

Quick start:
    >>> import freenic
    >>> freenic.set_data_dir("/path/to/parquet")
    >>> freenic.list_tables()
    >>> freenic.lookup_institution("jpmorgan")
    >>> freenic.get_financials(1039502, "BHCK2170")
"""

__version__ = "0.1.0"

from freenic._core import close, describe, list_tables, query, set_data_dir
from freenic.accessors import (
    get_failures,
    get_financials,
    get_hierarchy,
    lookup_column_id,
    lookup_institution,
    lookup_rssd,
    search_variables,
    show_regulatory_groups,
    show_source_descriptions,
    verify_mdrm_codes,
    verify_rssds,
)

__all__ = [
    "set_data_dir",
    "query",
    "list_tables",
    "describe",
    "close",
    "lookup_institution",
    "lookup_rssd",
    "lookup_column_id",
    "get_financials",
    "search_variables",
    "get_hierarchy",
    "get_failures",
    "show_source_descriptions",
    "show_regulatory_groups",
    "verify_mdrm_codes",
    "verify_rssds",
]
