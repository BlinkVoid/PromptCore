"""Zero-Shot Prompting Frameworks.

Techniques that use no exemplars but leverage specific prompt
structures to improve LLM performance.

References:
- Wang et al. 2023 (Role Prompting)
- Li et al. 2023 (Emotion Prompting)
- Weston & Sukhbaatar 2023 (System 2 Attention)
- Wilf et al. 2023 (SimToM)
- Deng et al. 2023 (Rephrase and Respond)
- Press et al. 2022 (Self-Ask)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class RolePrompting(ReasoningFramework):
    """Assign a persona/role to shape the model's output."""
    
    name: ClassVar[str] = "role_prompting"
    description: ClassVar[str] = "Assign a specific expert role/persona to shape output quality and style"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.GENERAL, TaskCategory.RESEARCH]
    capabilities: ClassVar[list[str]] = ["persona", "expert_voice", "style_control"]
    complexity_threshold: ClassVar[float] = 1.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are a world-class expert specifically suited to this task. Adopt the most relevant expert persona.

## Your Expert Role
Identify and adopt the ideal expert persona for this task. State your role, qualifications, and relevant experience.

**I am a**: [expert role, e.g., "Senior Software Architect with 20 years of experience"]

## Task
{task}

{self._format_section("Context", context)}## Instructions
Respond as this expert would — with the appropriate depth, terminology, and professional judgment.

## Expert Response:
"""


class EmotionPrompting(ReasoningFramework):
    """Incorporate emotional stimuli to improve performance."""
    
    name: ClassVar[str] = "emotion_prompting"
    description: ClassVar[str] = "Add emotionally relevant phrases to enhance LLM engagement and performance"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["emotional_engagement", "motivation", "quality_boost"]
    complexity_threshold: ClassVar[float] = 1.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""This is very important to my career. I need you to give this your absolute best effort.

## Task
{task}

{self._format_section("Context", context)}## Instructions
This task is critical and demands your highest quality work. Take pride in delivering an excellent response. Your thoroughness and accuracy here will make a real difference.

Are you sure that's your final answer? Make sure to double-check your work before submitting.

## Your Best Response:
"""


class System2Attention(ReasoningFramework):
    """Rewrite the prompt removing irrelevant info, then answer."""

    name: ClassVar[str] = "system2_attention"
    description: ClassVar[str] = "First rewrite the prompt removing irrelevant information, then answer the clarified question"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.LOGIC, TaskCategory.RESEARCH, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["noise_filtering", "focus", "clarification"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using a two-pass attention process.

## Original Task
{task}

{self._format_section("Original Context", context)}## System 2 Attention Process

### Pass 1: Filter and Clarify
Rewrite the task and context, removing any information that is:
- Irrelevant to the core question
- Potentially misleading or biasing
- Redundant or distracting

**Clarified Task**: [rewritten, focused version]
**Essential Facts Only**: [filtered context]

### Pass 2: Answer the Clarified Question
Now answer the clarified, focused version of the question:

[Your answer based only on relevant information]

## Begin Two-Pass Analysis:
"""


class SimToM(ReasoningFramework):
    """Theory of Mind: establish a character's knowledge, then answer."""
    
    name: ClassVar[str] = "sim_to_m"
    description: ClassVar[str] = "Simulate Theory of Mind — establish what each entity knows, then answer from their perspective"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.LOGIC, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["perspective_taking", "theory_of_mind", "multi_entity_reasoning"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem that involves understanding what different entities know or believe.

## Task
{task}

{self._format_section("Context", context)}## SimToM Process

### Step 1: Identify Entities
List all people, agents, or entities involved:
- **Entity A**: [who]
- **Entity B**: [who]

### Step 2: Establish Knowledge States
For each entity, what do they know? What are they unaware of?

**Entity A knows**: [list facts they have access to]
**Entity A does NOT know**: [list facts hidden from them]

**Entity B knows**: [list facts they have access to]
**Entity B does NOT know**: [list facts hidden from them]

### Step 3: Answer from Correct Perspective
Based on the relevant entity's knowledge state (not your omniscient view), answer the question:

[Answer grounded in the correct entity's perspective]

## Begin Perspective Analysis:
"""


class RephraseAndRespond(ReasoningFramework):
    """Rephrase and expand the question before answering."""
    
    name: ClassVar[str] = "rephrase_and_respond"
    description: ClassVar[str] = "Rephrase and expand the question to ensure full understanding before answering"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.RESEARCH]
    capabilities: ClassVar[list[str]] = ["clarification", "question_improvement", "comprehension"]
    complexity_threshold: ClassVar[float] = 2.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are improving a question before answering it.

## Original Task
{task}

{self._format_section("Context", context)}## Rephrase and Respond Process

### Step 1: Rephrase the Question
Rewrite the question to be clearer, more precise, and more complete. Expand any ambiguities:

**Rephrased question**: [improved version that captures the full intent]

### Step 2: Respond to the Improved Question
Now answer the rephrased version thoroughly:

[Your detailed answer]

## Begin:
"""


class SelfAsk(ReasoningFramework):
    """Generate follow-up sub-questions, answer them, then solve the main question."""
    
    name: ClassVar[str] = "self_ask"
    description: ClassVar[str] = "Decompose by generating and answering follow-up sub-questions before the main answer"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.LOGIC, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["decomposition", "sub_questioning", "multi_hop_reasoning"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by asking and answering follow-up questions.

## Task
{task}

{self._format_section("Context", context)}## Self-Ask Process

### Do I need to ask follow-up questions?
[Yes/No — analyze if the question requires intermediate knowledge]

### Follow-up Questions and Answers

**Follow-up Q1**: [sub-question needed to answer the main question]
**A1**: [answer]

**Follow-up Q2**: [next sub-question, building on A1]
**A2**: [answer]

**Follow-up Q3**: [if needed]
**A3**: [answer]

### Final Answer
Combining the answers to all follow-up questions:
[Final answer to the original task]

## Begin Self-Ask:
"""
