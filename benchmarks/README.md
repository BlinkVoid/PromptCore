# PromptCore Benchmarks

This directory contains benchmarking scripts to evaluate PromptCore's performance, accuracy, and coverage.

## Quick Start

Run all benchmarks:

```bash
# Run all benchmarks with default settings
uv run python benchmarks/bench_selection_accuracy.py
uv run python benchmarks/bench_complexity_calibration.py
uv run python benchmarks/bench_latency.py
uv run python benchmarks/bench_framework_coverage.py
```

Results are saved to `benchmarks/results/` in both JSON and Markdown formats.

## Benchmarks

### 1. Selection Accuracy (`bench_selection_accuracy.py`)

Measures how well PromptCore's automatic framework selection matches expert-selected "ground truth" frameworks.

**What it tests:**
- Exact match rate (PromptCore choice == expert choice)
- Top-3 match rate (expert choice in top 3 recommendations)
- Category detection accuracy (code/math/logic/etc.)

**Usage:**
```bash
# Default: 100 test tasks
uv run python benchmarks/bench_selection_accuracy.py

# Custom output path
uv run python benchmarks/bench_selection_accuracy.py --output my_results.json --markdown my_report.md
```

**Target metrics:**
- Exact match rate: ≥50% (acceptable), ≥70% (good)
- Top-3 match rate: ≥70%
- Category detection: ≥80%

---

### 2. Complexity Calibration (`bench_complexity_calibration.py`)

Evaluates the correlation between PromptCore's automated complexity scores and human-rated complexity judgments.

**What it tests:**
- Pearson correlation (linear relationship)
- Spearman correlation (rank-order relationship)
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)

**Usage:**
```bash
# Default: 50 test tasks with known complexity
uv run python benchmarks/bench_complexity_calibration.py
```

**Target metrics:**
- Pearson r: ≥0.5 (acceptable), ≥0.7 (strong)
- Spearman ρ: ≥0.5
- MAE: ≤2.0 points (on 0-10 scale)

---

### 3. Latency (`bench_latency.py`)

Measures the execution time of PromptCore operations to ensure negligible overhead.

**What it tests:**
- `FrameworkSelector.analyze()` latency
- `PromptBuilder.build_with_analysis()` latency
- Full pipeline (analyze + build) latency
- Framework registry lookup latency

**Usage:**
```bash
# Default: 1000 iterations per test
uv run python benchmarks/bench_latency.py

# More iterations for stable results
uv run python benchmarks/bench_latency.py --iterations 5000
```

**Target metrics:**
- p50 latency: <5ms
- Overhead vs LLM API: <1% (excellent), <5% (acceptable)

---

### 4. Framework Coverage (`bench_framework_coverage.py`)

Analyzes framework utilization across diverse tasks to identify "dead" frameworks.

**What it tests:**
- Which frameworks are selected most/least often
- Framework distribution by category
- Unused ("dead") framework identification
- Selection diversity

**Usage:**
```bash
# Default: 500 generated tasks
uv run python benchmarks/bench_framework_coverage.py

# More tasks for better coverage analysis
uv run python benchmarks/bench_framework_coverage.py --tasks 1000
```

**Target metrics:**
- Framework utilization: ≥80% of available frameworks
- No more than 5 "dead" frameworks
- Reasonable distribution (no framework >30% of selections)

---

## Output Format

Each benchmark produces two output files:

1. **JSON** (`results/*.json`): Machine-readable raw data
   - Complete results for each test case
   - Summary statistics
   - Detailed metrics

2. **Markdown** (`results/*.md`): Human-readable report
   - Executive summary
   - Key findings
   - Comparison to targets
   - Recommendations

## Interpreting Results

### Selection Accuracy

```
Exact Match Rate: 65%
→ Good agreement with expert selection

Top-3 Match Rate: 85%
→ Expert's choice is almost always in recommendations
```

### Complexity Calibration

```
Pearson r: 0.72
→ Strong linear correlation between human and machine ratings

MAE: 1.4 points
→ On average, complexity estimate is 1.4 points off (on 0-10 scale)
```

### Latency

```
Full pipeline p50: 1.8ms
Overhead vs LLM API: 0.36%
→ Negligible overhead, suitable for production
```

### Framework Coverage

```
Frameworks used: 35/40 (87.5%)
Dead frameworks: 2
→ Good coverage, minor tuning needed for unused frameworks
```

## Continuous Benchmarking

For CI/CD integration, benchmarks return exit codes:
- `0`: All targets met
- `1`: Some targets not met (see report for details)

Example CI workflow:

```yaml
- name: Run PromptCore benchmarks
  run: |
    uv run python benchmarks/bench_selection_accuracy.py
    uv run python benchmarks/bench_latency.py
    
- name: Check results
  run: |
    # Fail CI if exact match rate < 50%
    python -c "import json; r=json.load(open('benchmarks/results/selection_accuracy.json')); exit(0 if r['summary']['exact_match_rate'] >= 0.5 else 1)"
```

## Customizing Benchmarks

### Adding Test Cases

Edit the test case lists in each benchmark script:

- `bench_selection_accuracy.py`: `TEST_TASKS` list
- `bench_complexity_calibration.py`: `COMPLEXITY_TEST_TASKS` list
- `bench_latency.py`: `SAMPLE_TASKS` list
- `bench_framework_coverage.py`: `TASK_TEMPLATES` and `FILL_VALUES`

### Adjusting Targets

Modify the target thresholds in the markdown report generators within each script.

## Troubleshooting

### Import errors

Ensure you're running from the project root:
```bash
cd /path/to/promptcore
uv run python benchmarks/bench_selection_accuracy.py
```

### Module not found

Install dependencies:
```bash
uv sync
```

### Permission errors

Ensure the `benchmarks/results/` directory is writable:
```bash
mkdir -p benchmarks/results
chmod 755 benchmarks/results
```

## Contributing

When adding new benchmarks:

1. Follow the existing script structure
2. Use Python `logging` instead of `print`
3. Support `--output` and `--markdown` CLI arguments
4. Generate both JSON and Markdown reports
5. Include target metrics and interpretation guidance
6. Add to this README

## References

Benchmark methodology based on the [COMPARISON.md](../docs/COMPARISON.md) benchmark plan.
