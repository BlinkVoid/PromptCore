#!/usr/bin/env python3
"""Run the full PromptCore benchmark suite and emit a combined summary.

Usage:
    uv run python scripts/run_pipeline.py --label baseline
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
BENCHES = [
    "benchmarks/bench_selection_accuracy.py",
    "benchmarks/bench_complexity_calibration.py",
    "benchmarks/bench_latency.py",
    "benchmarks/bench_framework_coverage.py",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="Name for this run (e.g. baseline)")
    args = parser.parse_args()

    results = {"label": args.label, "timestamp": datetime.now().isoformat(), "benchmarks": {}}
    failed = False
    for bench in BENCHES:
        print(f"\n=== Running {bench} ===")
        proc = subprocess.run([sys.executable, str(ROOT / bench)], cwd=ROOT)
        if proc.returncode != 0:
            failed = True
        result_file = Path(bench).stem.replace("bench_", "")
        path = ROOT / "benchmarks" / "results" / f"{result_file}.json"
        if path.exists():
            data = json.loads(path.read_text())
            results["benchmarks"][result_file] = data.get("summary", data)
        else:
            results["benchmarks"][result_file] = "NO OUTPUT"

    out = ROOT / "benchmarks" / "results" / f"pipeline_{args.label}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nCombined summary written to {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
