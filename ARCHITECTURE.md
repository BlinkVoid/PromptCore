# Architecture - PromptCore

**PromptCore** is designed as a standalone Capability-Level 0 MCP Server providing "Reasoning as a Service".

## Core Design

The system follows a clean architecture pattern with distinct layers:

1.  **Interface Layer (`main.py`)**: Exposes functionality via the Model Context Protocol (MCP).
2.  **Domain Layer (`domain/`)**: Contains the core business logic, including reasoning frameworks and selector strategies.
3.  **Persistence Layer (`persistence/`)**: Handles data storage and retrieval.
4.  **Utils (`utils/`)**: Helper functions and common utilities.

## Directory Structure

```
PromptCore/
├── src/
│   └── promptcore/
│       ├── __init__.py
│       ├── main.py              # MCP Server Entry
│       ├── domain/              # Core Logic
│       │   ├── frameworks.py    # Registry (ToT, CoT, Table, etc.)
│       │   ├── selector.py      # Heuristic/ML Selector
│       │   └── builder.py       # Prompt Assembler
│       ├── persistence/
│       │   ├── models.py        # SQLAlchemy/Pydantic Models
│       │   └── storage.py       # DB Operations (SQLite)
│       └── utils/
│           └── complexity.py    # Text analysis metrics
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── CONTRIBUTING.md
```

## Component Details

### 1. Framework Registry (`domain/frameworks.py`)

The registry manages the available reasoning strategies. Each framework implements a common interface for generating meta-prompts.

**40 frameworks across 8 categories.** Each implements a common interface for generating meta-prompts. Examples include:
-   **ChainOfThought**: Linear step-by-step reasoning (complexity ≥ 2.0)
-   **ProgramOfThoughts**: Reasoning expressed as executable code (complexity ≥ 4.0)
-   **TreeOfThoughts**: BFS/DFS exploration for creative and planning tasks (complexity ≥ 6.0)
-   **ReAct**: Interleaved reasoning, action, and observation loop (complexity ≥ 7.0)
-   **Reflexion**: Self-critique and refinement cycle (complexity ≥ 8.0)
-   **GraphOfThoughts**: Graph-based reasoning with branching and backtracking (complexity ≥ 8.0)
-   ...and 34 more. See `domain/frameworks.py` for the full registry.

### 2. Selector Logic (`domain/selector.py`)

The `FrameworkSelector` analyzes incoming tasks to recommend the optimal strategy.

**Logic Flow:**
1.  **Categorization**: Classifies task into Code, Math, Logic, Creative, Research, Data, Planning, or General.
2.  **Complexity Scoring**: Calculates a score (0-10) based on token count, ambiguity, and constraints.
3.  **Mapping**: Applies rules to map category and complexity to a specific framework (e.g., High Complexity + Data -> ChainOfTable).

### 3. Persistence (`persistence/`)

Stores reasoning traces and usage statistics using SQLite.

**Data Model (`ReasoningLog`):**
-   `id`: Unique identifier
-   `task_input`: Original user task
-   `detected_category`: Classified category
-   `complexity_score`: Calculated complexity
-   `selected_framework`: Recommended framework
-   `meta_prompt_generated`: The final prompt output
-   `execution_feedback`: Optional feedback on effectiveness

### 4. Meta-Prompt Construction (`domain/builder.py`)

The `PromptBuilder` assembles the final prompt by combining the selected framework's template with the user's task and context.
