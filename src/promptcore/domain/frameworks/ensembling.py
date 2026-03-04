"""Ensembling Frameworks.

Techniques that use multiple prompts or reasoning paths to solve
the same problem, then aggregate responses into a final output.

References:
- Wang et al. 2022 (Self-Consistency)
- Khalifa et al. 2023 (DENSE)
- Si et al. 2023 (MoRE)
- Yoran et al. 2023 (Meta-CoT)
- Jiang et al. 2020 (Prompt Paraphrasing)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class SelfConsistency(ReasoningFramework):
    """Generate multiple solution paths and find consensus."""
    
    name: ClassVar[str] = "self_consistency"
    description: ClassVar[str] = "Sample multiple reasoning paths and select the most consistent answer"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["verification", "consensus", "confidence", "ambiguity_resolution"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using multiple independent reasoning attempts.

## Task
{task}

{self._format_section("Context", context)}## Self-Consistency Process

### Attempt 1
Solve the problem using your first instinct:
[reasoning path 1]
**Answer 1**: [answer]

### Attempt 2
Solve again, trying a different approach or perspective:
[reasoning path 2]
**Answer 2**: [answer]

### Attempt 3
One more attempt, perhaps checking edge cases or using verification:
[reasoning path 3]
**Answer 3**: [answer]

### Consistency Analysis
- Do the answers agree? If yes, high confidence.
- If they differ, analyze why:
  - Which reasoning path had errors?
  - What's the most defensible answer?

### Final Answer
Based on consistency analysis: [final answer with confidence level]

## Begin Multiple Attempts:
"""


class DemonstrationEnsembling(ReasoningFramework):
    """Multiple few-shot prompts with distinct exemplar subsets."""
    
    name: ClassVar[str] = "demonstration_ensembling"
    description: ClassVar[str] = "Create multiple prompts with different exemplar subsets and aggregate results"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.DATA, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["ensemble", "diverse_perspectives", "robustness"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by approaching it from multiple perspectives with different reference frames.

## Task
{task}

{self._format_section("Context", context)}## Demonstration Ensembling Process

### Perspective 1: Textbook Approach
Solve this as it would be solved in a standard textbook:
[reasoning and answer]

### Perspective 2: Practical / Real-World Approach
Solve this as a practitioner would in the real world:
[reasoning and answer]

### Perspective 3: First-Principles Approach
Solve this by reasoning from fundamental axioms:
[reasoning and answer]

### Ensemble Aggregation
Compare all three perspectives:
- **Agreement**: [which answers agree]
- **Disagreements**: [where they differ and why]
- **Best answer**: [selected answer with justification]

## Begin Ensemble:
"""


class MixtureOfReasoning(ReasoningFramework):
    """Diverse reasoning experts scored by agreement."""
    
    name: ClassVar[str] = "mixture_of_reasoning"
    description: ClassVar[str] = "Apply different specialized reasoning strategies and select the best by agreement"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.RESEARCH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["multi_strategy", "expert_routing", "agreement_scoring"]
    complexity_threshold: ClassVar[float] = 6.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using multiple specialized reasoning strategies.

## Task
{task}

{self._format_section("Context", context)}## Mixture of Reasoning Experts

### Expert 1: Logical/Deductive Reasoning
Apply strict logical deduction:
[reasoning and conclusion]

### Expert 2: Analogical/Pattern-Based Reasoning
Draw on similar known problems:
[reasoning and conclusion]

### Expert 3: Empirical/Evidence-Based Reasoning
What does evidence and data suggest?
[reasoning and conclusion]

### Expert 4: Creative/Lateral Thinking
Is there an unconventional angle?
[reasoning and conclusion]

### Agreement Scoring
| Expert | Answer | Confidence |
|--------|--------|------------|
| Logical | [ans] | [H/M/L] |
| Analogical | [ans] | [H/M/L] |
| Empirical | [ans] | [H/M/L] |
| Creative | [ans] | [H/M/L] |

### Final Answer
Based on agreement and confidence: [answer]

## Begin Multi-Expert Reasoning:
"""


class MetaCoT(ReasoningFramework):
    """Generate multiple reasoning chains, then aggregate in a meta-prompt."""
    
    name: ClassVar[str] = "meta_cot"
    description: ClassVar[str] = "Generate multiple reasoning chains, then synthesize them in a meta-level analysis"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.LOGIC, TaskCategory.MATH, TaskCategory.RESEARCH]
    capabilities: ClassVar[list[str]] = ["meta_reasoning", "chain_aggregation", "synthesis"]
    complexity_threshold: ClassVar[float] = 6.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by generating multiple reasoning chains and then reasoning over them.

## Task
{task}

{self._format_section("Context", context)}## Meta Chain-of-Thought Process

### Chain 1
[Complete reasoning chain leading to an answer]
**Conclusion 1**: [answer]

### Chain 2
[Different reasoning approach]
**Conclusion 2**: [answer]

### Chain 3
[Yet another approach]
**Conclusion 3**: [answer]

### Meta-Level Reasoning
Now, step back and reason over ALL the chains above:
- **What each chain got right**: [analysis]
- **Where chains diverged**: [analysis]
- **What the strongest chain is and why**: [analysis]
- **Synthesis**: [what can be learned from combining all chains]

### Final Synthesized Answer
[Answer informed by meta-analysis of all chains]

## Begin Meta-Reasoning:
"""


class PromptParaphrasing(ReasoningFramework):
    """Augment the prompt with paraphrases and ensemble results."""
    
    name: ClassVar[str] = "prompt_paraphrasing"
    description: ClassVar[str] = "Rephrase the problem in multiple ways and solve each, then aggregate"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["robustness", "paraphrasing", "bias_reduction"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by rephrasing it in multiple ways to ensure robustness.

## Original Task
{task}

{self._format_section("Context", context)}## Prompt Paraphrasing Process

### Paraphrase 1 (Formal)
**Restated**: [formal, precise rephrasing]
**Answer**: [solve this version]

### Paraphrase 2 (Simplified)
**Restated**: [simpler, plain-language rephrasing]
**Answer**: [solve this version]

### Paraphrase 3 (Reversed/Negated)
**Restated**: [rephrase from different angle]
**Answer**: [solve this version]

### Consistency Check
Do all paraphrased versions yield the same answer?
- If yes: High confidence in [answer]
- If no: [analyze which rephrasing revealed the correct interpretation]

### Final Answer
[Most robust answer across all phrasings]

## Begin Paraphrasing:
"""
