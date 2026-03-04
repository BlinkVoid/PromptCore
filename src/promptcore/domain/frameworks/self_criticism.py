"""Self-Criticism Frameworks.

Techniques where the LLM critiques, verifies, or refines its
own outputs to improve quality and correctness.

References:
- Madaan et al. 2023 (Self-Refine)
- Kadavath et al. 2022 (Self-Calibration)
- Shinn et al. 2023 (Reflexion)
- Jung et al. 2022 (Maieutic)
- Dhuliawala et al. 2023 (Chain of Verification)
- Xue et al. 2023 (Reverse CoT)
- Zhang et al. 2023 (Cumulative Reasoning)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class Reflexion(ReasoningFramework):
    """Self-correction through reflection on past failures."""
    
    name: ClassVar[str] = "reflexion"
    description: ClassVar[str] = "Self-critique and refinement cycle to improve answer validation"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CODE, TaskCategory.MATH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["self_correction", "critique", "refinement", "error_handling"]
    complexity_threshold: ClassVar[float] = 8.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a difficult problem using self-reflection and correction.

## Task
{task}

{self._format_section("Context", context)}## Reflexion Process

### Draft 1
Provide your initial solution attempt.
[Draft 1 Solution]

### Reflection 1
Critique Draft 1. 
- correct: [bool] - Is it 100% correct?
- error_analysis: What specifically is wrong? (Logic error, missing edge case, syntax error?)
- hint: What specific change typically fixes this type of error?

### Draft 2 (Improved)
Based on Reflection 1, rewrite the solution.
[Draft 2 Solution]

### Final Verification
Does Draft 2 satisfy all constraints?

## Begin Reflexion:
"""


class Maieutic(ReasoningFramework):
    """Recursive explanation and verification for deep understanding."""
    
    name: ClassVar[str] = "maieutic"
    description: ClassVar[str] = "Recursively explain and verify claims through Socratic questioning"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.LOGIC, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["explanation", "recursive_verification", "socratic", "truth_seeking"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are finding truth through recursive explanation and self-questioning.

## Task
{task}

{self._format_section("Context", context)}## Maieutic Process

### Initial Answer
Provide your first answer to the question:
[initial answer]

### Explanation Tree
For your answer, ask: "Why is this true?" and explain.
Then for each explanation, ask again: "Why is THIS true?"

**Level 1 - Why is [answer] true?**
→ Because [explanation 1]

  **Level 2 - Why is [explanation 1] true?**
  → Because [deeper explanation]
  
    **Level 3 - Can we verify this?**
    → [verification or foundational truth]

### Identify Contradictions
Are there any contradictions or weak links in the explanation tree?
- Check each claim for logical consistency
- Identify unsupported assumptions

### Refined Answer
Based on the explanation tree and contradiction check:
[refined, verified answer]

## Begin Socratic Exploration:
"""


class ChainOfVerification(ReasoningFramework):
    """Draft an answer, create verification questions, then revise."""
    
    name: ClassVar[str] = "chain_of_verification"
    description: ClassVar[str] = "Generate an answer, create verification questions, answer them, then revise"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.GENERAL, TaskCategory.DATA]
    capabilities: ClassVar[list[str]] = ["verification", "fact_checking", "hallucination_reduction"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using a systematic verification pipeline.

## Task
{task}

{self._format_section("Context", context)}## Chain-of-Verification Process

### Step 1: Draft Initial Response
[Your initial answer — respond fully but know you will verify it]

### Step 2: Plan Verification Questions
Generate questions that would help verify the correctness of your draft:
1. [Verification Q1 — checks a specific claim in the draft]
2. [Verification Q2 — checks another claim]
3. [Verification Q3 — checks for completeness]
4. [Verification Q4 — checks for edge cases]

### Step 3: Answer Verification Questions
**Q1**: [answer, with evidence]
**Q2**: [answer, with evidence]
**Q3**: [answer, with evidence]
**Q4**: [answer, with evidence]

### Step 4: Revised Final Response
Incorporating all verification findings, provide the corrected answer:
[Revised answer with any corrections applied]

## Begin Verification Chain:
"""


class SelfRefine(ReasoningFramework):
    """Iterative answer → feedback → improve loop."""
    
    name: ClassVar[str] = "self_refine"
    description: ClassVar[str] = "Iteratively generate, get self-feedback, and refine until quality threshold is met"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.CODE, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["iterative_improvement", "self_feedback", "quality_optimization"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are improving your response through iterative self-feedback and refinement.

## Task
{task}

{self._format_section("Context", context)}## Self-Refine Process

### Iteration 1: Initial Draft
[Your first attempt]

### Feedback on Iteration 1
Rate your draft on these dimensions (1-10):
- **Correctness**: [score] — [specific issues]
- **Completeness**: [score] — [what's missing]
- **Clarity**: [score] — [what's confusing]
- **Actionable improvements**: [list specific changes to make]

### Iteration 2: Refined Version
Applying the feedback above:
[Improved version]

### Feedback on Iteration 2
- **Correctness**: [score]
- **Completeness**: [score]
- **Clarity**: [score]
- **Remaining issues**: [if any]

### Final Version
[Polished final answer — if Iteration 2 scored well, use it; otherwise refine once more]

## Begin Iterative Refinement:
"""


class SelfCalibration(ReasoningFramework):
    """Ask the LLM if its own answer is correct."""
    
    name: ClassVar[str] = "self_calibration"
    description: ClassVar[str] = "After answering, ask whether the answer is correct and estimate confidence"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["confidence_estimation", "self_assessment", "calibration"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem with built-in confidence calibration.

## Task
{task}

{self._format_section("Context", context)}## Self-Calibration Process

### Step 1: Solve the Problem
[Your solution and answer]

### Step 2: Self-Assessment
Now critically evaluate your answer:
- **Is this answer correct?** [Yes/Probably/Uncertain/Probably Not]
- **Confidence level**: [0-100%]
- **What could be wrong**: [list potential issues]
- **What would change your answer**: [describe conditions]

### Step 3: Decision
Based on your confidence:
- If confidence ≥ 80%: Accept the answer
- If confidence < 80%: Re-examine and try again

**Final answer**: [answer]
**Calibrated confidence**: [percentage]

## Begin Calibrated Reasoning:
"""


class ReverseCoT(ReasoningFramework):
    """Reconstruct the problem from the answer to find inconsistencies."""
    
    name: ClassVar[str] = "reverse_cot"
    description: ClassVar[str] = "Reconstruct the original problem from your answer to check for inconsistencies"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["reverse_verification", "consistency_checking", "error_detection"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are verifying your answer by working backward to reconstruct the original problem.

## Task
{task}

{self._format_section("Context", context)}## Reverse Chain-of-Thought Process

### Step 1: Forward Solve
Solve the problem normally:
[Your solution]
**Answer**: [answer]

### Step 2: Reverse Reconstruction
Starting from your answer, reconstruct what the original problem must have been:
- **Given my answer [X], the problem must have stated**: [reconstructed problem]
- **The constraints must have been**: [reconstructed constraints]
- **The input must have been**: [reconstructed input]

### Step 3: Compare
Compare the reconstructed problem with the actual problem:
- **Match?** [Yes/No]
- **Discrepancies found**: [list any mismatches]

### Step 4: Revise if Needed
If discrepancies exist, revise the answer:
[Corrected answer, or confirm original answer]

## Begin Reverse Verification:
"""


class CumulativeReasoning(ReasoningFramework):
    """Propose reasoning steps, verify each, accumulate confirmed facts."""
    
    name: ClassVar[str] = "cumulative_reasoning"
    description: ClassVar[str] = "Propose reasoning steps, verify each one, and accumulate only confirmed facts toward the answer"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.LOGIC, TaskCategory.MATH, TaskCategory.RESEARCH]
    capabilities: ClassVar[list[str]] = ["incremental_verification", "fact_accumulation", "rigorous_reasoning"]
    complexity_threshold: ClassVar[float] = 6.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are building an answer by proposing and verifying facts one at a time.

## Task
{task}

{self._format_section("Context", context)}## Cumulative Reasoning Process

### Confirmed Facts Bank
(Start empty, accumulate verified facts)

### Round 1
**Proposed fact**: [a candidate reasoning step or claim]
**Verification**: [Is this definitely true? Check against known information]
**Decision**: ✅ Accept / ❌ Reject
→ If accepted, add to Confirmed Facts Bank

### Round 2
**Proposed fact**: [next candidate, building on confirmed facts]
**Verification**: [check]
**Decision**: ✅ Accept / ❌ Reject

### Round 3
[Continue...]

### Check: Have we reached the final answer?
- If yes: State the answer based on all confirmed facts
- If no: Continue proposing and verifying

### Final Answer
Based on accumulated confirmed facts:
[Answer grounded in verified reasoning chain]

## Begin Cumulative Reasoning:
"""
