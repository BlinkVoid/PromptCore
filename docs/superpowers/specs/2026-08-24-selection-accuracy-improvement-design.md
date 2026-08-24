# Design: Selection Accuracy Improvement Round

**Date:** 2026-08-24
**Status:** Approved (Approach A — deterministic retune)
**Baseline:** Exact match 19%, top-3 match 35%, category detection 67% (`benchmarks/results/selection_accuracy.json`, 100 tasks)

## Problem

PromptCore's heuristic framework selection matches expert ground truth only ~19% of the time.
Root causes identified:

1. **Broken benchmark labels.** Five expert framework names in `bench_selection_accuracy.py`
   do not exist in `FRAMEWORK_REGISTRY` (`self_refinement`, `analogical_reasoning`,
   `contrastive`, `reverse`, `zero_shot`), making ~15/100 tasks unwinnable by definition.
2. **Selector scoring quirks.** Intent bonus stacks (+4 per matching intent), the overkill
   penalty is capped at 1.5 while threshold-miss penalty is flat −2.0, and a simplicity
   tie-breaker biases toward low-threshold frameworks. Result: generic frameworks
   (`rephrase_and_respond`, `system2_attention`) dominate selections across all categories.
3. **Coarse category handling.** Framework plausibility is not constrained per
   category×complexity band; RESEARCH tasks scored 0% exact match.
4. **Stale catalog.** Catalog covers pre-2024 literature; newer well-cited techniques are absent.

## Goals

- Best-effort maximization of selection accuracy this round (no hard threshold).
- Expand the framework catalog with researched, cited additions.
- Document the improvement pipeline so future rounds are streamlined.

## Non-goals

- Outcome-based evaluation (LLM-in-the-loop task success testing) — deferred.
- Learned/retrieval-based selection (hybrid TF-IDF/embedding layer) — candidate follow-up if
  heuristics plateau below ~50% exact match.

## Section 1 — Benchmark repair

1. **Label alignment:** rename invalid expert labels to registry names:
   - `self_refinement → self_refine`
   - `analogical_reasoning → analogical`
   - `contrastive → contrastive_cot`
   - `reverse → reverse_cot`
   - `zero_shot` tasks (trivial factual recall) get acceptable sets such as
     `["role_prompting", "rephrase_and_respond", "prompt_paraphrasing"]`.
2. **Acceptable sets:** every task carries `expert_framework` plus an
   `acceptable_frameworks` list (equivalent expert-endorsed choices). Exact-match metric =
   predicted ∈ acceptable set. Top-3 metric unchanged.
3. **Expansion:** grow test set to ~200 tasks (~25 × 8 categories), stratified across
   complexity bands (low/mid/high), same style as existing entries.
4. Complexity calibration benchmark unchanged.

## Section 2 — Selector improvements (error-analysis driven)

Each change is made only when the confusion matrix justifies it:

1. Cap total intent bonus (e.g., max +4 aggregate instead of +4 per intent).
2. Rebalance overkill vs threshold penalties so low-threshold frameworks stop winning ties;
   remove or reduce the `(10 − threshold) × 0.01` tie-breaker.
3. Introduce a category×complexity preference matrix constraining plausible frameworks per
   band (e.g., DATA+mid → chain_of_table; RESEARCH+high → step_back/self_ask tier).
   Implausible frameworks are filtered or heavily penalized.
4. Recalibrate complexity scoring (base +2.0, length normalization) against
   `bench_complexity_calibration` targets (Pearson r ≥ 0.5, MAE ≤ 2.0).

## Section 3 — New frameworks

1. Research scan of well-cited post-2023 prompting techniques (candidate pool likely
   includes Self-Discover, Chain-of-Abstraction, PlanSearch, Medprompt-style k-NN CoT,
   Chain-of-Code; final list from scan).
2. Shortlist ~8–12 with paper citations and task-fit metadata; **user approval required
   before implementation**.
3. Implement approved frameworks in `src/promptcore/domain/frameworks/` following the
   existing class pattern (name, best_for categories, capabilities, complexity_threshold,
   template). Add matching coverage in the expanded benchmark task list.

## Section 4 — Pipeline documentation

- New `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md` describing the repeatable loop:
  1. Run baseline benchmarks (all four).
  2. Generate error report (confusion matrix, category breakdown, label audit).
  3. Apply one targeted fix at a time.
  4. Re-benchmark; compare against previous run.
  5. Record decision + measured result in the doc's changelog table; repeat until gains flatten.
- New `scripts/run_pipeline.py`: runs all benchmarks, emits combined summary
  (before/after comparison) — one command per future round.

## Section 5 — Testing & verification

- Unit tests for selector changes and each new framework, following existing patterns in `tests/`.
- Full benchmark suite run before/after with a comparison table recorded in the pipeline doc.
- Existing 22 tests remain green.

## Risks / mitigations

- *Ground-truth subjectivity:* acceptable sets reduce false negatives from equally-valid picks.
- *Overfitting selector to benchmark:* hold-out discipline — new benchmark tasks are written
  before selector tuning begins and never used as tuning feedback beyond aggregate metrics.
- *Catalog bloat:* every new framework requires citation + distinct task-fit rationale.

## Decision record

- Approach A (deterministic retune) chosen over hybrid retrieval (B) and outcome-based eval (C):
  preserves sub-millisecond deterministic identity, fully explainable picks, no new deps.
  B revisited if exact match plateaus < 50%; C deferred as separate effort.
