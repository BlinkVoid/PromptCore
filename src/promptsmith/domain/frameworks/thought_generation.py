"""Thought Generation Frameworks.

Techniques that prompt the LLM to articulate its reasoning
while solving a problem. Includes CoT variants and structured
thought-inducing approaches.

References:
- Wei et al. 2022 (Chain-of-Thought)
- Zheng et al. 2023 (Step-Back)
- Zhou et al. 2023 (Thread-of-Thought)
- Jin & Lu 2023 (Tab-CoT)
- Chia et al. 2023 (Contrastive CoT)
- Fu et al. 2023 (Complexity-Based)
- Diao et al. 2023 (Active Prompting)
- Yasunaga et al. 2023 (Analogical)
- Li et al. 2023 (Directional Stimulus)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class ChainOfThought(ReasoningFramework):
    """Standard step-by-step reasoning for structured problems."""
    
    name: ClassVar[str] = "chain_of_thought"
    description: ClassVar[str] = "Step-by-step logical reasoning with explicit intermediate steps"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["sequential_reasoning", "step_by_step", "analysis"]
    complexity_threshold: ClassVar[float] = 2.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        examples_text = ""
        if examples:
            examples_text = "## Examples\n" + "\n\n".join(examples) + "\n\n"

        return f"""You are solving a problem that requires careful, step-by-step reasoning.

## Task
{task}

{self._format_section("Context", context)}{examples_text}## Instructions
Think through this problem step by step:

1. **Understand**: What is being asked? What are the inputs and expected outputs?
2. **Identify**: What information, constraints, or patterns are relevant?
3. **Plan**: What approach will you take? Break it into logical steps.
4. **Execute**: Work through each step, showing your reasoning.
5. **Verify**: Check your work. Does the solution make sense?

Show your complete reasoning process before providing the final answer.

## Your Step-by-Step Solution:
"""


class StepBack(ReasoningFramework):
    """Ask a high-level principle question before solving."""
    
    name: ClassVar[str] = "step_back"
    description: ClassVar[str] = "First derive high-level principles/concepts, then reason to the specific answer"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.LOGIC, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["abstraction", "principle_extraction", "deep_understanding"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by first stepping back to consider the broader principles.

## Task
{task}

{self._format_section("Context", context)}## Step-Back Process

### Step 1: Step Back — Identify the Underlying Principle
Before answering directly, ask yourself: What is the broader concept, principle, or domain knowledge needed here?
- **High-level question**: [Rephrase the problem at a more abstract, general level]
- **Key principles**: [List the fundamental concepts that govern this domain]

### Step 2: Answer the High-Level Question
Provide a thorough answer to the stepped-back question, grounding yourself in first principles.

### Step 3: Apply to the Specific Problem
Now use your high-level understanding to answer the original, specific question.

### Final Answer
[Your answer, grounded in the principles identified above]

## Begin Step-Back Reasoning:
"""


class ThreadOfThought(ReasoningFramework):
    """Walk through complex context in manageable parts."""
    
    name: ClassVar[str] = "thread_of_thought"
    description: ClassVar[str] = "Walk through context in manageable parts, summarizing and analyzing as you go"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.DATA, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["context_processing", "summarization", "incremental_analysis"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are analyzing a problem by walking through the context systematically.

## Task
{task}

{self._format_section("Context", context)}## Thread-of-Thought Process

Walk me through this context in manageable parts step by step, summarizing and analyzing as we go.

### Part 1: Initial Reading
- **Key information extracted**: [list]
- **Summary so far**: [brief summary]

### Part 2: Deeper Analysis
- **New details found**: [list]
- **How this connects to Part 1**: [analysis]
- **Running summary**: [updated summary]

### Part 3: Synthesis
- **Complete picture**: [full synthesis of all parts]
- **Answer to the original question**: [answer]

## Begin Thread Analysis:
"""


class TabCoT(ReasoningFramework):
    """Output reasoning as a structured markdown table."""
    
    name: ClassVar[str] = "tab_cot"
    description: ClassVar[str] = "Structure reasoning as a markdown table for clarity and organization"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.DATA, TaskCategory.MATH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["tabular_reasoning", "structured_output", "comparison"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by organizing your reasoning in a structured table.

## Task
{task}

{self._format_section("Context", context)}## Tabular Chain-of-Thought

Organize your reasoning steps in a markdown table. Each row should represent one logical step:

| Step | Action | Input | Reasoning | Result |
|------|--------|-------|-----------|--------|
| 1 | [what you're doing] | [what data you're using] | [why] | [outcome] |
| 2 | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |

### Final Answer
Based on the table above: [answer]

## Begin Tabular Reasoning:
"""


class ContrastiveCoT(ReasoningFramework):
    """Include correct AND incorrect reasoning examples."""
    
    name: ClassVar[str] = "contrastive_cot"
    description: ClassVar[str] = "Show both correct and incorrect reasoning paths to guide the model"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["error_awareness", "contrastive_learning", "robust_reasoning"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by considering both correct and incorrect reasoning paths.

## Task
{task}

{self._format_section("Context", context)}## Contrastive Chain-of-Thought

### Step 1: Identify Common Mistakes
What are the typical wrong approaches or misconceptions for this type of problem?

**❌ Incorrect Approach**: [Describe a plausible but wrong reasoning path]
- Why this fails: [explanation]

**❌ Another Pitfall**: [Describe another common mistake]
- Why this fails: [explanation]

### Step 2: Correct Reasoning Path
Now, avoiding the pitfalls above, reason through the problem correctly:

**✅ Correct Approach**: [Step-by-step correct reasoning]
- Why this works: [explanation for each step]

### Final Answer
[Answer, with confidence based on having ruled out incorrect paths]

## Begin Contrastive Reasoning:
"""


class ComplexityBased(ReasoningFramework):
    """Select complex exemplars and vote on longer reasoning chains."""
    
    name: ClassVar[str] = "complexity_based"
    description: ClassVar[str] = "Favor longer, more detailed reasoning chains for higher quality answers"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["deep_reasoning", "thoroughness", "quality_through_depth"]
    complexity_threshold: ClassVar[float] = 6.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a complex problem that demands thorough, detailed reasoning.

## Task
{task}

{self._format_section("Context", context)}## Complexity-Based Prompting

### Instruction
This problem requires deep analysis. Do NOT take shortcuts. Generate the most detailed, thorough reasoning chain possible.

### Detailed Reasoning
Work through EVERY sub-step explicitly. Do not skip any intermediate steps, even if they seem obvious:

1. [First step with full detail]
2. [Second step with full detail]
3. [Continue with granular steps...]
...

### Verification Through Length
Review your reasoning. If your solution seems too short or skips steps, expand it. The more thorough your reasoning, the more likely you are to be correct.

### Final Answer
[Answer derived from the detailed chain above]

## Begin Deep Reasoning:
"""


class ActivePrompting(ReasoningFramework):
    """Target uncertain areas with focused exemplars."""
    
    name: ClassVar[str] = "active_prompting"
    description: ClassVar[str] = "Identify high-uncertainty areas and focus reasoning effort there"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.RESEARCH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["uncertainty_targeting", "focused_reasoning", "adaptive"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by focusing your reasoning on the most uncertain parts.

## Task
{task}

{self._format_section("Context", context)}## Active Prompting Process

### Step 1: Initial Assessment
Provide a quick first-pass answer and identify which parts you're uncertain about:
- **Preliminary answer**: [answer]
- **Confidence**: [high/medium/low]
- **Uncertain areas**: [list specific parts you're unsure about]

### Step 2: Deep-Dive on Uncertainties
For each uncertain area, apply focused reasoning:

**Uncertainty 1**: [description]
- Additional analysis: [detailed reasoning]
- Resolution: [resolved answer]

**Uncertainty 2**: [description]
- Additional analysis: [detailed reasoning]
- Resolution: [resolved answer]

### Step 3: Revised Answer
Incorporating the resolved uncertainties:
[Final, refined answer]

## Begin Active Reasoning:
"""


class Analogical(ReasoningFramework):
    """Recall relevant examples before solving."""
    
    name: ClassVar[str] = "analogical"
    description: ClassVar[str] = "Recall relevant examples or patterns before solving the target problem"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.CREATIVE, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["pattern_matching", "example_recall", "analogy"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by first drawing analogies to similar known problems.

## Task
{task}

{self._format_section("Context", context)}## Analogical Process

### Step 1: Recall Analogies
Identify 1-2 distinct problems that are similar to this one.
- **Analogy 1**: [Description of similar problem + Solution]
- **Analogy 2**: [Description of similar problem + Solution]

### Step 2: Extract Learnings
What principles from these analogies apply here?
- Pattern: [e.g., divide and conquer, dynamic programming, etc.]
- Pitfall to avoid: [e.g., off-by-one error]

### Step 3: Solve Target Problem
Apply these learnings to solve the current task.

[Final Solution]

## Begin Analogical Reasoning:
"""


class DirectionalStimulus(ReasoningFramework):
    """Use keyword hints to guide generation direction."""
    
    name: ClassVar[str] = "directional_stimulus"
    description: ClassVar[str] = "Use strategic keywords and hints to guide the reasoning direction"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["guided_generation", "creative_direction", "keyword_steering"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are generating a response guided by strategic directional cues.

## Task
{task}

{self._format_section("Context", context)}## Directional Stimulus Process

### Step 1: Extract Key Concepts
Identify the most important concepts, entities, and relationships in the task:
- **Key nouns**: [list]
- **Key actions**: [list]
- **Key constraints**: [list]

### Step 2: Generate Directional Keywords
Create stimulus keywords that should guide your response:
- **Must include**: [essential keywords]
- **Should include**: [helpful keywords]  
- **Tone/style**: [descriptive keywords]

### Step 3: Constrained Generation
Generate your response, ensuring it incorporates the directional keywords naturally:

[Your response here, weaving in the keywords]

### Step 4: Verify Coverage
Check that all essential keywords and concepts are addressed.

## Begin Guided Generation:
"""
