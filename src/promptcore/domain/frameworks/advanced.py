"""Advanced and Agent-Adjacent Frameworks.

Techniques that go beyond linear reasoning, incorporating
graph structures, planning algorithms, density operations,
and reusable thought templates.

References:
- Yao et al. 2022 (ReAct)
- Besta et al. 2023 (Graph of Thoughts)
- Hao et al. 2023 (Reasoning via Planning)
- Adams et al. 2023 (Chain of Density)
- Yang et al. 2024 (Buffer of Thoughts)
- Wang et al. 2023 (Chain of Table)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class ReAct(ReasoningFramework):
    """Reason, Act, Observe loop for tasks requiring tool usage."""
    
    name: ClassVar[str] = "react"
    description: ClassVar[str] = "Interleaved reasoning, action execution, and observation loop"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.CODE, TaskCategory.DATA]
    capabilities: ClassVar[list[str]] = ["tool_use", "action_execution", "interactive", "observation"]
    complexity_threshold: ClassVar[float] = 7.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by reasoning, acting (using tools), and observing results.

## Task
{task}

{self._format_section("Context", context)}## ReAct Process

Follow this loop until the task is complete:

1. **Thought**: Reason about what needs to be done next.
2. **Action**: Select a tool/action to perform.
3. **Action Input**: Provide specific input for the action.
4. **Observation**: Review the output of the action.

Repeat as needed.

### Example Sequence
**Thought**: I need to find the user's location.
**Action**: lookup_user_location
**Action Input**: {{"user_id": "123"}}
**Observation**: Location: "San Francisco, CA"
**Thought**: Now I can check the weather there.
...

## Begin ReAct Loop:
"""


class GraphOfThoughts(ReasoningFramework):
    """Non-linear graph reasoning with merge and backtrack operations."""
    
    name: ClassVar[str] = "graph_of_thoughts"
    description: ClassVar[str] = "Model reasoning as a graph — allowing branching, merging, and backtracking between thoughts"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.PLANNING, TaskCategory.RESEARCH, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["graph_reasoning", "merging", "backtracking", "non_linear"]
    complexity_threshold: ClassVar[float] = 8.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a complex problem using graph-structured reasoning where thoughts can branch, merge, and backtrack.

## Task
{task}

{self._format_section("Context", context)}## Graph of Thoughts Process

### Node 1 (Root): Problem Understanding
[Understand the problem]

### Branch A: [Approach 1]
**Node A1**: [first thought along this path]
**Node A2**: [next thought building on A1]

### Branch B: [Approach 2]
**Node B1**: [first thought along this path]
**Node B2**: [next thought building on B1]

### Merge Node (A + B → M1)
Combine insights from Branch A and Branch B:
**Node M1**: [merged insight that wouldn't be possible from either branch alone]

### Backtrack Check
Should we revisit any node? Did any branch reveal a flaw in an earlier assumption?
- If yes: [describe the backtrack and corrected reasoning]
- If no: Continue forward

### Convergence Node
**Final synthesis**: [answer derived from the full thought graph]

## Begin Graph Reasoning:
"""


class ReasoningViaPlanning(ReasoningFramework):
    """Use the LLM as a world model with MCTS-style planning."""
    
    name: ClassVar[str] = "reasoning_via_planning"
    description: ClassVar[str] = "Use the LLM as a world model, simulating actions and outcomes like Monte Carlo Tree Search"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.PLANNING, TaskCategory.LOGIC, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["planning", "simulation", "lookahead", "strategic"]
    complexity_threshold: ClassVar[float] = 8.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by simulating different action sequences and evaluating their outcomes.

## Task
{task}

{self._format_section("Context", context)}## Reasoning via Planning (MCTS-style)

### State 0: Current Situation
[Describe the current state of the problem]

### Available Actions
List possible next actions:
1. [Action A]
2. [Action B]
3. [Action C]

### Simulation: Action A
**Predicted state after A**: [simulate the outcome]
**Quality score**: [1-10, how good is this state?]
**Further actions available**: [what can we do next?]

### Simulation: Action B
**Predicted state after B**: [simulate the outcome]
**Quality score**: [1-10]
**Further actions available**: [what can we do next?]

### Simulation: Action C
**Predicted state after C**: [simulate the outcome]
**Quality score**: [1-10]
**Further actions available**: [what can we do next?]

### Best Path Selection
Based on simulated outcomes, the optimal action sequence is:
1. [Best first action] → 2. [Best second action] → ...

### Execute Optimal Plan
[Carry out the selected plan and produce the final answer]

## Begin Planning:
"""


class ChainOfDensity(ReasoningFramework):
    """Iteratively densify summaries with more information."""
    
    name: ClassVar[str] = "chain_of_density"
    description: ClassVar[str] = "Iteratively create denser, more information-rich summaries without increasing length"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.RESEARCH, TaskCategory.DATA, TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = ["summarization", "densification", "information_compression"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are creating a progressively denser summary/response.

## Task
{task}

{self._format_section("Context", context)}## Chain of Density Process

### Iteration 1: Initial Summary
Write an initial response that covers the main points but may be sparse on details:
[Initial version — ~100 words]

**Missing entities/concepts**: [list 1-3 important things not yet covered]

### Iteration 2: Denser Version
Rewrite to incorporate the missing entities WITHOUT increasing length significantly:
[Denser version — same ~100 words but with more information packed in]

**Missing entities/concepts**: [list 1-3 more things not yet covered]

### Iteration 3: Maximum Density
Final rewrite — pack in as much relevant information as possible while remaining fluent:
[Maximum density version — same length, maximum information]

### Final Output
[The densest, most informative version]

## Begin Density Iteration:
"""


class BufferOfThoughts(ReasoningFramework):
    """Use a library of reusable thought templates for common problem patterns."""
    
    name: ClassVar[str] = "buffer_of_thoughts"
    description: ClassVar[str] = "Draw from a meta-buffer of reusable thought templates matched to the problem type"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL, TaskCategory.MATH, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["template_reuse", "pattern_library", "efficient_reasoning"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by first identifying which known reasoning template best fits, then applying it.

## Task
{task}

{self._format_section("Context", context)}## Buffer of Thoughts Process

### Step 1: Problem Distillation
Distill the core structure of this problem:
- **Problem type**: [e.g., optimization, classification, search, construction, proof]
- **Key pattern**: [e.g., divide-and-conquer, greedy, constraint satisfaction]

### Step 2: Template Selection
From your knowledge base, select the most relevant thought template:
- **Template**: [name the reasoning pattern]
- **Why it fits**: [explain the match]
- **Template structure**:
  1. [Step 1 of the template]
  2. [Step 2 of the template]
  3. [Step 3 of the template]

### Step 3: Instantiate Template
Apply the selected template to this specific problem:

**Applying Step 1**: [instantiated for this problem]
**Applying Step 2**: [instantiated for this problem]
**Applying Step 3**: [instantiated for this problem]

### Final Answer
[Answer derived from the instantiated template]

## Begin Template Reasoning:
"""


class ChainOfTable(ReasoningFramework):
    """Structured tabular reasoning for data-centric problems."""
    
    name: ClassVar[str] = "chain_of_table"
    description: ClassVar[str] = "Use dynamic table operations to organize, transform, and analyze data"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.DATA]
    capabilities: ClassVar[list[str]] = ["structured_data", "tabular_reasoning", "comparison", "aggregation"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a data-centric problem using structured table operations.

## Task
{task}

{self._format_section("Context", context)}## Chain of Table Process

### Step 1: Data Inventory
List all data elements involved. Create an initial table representation:
```
| Column 1 | Column 2 | ... |
|----------|----------|-----|
| ...      | ...      | ... |
```

### Step 2: Required Transformations
Identify what operations are needed:
- [ ] Filter rows (by condition)
- [ ] Select/project columns
- [ ] Sort/order data
- [ ] Aggregate (sum, count, avg)
- [ ] Join with other data
- [ ] Derive new columns

### Step 3: Execute Operations
Apply each transformation step-by-step, showing the intermediate table state.

### Step 4: Extract Answer
From the final table state, extract the answer to the original question.

## Begin Table Reasoning:
"""
