"""Decomposition Frameworks.

Techniques that break complex problems into simpler sub-problems
and solve them individually or in sequence.

References:
- Yao et al. 2023 (Tree of Thoughts)
- Zhou et al. 2022 (Least-to-Most)
- Chen et al. 2023 (Program-of-Thoughts)
- Ning et al. 2023 (Skeleton-of-Thought)
- Wang et al. 2023 (Plan-and-Solve)
- Lyu et al. 2023 (Faithful CoT)
- Lee & Kim 2023 (Recursion-of-Thought)
"""

from typing import ClassVar, Optional

from .base import ReasoningFramework, TaskCategory


class TreeOfThoughts(ReasoningFramework):
    """Explore multiple solution paths for complex/creative problems."""
    
    name: ClassVar[str] = "tree_of_thoughts"
    description: ClassVar[str] = "Explore multiple solution branches, evaluate each, and select the best path"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.PLANNING, TaskCategory.RESEARCH]
    capabilities: ClassVar[list[str]] = ["exploration", "branching", "alternatives", "brainstorming"]
    complexity_threshold: ClassVar[float] = 6.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are exploring a complex problem that benefits from considering multiple approaches.

## Task
{task}

{self._format_section("Context", context)}## Tree of Thoughts Process

### Phase 1: Generate Candidate Approaches
Brainstorm 3 distinct approaches to this problem. For each:
- **Approach A**: [describe approach]
- **Approach B**: [describe approach]  
- **Approach C**: [describe approach]

### Phase 2: Evaluate Each Branch
For each approach, think 2-3 steps ahead:
- What are the immediate next steps?
- What challenges or dead-ends might arise?
- How promising is this path? (rate 1-10)

### Phase 3: Select Best Path
Based on your evaluation:
- Which approach has the best promise-to-effort ratio?
- Are there elements from other approaches worth combining?

### Phase 4: Execute Selected Approach
Develop your chosen solution in detail.

## Begin Exploration:
"""


class LeastToMost(ReasoningFramework):
    """Decompose complex problems into simpler subproblems."""
    
    name: ClassVar[str] = "least_to_most"
    description: ClassVar[str] = "Break down complex problems into simpler subproblems, solve bottom-up"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CODE, TaskCategory.MATH, TaskCategory.PLANNING]
    capabilities: ClassVar[list[str]] = ["decomposition", "simplification", "bottom_up"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a complex problem by breaking it into simpler subproblems.

## Task
{task}

{self._format_section("Context", context)}## Least-to-Most Decomposition

### Phase 1: Decompose
Break the main problem into subproblems, ordered from simplest to most complex:

1. **Subproblem 1** (simplest): [describe]
2. **Subproblem 2** (builds on 1): [describe]
3. **Subproblem 3** (builds on 1,2): [describe]
...continue until the final problem is the original task

### Phase 2: Solve Bottom-Up
Solve each subproblem in order, using solutions from previous steps:

**Solving Subproblem 1:**
[solution]

**Solving Subproblem 2** (using solution 1):
[solution]

...continue

### Phase 3: Synthesize Final Answer
Combine all subproblem solutions into the complete answer.

## Begin Decomposition:
"""


class ProgramOfThoughts(ReasoningFramework):
    """Generate executable code as reasoning steps."""
    
    name: ClassVar[str] = "program_of_thoughts"
    description: ClassVar[str] = "Express reasoning as executable code, using a code interpreter for precise computation"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.CODE, TaskCategory.DATA]
    capabilities: ClassVar[list[str]] = ["code_reasoning", "computation", "precision", "executable_logic"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by expressing your reasoning as executable code.

## Task
{task}

{self._format_section("Context", context)}## Program-of-Thoughts Process

### Step 1: Formalize the Problem
Translate the problem into variables, constraints, and operations:
- **Inputs**: [define variables]
- **Operations needed**: [list computations]
- **Expected output**: [describe]

### Step 2: Write Reasoning as Code
```python
# Step-by-step computation
# [Your code expressing the reasoning logic]
```

### Step 3: Trace Execution
Walk through the code mentally, showing intermediate values:
- After line X: variable = value
- After line Y: variable = value
- ...

### Final Answer
The result of executing the program: [answer]

## Begin Program Reasoning:
"""


class SkeletonOfThought(ReasoningFramework):
    """Outline a skeleton answer, then fill in details in parallel."""
    
    name: ClassVar[str] = "skeleton_of_thought"
    description: ClassVar[str] = "First create an answer skeleton, then elaborate each part independently"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.CREATIVE, TaskCategory.GENERAL, TaskCategory.PLANNING]
    capabilities: ClassVar[list[str]] = ["outlining", "parallel_elaboration", "structure_first"]
    complexity_threshold: ClassVar[float] = 3.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem by first creating an outline, then elaborating each point.

## Task
{task}

{self._format_section("Context", context)}## Skeleton-of-Thought Process

### Phase 1: Create Skeleton
Outline the main points/sections of your answer (skeleton only, no details):

1. [Point/Section 1 — one line summary]
2. [Point/Section 2 — one line summary]
3. [Point/Section 3 — one line summary]
...

### Phase 2: Elaborate Each Point
Now fill in each skeleton point with full detail:

**1. [Point 1]**
[Detailed elaboration]

**2. [Point 2]**
[Detailed elaboration]

**3. [Point 3]**
[Detailed elaboration]

### Final Assembled Answer
[Combine all elaborated points into a cohesive response]

## Begin Skeleton Construction:
"""


class PlanAndSolve(ReasoningFramework):
    """Understand the problem, devise a plan, then execute step by step."""
    
    name: ClassVar[str] = "plan_and_solve"
    description: ClassVar[str] = "First understand the problem and create a plan, then execute the plan step by step"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.PLANNING, TaskCategory.CODE, TaskCategory.MATH]
    capabilities: ClassVar[list[str]] = ["planning", "structured_execution", "organized_solving"]
    complexity_threshold: ClassVar[float] = 4.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""Let's first understand the problem and devise a plan to solve it. Then, let's carry out the plan and solve the problem step by step.

## Task
{task}

{self._format_section("Context", context)}## Plan-and-Solve Process

### Step 1: Understand the Problem
- **What is being asked**: [restate clearly]
- **Given information**: [list all inputs/constraints]
- **Expected output format**: [describe]

### Step 2: Devise a Plan
Create a numbered plan of action:
1. [First action]
2. [Second action]
3. [Third action]
...

### Step 3: Execute the Plan
Follow your plan step by step:

**Executing Step 1**: [work and result]
**Executing Step 2**: [work and result]
**Executing Step 3**: [work and result]

### Final Answer
[Answer derived from executing the plan]

## Begin Planning:
"""


class FaithfulCoT(ReasoningFramework):
    """CoT with interleaved natural language and symbolic/code reasoning."""
    
    name: ClassVar[str] = "faithful_cot"
    description: ClassVar[str] = "Interleave natural language reasoning with symbolic/code execution for faithful results"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.LOGIC, TaskCategory.CODE]
    capabilities: ClassVar[list[str]] = ["symbolic_reasoning", "code_verification", "faithful_computation"]
    complexity_threshold: ClassVar[float] = 5.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using both natural language reasoning and symbolic/code verification.

## Task
{task}

{self._format_section("Context", context)}## Faithful Chain-of-Thought Process

### Reasoning Step 1
**Natural Language**: [Explain what you're doing and why]
**Symbolic/Code**:
```python
# Formal verification of this step
```
**Result**: [outcome]

### Reasoning Step 2
**Natural Language**: [Next reasoning step]
**Symbolic/Code**:
```python
# Formal verification
```
**Result**: [outcome]

### Continue until solved...

### Final Verification
**Natural Language Conclusion**: [your answer in words]
**Symbolic Verification**: [code that confirms the answer]

## Begin Faithful Reasoning:
"""


class RecursionOfThought(ReasoningFramework):
    """Recursively delegate complex sub-problems to fresh reasoning contexts."""
    
    name: ClassVar[str] = "recursion_of_thought"
    description: ClassVar[str] = "When encountering a complex sub-problem, recursively spawn a fresh reasoning context to solve it"
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.MATH, TaskCategory.CODE, TaskCategory.LOGIC]
    capabilities: ClassVar[list[str]] = ["recursive_reasoning", "sub_problem_delegation", "depth_handling"]
    complexity_threshold: ClassVar[float] = 7.0
    
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        return f"""You are solving a problem using recursive reasoning — delegating complex sub-problems to fresh reasoning contexts.

## Task
{task}

{self._format_section("Context", context)}## Recursion-of-Thought Process

### Main Problem Analysis
Break down the problem. If any sub-problem is complex, mark it for recursive solving:

1. [Sub-problem 1] — Complexity: [simple/complex]
2. [Sub-problem 2] — Complexity: [simple/complex]
3. [Sub-problem 3] — Complexity: [simple/complex]

### Recursive Solving
For each complex sub-problem, solve it as if it were a fresh, standalone problem:

**=== RECURSIVE CALL: Sub-problem N ===**
**Problem**: [restate the sub-problem clearly]
**Solution approach**: [full reasoning for just this sub-problem]
**Result**: [answer]
**=== END RECURSIVE CALL ===**

### Combine Results
Insert all recursive results back into the main problem:
[Final combined solution]

## Begin Recursive Reasoning:
"""
