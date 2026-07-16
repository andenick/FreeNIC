#!/usr/bin/env python3
"""serve_freenic.py — one-command self-host for the FreeNIC parquet data (see SELF_HOSTING.md).

Serves Outputs/parquet/ (+ PROVENANCE.csv, DATA_LICENSE.md, SHA256SUMS.txt) read-only over HTTP with
byte-range support, so clients can query directly with DuckDB httpfs without downloading whole files:

    # on the mini PC:
    python serve_freenic.py --port 8080            # serves http://<host>:8080/parquet/<table>.parquet

    # on a client:
    import duckdb; con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs;")
    BASE = "http://minipc.local:8080/parquet"
    con.execute(f"SELECT COUNT(*) FROM read_parquet('{BASE}/institutions.parquet')").fetchone()

    # or point the package at it once the optional remote reader is enabled:
    import freenic; freenic.set_data_dir("http://minipc.local:8080/parquet")

Read-only: this server only GETs/HEADs; it never writes. Range requests are enabled (RangeHTTP
handler) so DuckDB fetches only the row groups it needs. Run behind nginx/a tunnel for WAN.
"""
import argparse
import functools
import http.server
import os
import socketserver
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "Outputs"


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with HTTP Range support (Python 3.11+ has partial; this is explicit)
    so DuckDB httpfs can fetch byte ranges of large parquet files."""

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng or not rng.startswith("bytes="):
            return super().send_head()
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        try:
            start_s, end_s = rng[len("bytes="):].split("-", 1)
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else size - 1
        except ValueError:
            return super().send_head()
        start = max(0, start); end = min(end, size - 1)
        length = end - start + 1
        f = open(path, "rb"); f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        self._range_remaining = length
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "_range_remaining", None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk); remaining -= len(chunk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--bind", default="0.0.0.0")
    ap.add_argument("--root", default=str(ROOT), help="dir to serve (default: Outputs/)")
    args = ap.parse_args()
    handler = functools.partial(RangeHandler, directory=args.root)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((args.bind, args.port), handler) as httpd:
        print(f"FreeNIC self-host serving {args.root} at http://{args.bind}:{args.port}/  (Ctrl-C to stop)")
        print(f"  parquet -> http://<host>:{args.port}/parquet/<table>.parquet")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
