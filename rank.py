#!/usr/bin/env python3
"""
Rank candidates against the Redrob Senior AI Engineer JD.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv
"""
import argparse
import csv
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob Senior AI Engineer JD")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Output CSV path (e.g. submission.csv)")
    parser.add_argument("--top-n", type=int, default=100, help="Number of top candidates to output (default: 100)")
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    if not candidates_path.exists():
        print(f"ERROR: candidates file not found: {candidates_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading ranking engine...")
    from src.engine import rank_candidates

    print(f"Ranking candidates from {candidates_path} ...")
    t0 = time.time()
    results = rank_candidates(str(candidates_path), top_n=args.top_n)
    elapsed = time.time() - t0
    print(f"Ranked top {len(results)} of all candidates in {elapsed:.1f}s")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved: {out_path}")

    # Also save xlsx if openpyxl is available
    xlsx_path = out_path.with_suffix(".xlsx")
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Rankings"
        ws.append(["candidate_id", "rank", "score", "reasoning"])
        for r in results:
            ws.append([r["candidate_id"], r["rank"], r["score"], r["reasoning"]])
        wb.save(xlsx_path)
        print(f"Also saved: {xlsx_path}")
    except ImportError:
        pass  # xlsx is optional


if __name__ == "__main__":
    main()
