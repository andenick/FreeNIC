# freenic Best Practices Research

*Compiled: 2026-03-24*

## Priority Summary

| # | Finding | Rating | Impact |
|---|---------|--------|--------|
| B1.2 | Sorted Parquet exports (ORDER BY rssd_id, period_end) | **Quick Win** | ~10x for selective queries |
| B1.4 | Memory configuration (SET memory_limit, threads) | **Quick Win** | Prevents OOM, optimizes parallelism |
| B3.1 | Persistent read-only connection in MCP server | **Quick Win** | Eliminates per-call open overhead |
| B1.1 | ROW_GROUP_SIZE to 122,880-200,000 | **Quick Win** | Better parallelism and pruning |
| B2.1 | Explicit ZSTD level 3 | **Quick Win** | Confirm optimal compression |
| B1.3 | No ART indexes (rely on zone maps) | **Quick Win** | Avoid unnecessary overhead |
| B3.2 | Schema discovery MCP tool | Medium Effort | Dramatically better LLM queries |
| B3.3 | Query timeout (30s default) | Medium Effort | Server stability protection |
| B3.4 | Result size limits + pagination | Medium Effort | Prevent memory blowouts |
| B1.5 | Year-based Hive partitioning for large tables | Medium Effort | File-level pruning for time queries |
| B4.1 | WRDS-style entity mapping table | Future | Better data modeling |
| B4.2 | OpenBB-style standardized response schemas | Future | Cleaner MCP tool outputs |
| B4.3 | FRED v2 bulk API for macro data | Future | Enrich with economic context |

---

## B1. DuckDB Performance for Billion-Row Databases

### B1.1 ROW_GROUP_SIZE

**Current**: 100,000. **DuckDB default**: 122,880.

DuckDB parallelizes at the row group level — needs `threads × row_group_size` rows for full utilization. Sweet spot: **100K-1M rows**. Too small = metadata overhead; too large = zone map statistics get washed out.

**Recommendation**: Increase to **122,880** (default) or **200,000**. For `call_report_filings` (896M rows), consider up to 500K.

### B1.2 Sorted Parquet Exports

**Key finding**: Sorting before export can speed selective queries by **~10x**. DuckDB creates zone maps (min/max per row group per column) automatically. Sorted data = tight min/max ranges = effective row group skipping. Unsorted data = overlapping ranges = no pruning.

**Recommendation**: Add `ORDER BY rssd_id, period_end` to all COPY statements:
```sql
COPY (SELECT * FROM table ORDER BY rssd_id, period_end)
TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

### B1.3 Indexing

ART indexes only help selective point lookups (equality, IN). They **do not help** joins, aggregations, or sorting. Focus on sorted exports instead (makes zone maps effective).

**Recommendation**: Do NOT add indexes. Invest in sorted Parquet exports.

### B1.4 Memory Configuration

Rule of thumb: 1-2 GB per thread for aggregation, 3-4 GB per thread for joins. DuckDB spills to disk automatically.

```sql
SET memory_limit = '8GB';
SET threads = 4;
```

### B1.5 Partitioned Parquet

Hive-style partitioning enables file-level pruning (queries drop from 1.8s to 35ms when partition filter matches). But adds filesystem overhead.

**Recommendation**: Only for `call_report_filings` (2.4 GB) — partition by year. Smaller tables stay monolithic.

---

## B2. Parquet Distribution

### B2.1 ZSTD Compression

ZSTD level 3 (DuckDB default) is the sweet spot. ~82% faster than GZIP with similar ratios. Level 5 for distribution if download size matters.

### B2.2 Row Group Sizing

Industry consensus: 100K-1M rows, physically 64-256 MB uncompressed per row group. Audit with:
```sql
SELECT row_group_id, row_group_num_rows, row_group_bytes_total_compressed
FROM parquet_metadata('file.parquet');
```

---

## B3. MCP Server Patterns

### B3.1 Connection Lifecycle

DuckDB connections are lightweight. MotherDuck MCP server uses a single persistent connection. Read-only mode allows concurrent readers.

**Recommendation**: Single persistent read-only connection at server startup, not open/close per call.

### B3.2 Schema Discovery Tool

Add `describe_database` tool returning table names, columns, types, and row counts. Dramatically improves LLM query accuracy.

### B3.3 Query Timeout

MCP protocol has 60s request timeout. Implement 30s default via `threading.Timer` (Windows) + `conn.interrupt()`.

### B3.4 Result Limits

MotherDuck defaults: 1,024 rows / 50,000 chars. Implement hard cap + `total_count` from separate COUNT(*).

---

## B4. Reference Architectures

### WRDS
- Schemas as namespaces (bank_regulatory, crsp, compustat)
- RSSD ID as primary institution key with linking tables
- Temporal modeling: `_row` (static), `_arr` (events), `_ts` (time series)

### OpenBB
- Standardized Pydantic models for consistent interfaces
- Router hierarchy by asset class
- Provider abstraction: each source implements standard interface

### FRED
- v2 bulk API (Nov 2025) supports full release downloads
- Revision-aware vintage dates for point-in-time analysis
- Cache locally in Parquet for join performance

---

*Sources: DuckDB docs (tuning, indexing, memory, file formats, Hive partitioning), MotherDuck MCP server, MCP specification, WRDS documentation, OpenBB architecture blog, FRED API v2*
