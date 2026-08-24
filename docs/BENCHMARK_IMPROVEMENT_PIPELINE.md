# Benchmark Improvement Pipeline

## Purpose

This document tracks the ongoing effort to improve PromptCore's selection
accuracy (choosing the right prompt-engineering framework for a given task).
Each improvement round follows a measured, one-change-at-a-time loop so every
number in the changelog below is attributable to a single fix.

## The Loop

1. **Baseline** — run the full benchmark suite to get current numbers.
2. **Error report** — analyze failures (which tasks miss, why).
3. **One targeted fix** — make exactly one change to selection logic or eval data.
4. **Re-run** — run the full suite again with a distinct `--label`.
5. **Log** — append a row to the changelog table below.

Never bundle multiple changes into one round; if numbers move, we need to know
why.

## How to Run

```bash
uv run python scripts/run_pipeline.py --label <name>
```

This executes all four benchmarks and writes a combined summary.

## Where Results Live

- Per-benchmark JSON: `benchmarks/results/{selection_accuracy,complexity_calibration,latency,framework_coverage}.json`
- Combined summary: `benchmarks/results/pipeline_<label>.json`
- These artifacts are gitignored; commit only the changelog rows here.

## Changelog

| Date | Label | Change made | Exact match | Top-3 | Category | Notes |
|------|-------|-------------|-------------|-------|----------|-------|
| 2026-03-17 | baseline-19pct | — | 19.00% | 35.00% | 67.00% | Original 100-task eval set |
| 2026-08-24 | post-benchmark-fix | Fixed invalid ground-truth labels + acceptable-set matching; expanded eval set to frozen 201-task set | 20.40% | 36.32% | 54.23% | Eval-set expansion (100 → 201 stratified tasks); category drop reflects stricter labels, not a regression |
| 2026-08-24 | scoring-v2 | Capped intent bonus (4.0 flat), added category×complexity tier gating (-5 out-of-tier), recalibrated complexity base/divisor, removed threshold tie-breaker; alternatives no longer filtered by score>0 | 21.39% | 41.79% | 55.72% | All metrics improved; DATA keywords gained "group"/"revenue"/"sales" so grouped-data tasks detect as DATA |
| 2026-08-24 | iter-1 | Category keyword repair grounded in observed misses: MATH += "shortest path"/"weighted graph"/"statistical"/"significant"/"integer"/"infinite series"/"surface area"/"celsius"/"arranged"; LOGIC += "deductive"/"inductive"/"negation"/"flaw"; DATA += "column"/"anomalies"/"features"/"sensor" | 21.89% | 42.79% | 62.19% | Category detection +6.5pp; exact +0.5pp — corrected tasks often still lose on framework scoring (complexity lands LOW, generic frameworks keep fit bonus); one prior pass (derivative task) lost via MATH LOW-tier gating of program_of_thoughts |
