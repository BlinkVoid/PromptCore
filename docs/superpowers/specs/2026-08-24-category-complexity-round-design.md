# Design: Category Detection & Complexity Calibration Round

**Date:** 2026-08-24
**Status:** Draft
**Baseline:** exact 30.00%, top-3 47.73%, category 63.64%; Pearson r 0.417, MAE 3.91 (frozen 220-task set)

## Problem

PromptCore's framework selection still struggles because the upstream signals are weak:

1. **Category detection** is only **63.64%** (target ≥80%, minimum ≥75%). Worst categories:
   - research 11.11%, planning 20.00%, logic 27.59%, data 37.04%.
   - Many tasks are misclassified as `general` or `creative` because keywords are too broad ("write" matches CREATIVE even for code-tasks like "Write a Python function...") and `general` is the default fallback.
2. **Complexity calibration** is weak: Pearson r 0.417, MAE 3.91 (target Pearson ≥0.5, MAE ≤2.5). Errors are largest in the medium (MAE 3.45) and high (MAE 6.50) bands.
3. **Compounding effect:** a wrong category sends the task to the wrong tier, and a wrong complexity picks the wrong level inside that tier. This is why exact-match is stuck at 30% despite acceptable-set matching.

## Goals

- Raise category-detection accuracy to **≥75%** on the frozen 220-task benchmark.
- Raise complexity calibration to **Pearson r ≥0.5** and **MAE ≤2.5** on the 45-task calibration benchmark.
- Keep selection deterministic, LLM-free, no new runtime dependencies.

## Non-goals

- Framework utilization / dead-framework fixes — deferred to the next round.
- Adding more frameworks — out of scope.
- LLM-in-the-loop selection or training — violates PromptCore's identity.

## Section 1 — Category detection retune

Current `_detect_category` does simple keyword counting with equal weights and falls back to GENERAL when no keyword matches. Improvements:

1. **Remove broad bleed keywords:** e.g., "write" should not dominate CODE/CREATIVE when the task clearly asks for code; add stopwords/negative signals.
2. **Weighted keyword scoring:** rare domain words ("derivative", "syllogism", "csv", "milestones") should count more than generic verbs ("explain", "analyze").
3. **Negative signals / disambiguation:**
   - "write a function" → CODE, not CREATIVE.
   - "analyze this data" → DATA, not RESEARCH.
   - "explain how X works" → GENERAL unless stronger domain words present.
4. **Soft fallback:** instead of GENERAL for zero-score, use task-length and keyword-strength heuristics to choose a least-bad category.
5. **Regression tests:** add failing tests for the worst categories (research, planning, logic, data) before fixing, pass after.

## Section 2 — Complexity calibration retune

Current `_calculate_complexity` uses hand-tuned constants. Improvements:

1. **Feature audit:** keep features (word count, sentence length, question count, booster/reducer keyword matches) but express them as a linear model with learnable weights.
2. **Calibrate against labeled data:** use the 45 tasks in `bench_complexity_calibration.py` (human-rated complexity) to fit weights via least-squares or simple grid search — no external ML library required.
3. **Band-specific correction:** the model currently underestimates hard tasks and overestimates medium tasks; add a post-hoc band correction or non-linear mapping.
4. **Validation:** after retune, run `bench_complexity_calibration.py` and confirm Pearson ≥0.5 and MAE ≤2.5.

## Section 3 — Error-analysis loop (same pipeline as Round 1)

1. Run `scripts/run_pipeline.py --label cat-complex-baseline`.
2. Generate confusion matrix + per-category breakdown.
3. Apply one targeted fix per iteration (category keyword, complexity weight, or band correction).
4. Re-benchmark; compare; log in `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md`.
5. Stop when two consecutive iterations fail to gain ≥2 pp category accuracy or ≥0.05 Pearson.

## Section 4 — Testing & documentation

- Unit tests for category detection (worst categories) and complexity calibration (Pearson/MAE targets).
- Update pipeline changelog with before/after rows.
- Update README/ARCHITECTURE only if counts change (they shouldn't).

## Risks / mitigations

- **Overfitting to benchmark:** use hold-out discipline; new tasks can be added only before tuning begins, and only heuristic constants are tuned, not per-task rules.
- **Calibrated complexity may not improve selection:** track selection accuracy too; if it degrades, complexity is not the binding constraint.

## Approaches

- **A — Deterministic retune (recommended):** hand-tune keyword lists and recalibrate complexity constants. Preserves zero-dep identity, fully explainable.
- **B — Lightweight learned models:** add scikit-learn TF-IDF/logistic-regression for category and linear regression for complexity. Higher ceiling but new dependency and risk of overfitting; only if A misses targets.

**Decision:** Approach A for this round. Approach B reserved as fallback if category <70% or Pearson <0.45 after A.
