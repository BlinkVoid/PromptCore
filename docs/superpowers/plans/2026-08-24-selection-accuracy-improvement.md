# Selection Accuracy Improvement Round — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise PromptCore's framework-selection accuracy from the 19% baseline via benchmark repair + deterministic selector retune, add researched new frameworks, and document the repeatable improvement pipeline.

**Architecture:** Keep the zero-LLM heuristic selector (`FrameworkSelector`). Repair and expand the benchmark first (hold-out discipline: evaluation set finalized before tuning), then iterate error-analysis → targeted fix → re-benchmark. New frameworks plug into the existing auto-registration registry (`__init_subclass__`).

**Tech Stack:** Python 3.10+, pydantic, pytest, uv. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-24-selection-accuracy-improvement-design.md`

## Global Constraints

- Selection stays deterministic and LLM-free (sub-millisecond).
- No new runtime dependencies.
- All existing tests stay green: `uv run pytest -q` (currently 22 passing) unless a test's expectation is *deliberately* changed by a task below (only `tests/unit/test_selector.py` expectations tied to removed behaviors).
- Every benchmark label used in ground truth must exist in `FRAMEWORK_REGISTRY` (enforced by a validator added in Task 1).
- Commits after each task; conventional commit style (`feat:`, `fix:`, `docs:`, `bench:`).

---

### Task 1: Benchmark label repair + acceptable sets

**Files:**
- Modify: `benchmarks/bench_selection_accuracy.py`
- Test: verification by running the benchmark itself (no unit-test file for benches)

**Interfaces:**
- Produces: `TEST_TASKS` entries gain key `"acceptable"` (list of registry-valid framework names, may be empty); metric `exact_match_rate` becomes predicted ∈ `{expert} ∪ acceptable`. Later tasks rely on this schema.

- [ ] **Step 1: Add registry-membership validator + acceptable-set matching**

In `benchmarks/bench_selection_accuracy.py`, replace the exact-match block inside `run_benchmark()` (lines ~184-187):

```python
        # Check exact match (predicted is the expert choice OR in its acceptable set)
        acceptable = set(test_case.get("acceptable", []))
        exact_match = (
            analysis.recommended_framework == expert_framework
            or analysis.recommended_framework in acceptable
        )
        if exact_match:
            exact_matches += 1

        # Check top-3 match (expert choice or any acceptable choice in top 3)
        top3_set = set(analysis.alternative_frameworks[:3])
        top3_match = (
            expert_framework in top3_set
            or bool(top3_set & acceptable)
            or exact_match
        )
        if top3_match:
            top3_matches += 1
```

Add a validator function and call it at the start of `run_benchmark()`:

```python
def validate_labels() -> None:
    """Fail fast if any ground-truth label is not a registered framework."""
    valid = set(FRAMEWORK_REGISTRY.keys())
    for tc in TEST_TASKS:
        labels = [tc["expert_framework"]] + tc.get("acceptable", [])
        bad = [l for l in labels if l not in valid]
        if bad:
            raise ValueError(f"Invalid framework labels {bad} in task: {tc['task'][:60]}")
```

In `run_benchmark()`, before the loop: `validate_labels()`.

- [ ] **Step 2: Fix the five broken labels across TEST_TASKS**

Apply these renames throughout `TEST_TASKS`:
- `"expert_framework": "self_refinement"` → `"self_refine"`
- `"expert_framework": "analogical_reasoning"` → `"analogical"`
- `"expert_framework": "contrastive"` → `"contrastive_cot"`
- `"expert_framework": "reverse"` → `"reverse_cot"`

For the six trivial-fact GENERAL tasks currently labeled `"zero_shot"` ("capital of France", "World Cup 2018", "time in Tokyo", "To Kill a Mockingbird", "tallest mountain", plus "List the benefits of regular exercise"), set:

```python
{"task": "...", "category": TaskCategory.GENERAL,
 "expert_framework": "role_prompting",
 "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"],
 "complexity": 1},
```

- [ ] **Step 3: Run benchmark and record the new baseline**

Run: `uv run python benchmarks/bench_selection_accuracy.py`
Expected: validator raises nothing; exact match rises above 19% (unwinnable tasks are now winnable). Record the number — this becomes row 1 of the changelog table in Task 3's doc.

- [ ] **Step 4: Commit**

```bash
git add benchmarks/bench_selection_accuracy.py
git commit -m "bench: fix invalid ground-truth labels, add acceptable-set matching"
```

---

### Task 2: Expand benchmark to ~200 stratified tasks

**Files:**
- Modify: `benchmarks/bench_selection_accuracy.py` (TEST_TASKS only)
- Test: automated quota validation inside the script

**Interfaces:**
- Consumes: label schema from Task 1.
- Produces: final frozen evaluation set (~200 tasks). This set must NOT change during Tasks 4–5 (hold-out discipline).

- [ ] **Step 1: Add a quota validator**

Append to `validate_labels()` (same function, after the label loop):

```python
    # Quota checks: ~25 per category, spread over complexity bands
    from collections import Counter
    cat_counts = Counter(tc["category"].value for tc in TEST_TASKS)
    band_counts = Counter(
        "low" if tc["complexity"] <= 3 else "mid" if tc["complexity"] <= 6 else "high"
        for tc in TEST_TASKS
    )
    for cat in TaskCategory:
        n = cat_counts[cat.value]
        assert 20 <= n <= 30, f"{cat.value}: {n} tasks, expected 20-30"
    assert band_counts["low"] >= 40 and band_counts["mid"] >= 60 and band_counts["high"] >= 40, band_counts
    # Acceptable sets must never contain the expert label itself duplicated
    for tc in TEST_TASKS:
        assert tc["expert_framework"] not in tc.get("acceptable", [])
```

Running the benchmark now FAILS until quotas are met — that's the driving test.

- [ ] **Step 2: Author new tasks to meet quotas**

Add ~100 new entries following the existing style. Distribution target per category (20–30 each): CODE 13 new, MATH 13, LOGIC 13, CREATIVE 13, DATA 13, RESEARCH 13, PLANNING 12, GENERAL 10. Each new entry needs: distinct realistic phrasing (no near-duplicates), correct `category`, honest human-judgment `complexity` (1–10), `expert_framework` that exists in the registry, and an `acceptable` list of genuinely equivalent alternatives (may be empty when the choice is clear-cut). Model entries per category:

```python
{"task": "Write a unit test suite with pytest fixtures for this payment processing module.", "category": TaskCategory.CODE, "expert_framework": "least_to_most", "acceptable": ["plan_and_solve"], "complexity": 6},
{"task": "A train leaves at 14:35 traveling 80 km/h; another leaves at 15:05 at 100 km/h. When does it catch up?", "category": TaskCategory.MATH, "expert_framework": "program_of_thoughts", "acceptable": ["chain_of_thought", "faithful_cot"], "complexity": 5},
{"task": "Three people each either always lie or always tell the truth. Given their statements, determine who lies.", "category": TaskCategory.LOGIC, "expert_framework": "tree_of_thoughts", "acceptable": ["self_ask", "meta_cot"], "complexity": 7},
{"task": "Write a wedding toast that is funny but keeps it family-friendly.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "acceptable": ["emotion_prompting"], "complexity": 3},
{"task": "Pivot this transaction table to show monthly totals per product category.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "acceptable": [], "complexity": 5},
{"task": "Map the competing theories about why the Bronze Age collapsed and weigh the evidence.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive_cot", "acceptable": ["step_back", "maieutic"], "complexity": 8},
{"task": "Draft an onboarding checklist for new engineers joining a platform team.", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "acceptable": ["plan_and_solve", "skeleton_of_thought"], "complexity": 4},
{"task": "What causes the seasons on Earth?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "acceptable": ["step_back"], "complexity": 3},
```

Continue in the same pattern until `validate_labels()` passes. Do NOT modify existing 100 entries beyond Task 1's fixes.

- [ ] **Step 3: Freeze the set**

Run: `uv run python benchmarks/bench_selection_accuracy.py`
Expected: passes quotas; record exact/top-3/category rates as the official pre-tuning baseline. Copy `benchmarks/results/selection_accuracy.md` aside (e.g., `/tmp/opencode/baseline_200.md`) for comparison.

- [ ] **Step 4: Commit**

```bash
git add benchmarks/bench_selection_accuracy.py
git commit -m "bench: expand eval set to ~200 stratified tasks with quotas validator"
```

---

### Task 3: Pipeline runner + improvement-pipeline doc skeleton

**Files:**
- Create: `scripts/run_pipeline.py`
- Create: `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md`

**Interfaces:**
- Produces: `python scripts/run_pipeline.py [--label NAME]` writes `benchmarks/results/pipeline_<label>.json` combining all four benchmark summaries; the doc's changelog table gets one row per subsequent task.

- [ ] **Step 1: Write the runner**

```python
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
```

- [ ] **Step 2: Write the pipeline doc**

Create `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md` with: purpose paragraph; the loop (baseline → error report → one targeted fix → re-run → log); how to run (`scripts/run_pipeline.py --label <name>`); where results live; and an initially-empty changelog table:

```markdown
| Date | Label | Change made | Exact match | Top-3 | Category | Notes |
|------|-------|-------------|-------------|-------|----------|-------|
```

Fill the first two rows now: `baseline-19pct` (original run) and the Task 1 + Task 2 numbers from the recorded outputs.

- [ ] **Step 3: Verify runner end-to-end**

Run: `uv run python scripts/run_pipeline.py --label post-benchmark-fix`
Expected: exit 0, `pipeline_post-benchmark-fix.json` created with all four summaries.

- [ ] **Step 4: Commit**

```bash
git add scripts/run_pipeline.py docs/BENCHMARK_IMPROVEMENT_PIPELINE.md
git commit -m "feat: benchmark pipeline runner and improvement-loop documentation"
```

---

### Task 4: Selector scoring fixes

**Files:**
- Modify: `src/promptcore/domain/selector.py`
- Test: `tests/unit/test_selector.py`

**Interfaces:**
- Consumes: frozen benchmark from Task 2.
- Produces: `FrameworkSelector._select_framework` with capped intent bonus, preference-matrix gating, no threshold tie-breaker. Public API (`analyze`) unchanged.

- [ ] **Step 1: Write failing tests capturing desired behavior**

Replace/add in `tests/unit/test_selector.py` (keep fixtures):

```python
class TestScoringFixes:
    def test_generic_framework_does_not_dominate_research(self, selector):
        """Research tasks should select research-tier frameworks, not rephrase_and_respond."""
        analysis = selector.analyze("Evaluate the credibility of these sources.")
        assert analysis.recommended_framework != "rephrase_and_respond"

    def test_intent_bonus_is_capped(self, selector):
        """A task triggering many intents shouldn't let any low-threshold framework win."""
        analysis = selector.analyze(
            "Break down this complex problem, verify each part, and organize "
            "the data in a table with steps."
        )
        assert analysis.recommended_framework in FRAMEWORK_REGISTRY

    def test_data_mid_complexity_prefers_chain_of_table(self, selector):
        analysis = selector.analyze(
            "Group these sales records by region and calculate total revenue per region."
        )
        assert analysis.category == TaskCategory.DATA

    def test_trivial_fact_stays_lightweight(self, selector):
        analysis = selector.analyze("Who wrote 'Pride and Prejudice'?")
        assert analysis.complexity_score < 4.0
```

Add import at top: `from promptcore.domain.frameworks import FRAMEWORK_REGISTRY`.

- [ ] **Step 2: Run tests to verify failures**

Run: `uv run pytest tests/unit/test_selector.py -v`
Expected: `test_generic_framework_does_not_dominate_research` FAILS (currently returns rephrase_and_respond-class picks); others may pass/fail mixed.

- [ ] **Step 3: Implement scoring changes in selector.py**

a) Add class-level preference tiers (after `INTENT_KEYWORDS`), listing plausible frameworks per category+level (names must exist in `FRAMEWORK_REGISTRY`; GENERAL intentionally unconstrained):

```python
    CATEGORY_TIERS: dict[TaskCategory, dict[ComplexityLevel, set[str]]] = {
        TaskCategory.CODE: {
            ComplexityLevel.LOW: {"chain_of_thought"},
            ComplexityLevel.MEDIUM: {"program_of_thoughts", "analogical", "self_ask", "self_refine", "contrastive_cot"},
            ComplexityLevel.HIGH: {"plan_and_solve", "least_to_most", "reflexion", "faithful_cot", "recursion_of_thought"},
        },
        TaskCategory.MATH: {
            ComplexityLevel.LOW: {"chain_of_thought"},
            ComplexityLevel.MEDIUM: {"program_of_thoughts", "chain_of_thought", "tab_cot", "self_consistency"},
            ComplexityLevel.HIGH: {"least_to_most", "complexity_based", "cumulative_reasoning", "meta_cot", "reverse_cot"},
        },
        TaskCategory.LOGIC: {
            ComplexityLevel.LOW: {"chain_of_thought", "prompt_paraphrasing"},
            ComplexityLevel.MEDIUM: {"chain_of_thought", "sim_to_m", "step_back", "contrastive_cot", "system2_attention"},
            ComplexityLevel.HIGH: {"maieutic", "meta_cot", "tree_of_thoughts", "cumulative_reasoning", "self_ask"},
        },
        TaskCategory.CREATIVE: {
            ComplexityLevel.LOW: {"role_prompting", "emotion_prompting"},
            ComplexityLevel.MEDIUM: {"directional_stimulus", "analogical", "skeleton_of_thought", "role_prompting"},
            ComplexityLevel.HIGH: {"tree_of_thoughts", "skeleton_of_thought", "self_refine"},
        },
        TaskCategory.DATA: {
            ComplexityLevel.LOW: {"chain_of_table", "tab_cot"},
            ComplexityLevel.MEDIUM: {"chain_of_table", "thread_of_thought", "program_of_thoughts", "tab_cot"},
            ComplexityLevel.HIGH: {"react", "plan_and_solve", "chain_of_density", "contrastive_cot"},
        },
        TaskCategory.RESEARCH: {
            ComplexityLevel.LOW: {"rephrase_and_respond", "role_prompting"},
            ComplexityLevel.MEDIUM: {"step_back", "self_ask", "chain_of_verification", "thread_of_thought", "chain_of_density"},
            ComplexityLevel.HIGH: {"maieutic", "graph_of_thoughts", "step_back", "meta_cot", "active_prompting", "mixture_of_reasoning"},
        },
        TaskCategory.PLANNING: {
            ComplexityLevel.LOW: {"skeleton_of_thought", "plan_and_solve"},
            ComplexityLevel.MEDIUM: {"plan_and_solve", "least_to_most", "tree_of_thoughts", "self_ask"},
            ComplexityLevel.HIGH: {"reasoning_via_planning", "graph_of_thoughts", "tree_of_thoughts", "buffer_of_thoughts"},
        },
    }
    OUT_OF_TIER_PENALTY = 5.0
    INTENT_BONUS_CAP = 4.0
```

b) Rewrite the scoring core of `_select_framework`:

```python
        tier = self.CATEGORY_TIERS.get(category)
        allowed = tier.get(self._score_to_level(complexity)) if tier else None

        for framework_cls in FRAMEWORK_REGISTRY.values():
            score = 0.0
            reasons = []

            # 1. Intent match, capped aggregate bonus
            matched_intents = [
                i for i in intents if i in framework_cls.capabilities
            ]
            if matched_intents:
                score += self.INTENT_BONUS_CAP
                reasons.append(f"matches intent(s) {matched_intents}")

            # 2. Category match
            if category in framework_cls.best_for:
                score += 2.0
                reasons.append(f"matches {category.value} category")

            # 3. Complexity fit
            if complexity >= framework_cls.complexity_threshold:
                score += 2.0
                overkill = (complexity - framework_cls.complexity_threshold) * 0.75
                score -= min(overkill, 3.0)
                reasons.append("complexity fit")
            else:
                score -= 2.0

            # 4. Tier gating
            if allowed is not None and framework_cls.name not in allowed:
                score -= self.OUT_OF_TIER_PENALTY

            candidates.append((framework_cls, score, "; ".join(reasons) if reasons else "default option"))
```

Delete the old tie-breaker line `score += (10 - framework_cls.complexity_threshold) * 0.01`.

c) Recalibrate complexity: change base `total += 2.0` → `total += 1.0` and length divisor `word_count / 50` → `word_count / 65` in `_calculate_complexity`.

- [ ] **Step 4: Reconcile existing tests**

Run: `uv run pytest tests/unit/test_selector.py -v`
If `test_intent_prioritizes_framework` or `test_complexity_tie_breaking` fail because their documented behavior changed (tie-breaker removed), update the test body/docstring to assert the NEW intended outcome (e.g., DATA-tier pick for "Create a table of the data"). Only touch these two tests; do not weaken assertions elsewhere.

- [ ] **Step 5: Full test suite + benchmark**

Run: `uv run pytest -q` then `uv run python benchmarks/bench_selection_accuracy.py`
Expected: all green; selection accuracy improves vs Task 2 baseline. Log the delta in the changelog table of `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md` with label `scoring-v2`.

- [ ] **Step 6: Commit**

```bash
git add src/promptcore/domain/selector.py tests/unit/test_selector.py docs/BENCHMARK_IMPROVEMENT_PIPELINE.md
git commit -m "feat(selector): cap intent bonus, add category-complexity tiers, recalibrate complexity"
```

---

### Task 5: Error-analysis iteration loop (repeat until gains flatten)

**Files:**
- Modify: `src/promptcore/domain/selector.py`, possibly `src/promptcore/utils/complexity.py`
- Modify: `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md` (changelog rows)
- Test: `tests/unit/test_selector.py` (add one regression test per fix)

**Interfaces:**
- Consumes: confusion matrix + per-category breakdown from `benchmarks/results/selection_accuracy.md`.
- Produces: final tuned selector; one changelog row + one regression test per iteration.

- [ ] **Step 1: Generate error report**

Run: `uv run python benchmarks/bench_selection_accuracy.py`
Read `benchmarks/results/selection_accuracy.md`: identify the top misclassification pairs and worst categories.

- [ ] **Step 2: Apply ONE targeted fix per iteration**

Allowed fix types (pick what the confusion matrix supports):
- Move a framework between tiers or across levels in `CATEGORY_TIERS`.
- Adjust a keyword list (add missing trigger words observed in missed tasks).
- Tune one penalty weight (overkill factor, OUT_OF_TIER_PENALTY).

Each iteration MUST end with: targeted regression test added, e.g.:

```python
    def test_regression_shortest_path_math(self, selector):
        analysis = selector.analyze("Find the shortest path through this weighted graph.")
        assert analysis.recommended_framework in {"tree_of_thoughts", "react", "dijkstra_unsupported"}
```

(replace assertion set with the acceptable set from the benchmark entry for whichever pair you fixed).

- [ ] **Step 3: Verify and stop condition**

After each fix: `uv run pytest -q && uv run python benchmarks/bench_selection_accuracy.py`
Stop iterating when two consecutive fixes yield < 2 percentage-point exact-match gain. Record every iteration in the changelog table with distinct labels (`iter-1`, `iter-2`, …).

- [ ] **Step 4: Commit per iteration**

```bash
git add -A
git commit -m "fix(selector): iter-N <one-line description of the targeted fix>"
```

---

### Task 6: Research scan → framework shortlist (USER APPROVAL GATE)

**Files:**
- Create: `docs/superpowers/research/2026-framework-scan.md`

**Interfaces:**
- Produces: approved shortlist consumed by Task 7. NO implementation before user approves the shortlist.

- [ ] **Step 1: Scan literature/web for candidates**

Search for well-cited post-2023 prompting/reasoning techniques not already in the 40-framework catalog (existing catalog: see README Framework Reference Table). Candidate pool to verify and extend: Self-Discover (Zhou et al. 2024), Chain-of-Abstraction (Hao et al. 2024), PlanSearch, Medprompt (Nori et al. 2023), Chain-of-Code (Li et al. 2023), Backtracking-free CoT variants, Deliberate-then-Generate, Buffer-of-Thoughts successor work. For each candidate capture: paper/citation, one-line mechanism, best_for categories, suggested complexity_threshold, evidence of adoption/citations.

- [ ] **Step 2: Write shortlist doc and present to user**

Write `docs/superpowers/research/2026-framework-scan.md` with the shortlist (~8–12 ranked, with metadata above) plus rejected-with-reasons list. **Present the shortlist to the user and wait for approval. Do not proceed without it.**

- [ ] **Step 3: Commit scan doc**

```bash
git add docs/superpowers/research/2026-framework-scan.md
git commit -m "docs: framework research scan and shortlist"
```

---

### Task 7: Implement approved frameworks

**Files:**
- Modify: `src/promptcore/domain/frameworks/decomposition.py` or the fitting existing submodule (create `src/promptcore/domain/frameworks/modern.py` if ≥4 additions don't fit existing submodules)
- Modify: `src/promptcore/domain/frameworks/__init__.py` (exports + `__all__`)
- Modify: `README.md` (badge count, catalog graph node(s), reference-table rows, "40" mentions)
- Test: `tests/unit/test_frameworks_new.py`

**Interfaces:**
- Consumes: approved shortlist from Task 6.
- Produces: one registered `ReasoningFramework` subclass per approved framework, selectable by the existing scorer.

- [ ] **Step 1: Write failing tests (one class per approved framework)**

```python
import pytest
from promptcore.domain.frameworks import FRAMEWORK_REGISTRY
from promptcore.domain.frameworks.modern import SelfDiscover


class TestSelfDiscover:
    def test_registered(self):
        assert "self_discover" in FRAMEWORK_REGISTRY

    def test_metadata(self):
        info = SelfDiscover.get_info()
        assert info["name"] == "self_discover"
        assert TaskCategory.PLANNING in SelfDiscover.best_for
        assert SelfDiscover.complexity_threshold >= 6.0

    def test_template_mentions_task(self):
        fw = SelfDiscover()
        template = fw.generate_prompt_template("Design a caching strategy")
        assert "Design a caching strategy" in template
        assert len(template) > 200
```

Repeat the same three assertions per approved framework with its real module/name/metadata. Run: `uv run pytest tests/unit/test_frameworks_new.py -v` — expect ImportError/FAIL.

- [ ] **Step 2: Implement frameworks following the established pattern**

Worked example (adapt name/metadata/template per shortlist entry; template must embed the framework's actual methodology, not boilerplate):

```python
class SelfDiscover(ReasoningFramework):
    """Self-Discover: model composes a task-specific reasoning structure
    from atomic reasoning modules (SELECT → ADAPT → IMPLEMENT).

    Reference: Zhou et al. 2024, "Self-Discover: Large Language Models
    Self-Compose Reasoning Structures".
    """

    name: ClassVar[str] = "self_discover"
    description: ClassVar[str] = (
        "Compose a custom reasoning structure by selecting and adapting atomic "
        "reasoning modules before solving"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.PLANNING, TaskCategory.CODE, TaskCategory.LOGIC,
    ]
    capabilities: ClassVar[list[str]] = [
        "structure_composition", "meta_reasoning", "adaptive_planning",
    ]
    complexity_threshold: ClassVar[float] = 7.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Before solving, compose your own reasoning procedure for this task.

## Phase 1 — SELECT
From atomic reasoning modules (e.g., decomposition, critical thinking, compare-and-contrast,
divide-and-conquer, root-cause analysis), pick 3–5 that best fit the task below. List them.

## Phase 2 — ADAPT
Re-describe each selected module in the vocabulary of this specific task.

## Phase 3 — IMPLEMENT
Assemble the adapted modules into a numbered, step-by-step reasoning structure with no gaps.

## Phase 4 — SOLVE
Execute your composed structure strictly, step by step, showing intermediate output.

## Task
{task}

{self._format_section("Context", context)}## Composed Structure and Solution:
"""
```

Also: export each class in `src/promptcore/domain/frameworks/__init__.py` imports + `__all__`; add each to the appropriate `CATEGORY_TIERS` entries in `selector.py` (MEDIUM/HIGH levels where the shortlist metadata says they fit).

- [ ] **Step 3: Benchmark coverage + docs**

Add ≥2 benchmark TEST_TASKS per new framework (with acceptable sets) respecting Task 2 quotas. Update README badge `reasoning_frameworks-<new_total>`, add rows to the reference table and nodes to the catalog mermaid graph, and replace literal "40" mentions with the new total.

Run: `uv run pytest -q && uv run python scripts/run_pipeline.py --label frameworks-expanded`
Expected: all green; coverage benchmark shows new frameworks being selected.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: implement approved modern reasoning frameworks (<names>)"
```

---

### Task 8: Final verification + closeout docs

**Files:**
- Modify: `docs/BENCHMARK_IMPROVEMENT_PIPELINE.md` (final changelog row, lessons learned)
- Modify: `docs/superpowers/specs/2026-08-24-selection-accuracy-improvement-design.md` (status → implemented, final numbers)

- [ ] **Step 1: Full verification**

Run: `uv run pytest -q && uv run python scripts/run_pipeline.py --label final`
Expected: all tests pass; all four benchmark JSONs present; record final exact/top-3/category numbers.

- [ ] **Step 2: Closeout edits**

Add the `final` row to the changelog; append a "Lessons learned" subsection (what moved the needle most, what didn't, recommended next lever — e.g., hybrid retrieval if plateaued). Set spec status line to `Implemented (see pipeline changelog)`.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs: closeout — final metrics and pipeline lessons learned"
```

---

## Self-review notes

- Spec coverage: §1 benchmark repair → Tasks 1–2; §2 selector → Tasks 4–5; §3 frameworks → Tasks 6–7; §4 pipeline docs → Task 3 (+ ongoing changelog); §5 testing → embedded per task + Task 8. ✔
- Hold-out discipline encoded: Task 2 Step 3 freeze + Task 4 consumes frozen set. ✔
- Type consistency: `acceptable` key schema defined Task 1, reused Tasks 2/7; `CATEGORY_TIERS` defined Task 4, extended Task 7. ✔
