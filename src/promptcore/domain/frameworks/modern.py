"""Modern Frameworks (2023–2026 wave).

Post-2023 reasoning frameworks kept together as a coherent batch so
old-vs-new selector accuracy can be A/B benchmarked cleanly.

References:
- Zhou et al. 2024, arXiv:2402.03620 (Self-Discover, NeurIPS 2024)
- Xu, Xie, Zhao & He 2025, arXiv:2502.18600 (Chain of Draft)
- Gou et al. 2024, arXiv:2305.11738 (CRITIC, ICLR 2024)
- Li et al. 2024, arXiv:2312.04474 (Chain of Code, ICML 2024)
- Xu et al. 2024, arXiv:2309.06275 (RE2 Re-Reading, EMNLP 2024)
- Gao et al. 2024, arXiv:2401.17464 (Chain-of-Abstraction)
- Bei Li et al. 2023, arXiv:2305.19835 (Deliberate-then-Generate, AAAI 2024)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


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
        TaskCategory.GENERAL, TaskCategory.LOGIC,
        TaskCategory.PLANNING, TaskCategory.RESEARCH,
    ]
    capabilities: ClassVar[list[str]] = [
        "structure_composition", "meta_reasoning", "adaptive_planning", "planning",
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


class ChainOfDraft(ReasoningFramework):
    """Chain of Draft: every intermediate reasoning step is limited to
    at most five words, producing terse dense drafts instead of verbose CoT.

    Reference: Xu, Xie, Zhao & He 2025, "Chain of Draft: Thinking Faster
    by Writing Less".
    """

    name: ClassVar[str] = "chain_of_draft"
    description: ClassVar[str] = (
        "Reason through the task in ultra-concise draft steps of five words "
        "or fewer, minimizing tokens while keeping accuracy"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.CODE,
        TaskCategory.CREATIVE, TaskCategory.GENERAL,
    ]
    capabilities: ClassVar[list[str]] = [
        "token_efficiency", "latency_reduction", "summarization",
    ]
    complexity_threshold: ClassVar[float] = 3.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Solve this task using minimal-output reasoning drafts.

## Task
{task}

{self._format_section("Context", context)}## Chain-of-Draft Rules

### Step 1 — Draft the Steps
Work toward the answer one step at a time. HARD LIMIT: each step must be
at most **five words**. No full sentences. No elaboration.

Example shape:
1. identify given quantities
2. set up equation
3. isolate unknown term
4. compute result: [value]

### Step 2 — Final Answer
Expand ONLY the conclusion into one clear sentence. The drafts above stay terse;
the density of each draft must carry the full reasoning content.

## Your Terse Drafts:
"""


class Critic(ReasoningFramework):
    """CRITIC: verify-then-correct loop — the model critiques its own draft
    with tool-grounded evidence (search, code execution), then revises.

    Reference: Gou et al., ICLR 2024, "CRITIC: Large Language Models Can
    Self-Correct with Tool-Interactive Critiquing".
    """

    name: ClassVar[str] = "critic"
    description: ClassVar[str] = (
        "Draft an answer, critique it against external tools and evidence, "
        "then iteratively correct before finalizing"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.RESEARCH, TaskCategory.DATA,
        TaskCategory.CODE, TaskCategory.GENERAL,
    ]
    capabilities: ClassVar[list[str]] = [
        "verification", "self_correction", "tool_use",
    ]
    complexity_threshold: ClassVar[float] = 6.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Answer this task through a verify-then-correct loop.

## Task
{task}

{self._format_section("Context", context)}## CRITIC Process

### Step 1 — Initial Draft
Produce a first-pass answer without self-censoring uncertain claims.
Mark each factual claim with [C] (checkable) or [J] (judgment).

### Step 2 — Tool-Interactive Critique
For every [C] claim, specify how an external tool could validate it:
- search / lookup: what exact query or source?
- code execution: what computation would confirm the number?
- database / document check: which record or passage?
Flag each claim as CONFIRMED, REFUTED, or UNVERIFIABLE.

### Step 3 — Corrective Revision
Rewrite the draft, fixing every refuted or unsupported claim.
Do not reuse a claim unless it survived the critique.

### Step 4 — Final Verified Answer
Emit the revised answer, listing the corrections you made.

## Begin Draft–Critique–Correct Loop:
"""


class ChainOfCode(ReasoningFramework):
    """Chain of Code: express sub-tasks as code; the interpreter runs the
    executable parts while the LLM emulates undefined semantic functions
    (the "LMulator") when no interpreter exists.

    Reference: Li et al., ICML 2024, "Chain of Code: Reasoning with a
    Language Model-Augmented Code Emulator".
    """

    name: ClassVar[str] = "chain_of_code"
    description: ClassVar[str] = (
        "Solve by writing code per sub-task, executing what runs, and "
        "emulating the rest as the LMulator when no interpreter applies"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.CODE, TaskCategory.MATH,
        TaskCategory.DATA, TaskCategory.LOGIC,
    ]
    capabilities: ClassVar[list[str]] = [
        "code_reasoning", "code_emulation", "pseudocode_fallback",
    ]
    complexity_threshold: ClassVar[float] = 6.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Solve this task as a chain of code, mixing real execution with emulation.

## Task
{task}

{self._format_section("Context", context)}## Chain-of-Code Process

### Step 1 — Decompose into Sub-Tasks
Break the problem into small computational steps (parsing, arithmetic,
lookup, comparison, generation of candidates...).

### Step 2 — Write Code per Step
Express each step as short code. For every fragment, classify it:
- EXECUTABLE: deterministic numeric/logic/data manipulation → write runnable code.
- SEMANTIC: needs language understanding (tone, intent, plausibility...) →
  write a function stub the model itself must emulate.

### Step 3 — Execute or Emulate
Run the executable fragments and show their outputs. For semantic stubs,
act as the LMulator: emulate the function's return value and state why it
is plausible. If a fragment cannot be coded precisely, fall back to
structured pseudocode and simulate it line by line.

### Step 4 — Assemble the Result
Feed all outputs forward through the chain and state the final answer.

## Begin Code Chain:
"""


class Re2ReReading(ReasoningFramework):
    """RE2 (Re-Reading): repeat the question in the input so the second
    occurrence is read with 'later' token context — pseudo-bidirectional
    encoding for decoder-only models. Composable with any output-phase
    technique.

    Reference: Xu et al., EMNLP 2024, "RE2: Simple and Effective Method
    for Enhancing Reasoning in Language Models".
    """

    name: ClassVar[str] = "re2_re_reading"
    description: ClassVar[str] = (
        "Re-read the question a second time before answering, exploiting "
        "repeated input for stronger comprehension"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.RESEARCH,
    ]
    capabilities: ClassVar[list[str]] = [
        "input_repetition", "bidirectional_encoding", "composability", "clarification",
    ]
    complexity_threshold: ClassVar[float] = 2.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Use two-pass re-reading before answering.

## First Reading of the Question
{task}

{self._format_section("Context", context)}## Second Reading of the Question
Read the question again, now knowing it in full:

{task}

## Instructions

### Pass 1 — Surface Understanding
After the first reading, note only what the question asks and what is given.

### Pass 2 — Deepened Understanding
On the second reading, resolve details you could not know during the first
pass (scope, constraints, what kind of answer is expected). State anything
your understanding changed between passes.

### Answer
Now answer the question, relying on your second-pass understanding.

## Your Two-Pass Response:
"""


class ChainOfAbstraction(ReasoningFramework):
    """Chain-of-Abstraction: first decode a reasoning chain with abstract
    placeholders (y1, y2, ...), then infill concrete values from knowledge
    or tools in one batch — decoupling reasoning from retrieval and keeping
    the chain robust out-of-domain.

    Reference: Gao et al. 2024, "Chain-of-Abstraction: Reasoning with
    Mixed Language and Symbolic Chains" (FAIR/EPFL).
    """

    name: ClassVar[str] = "chain_of_abstraction"
    description: ClassVar[str] = (
        "Reason with abstract placeholder variables first, then infill "
        "their concrete values from tools or knowledge in one deferred step"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.MATH, TaskCategory.DATA, TaskCategory.RESEARCH,
    ]
    capabilities: ClassVar[list[str]] = [
        "abstraction", "placeholder_infilling", "deferred_tool_infilling",
    ]
    complexity_threshold: ClassVar[float] = 5.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Solve in two detached stages: abstract chain first, grounding last.

## Task
{task}

{self._format_section("Context", context)}## Stage 1 — Abstract Reasoning Chain
Derive the full solution chain while referring to every needed quantity,
entity, or lookup result ONLY as abstract placeholders (y1, y2, y3, ...).
Write the chain as symbolic operations over these placeholders, e.g.:
y3 = f(y1, y2); answer = g(y3, y4).
Do NOT guess any concrete value yet.

## Stage 2 — Placeholder Infilling
Now, in one batch:
1. List each placeholder and where its value comes from (given data, known
   fact, or a specific tool/query).
2. Fill in the concrete values.
3. Replay the abstract chain with real values to produce the final answer.

If a placeholder cannot be grounded, mark it explicitly instead of inventing
a value.

## Abstract Chain, then Infilled Solution:
"""


class DeliberateThenGenerate(ReasoningFramework):
    """Deliberate-then-Generate: force explicit error-detection deliberation
    on a deliberately flawed (or empty) candidate before generating the
    final output, improving generation quality at single-step cost.

    Reference: Bei Li et al. 2023, "Deliberate then Generate: Harnessing
    the Power of Error Detection in Text Generation" (AAAI 2024).
    """

    name: ClassVar[str] = "deliberate_then_generate"
    description: ClassVar[str] = (
        "Detect errors in a deliberately flawed candidate response first, "
        "then generate the corrected final output"
    )
    best_for: ClassVar[list[TaskCategory]] = [
        TaskCategory.CREATIVE, TaskCategory.GENERAL, TaskCategory.RESEARCH,
    ]
    capabilities: ClassVar[list[str]] = [
        "error_awareness", "candidate_critique", "generation_quality",
    ]
    complexity_threshold: ClassVar[float] = 4.0

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Generate the best answer by first deliberating over a flawed candidate.

## Task
{task}

{self._format_section("Context", context)}## Deliberate-then-Generate Process

### Step 1 — Flawed Candidate
Sketch a hasty, plausible-but-imperfect response to the task. Do not try
to make it good; make it typical of a rushed first attempt.

### Step 2 — Error Detection
Deliberately hunt for defects in that candidate:
- factual mistakes or unsupported claims,
- missed constraints or requirements from the task,
- coherence, tone, or completeness problems.
List each defect explicitly.

### Step 3 — Final Generation
Generate the final output, actively avoiding every defect found above.
The final answer must stand alone and must not mention the flawed draft.

## Flawed Candidate, Detected Errors, and Final Output:
"""
