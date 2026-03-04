# PromptCore

**Reasoning as a Service** - A Capability-Level 0 MCP Server that provides intelligent reasoning framework selection and meta-prompt generation for AI agents.

## Purpose

PromptCore analyzes tasks, determines their complexity and category, and generates optimized "meta-prompts" using the most appropriate reasoning framework.

## Features

- 🧠 **40 Reasoning Frameworks**: Chain of Thought, Tree of Thoughts, ReAct, Reflexion, Graph of Thoughts, Program of Thoughts, and more
- 📊 **Intelligent Task Analysis**: Automatic category detection (code, math, logic, creative, research, data, planning) and complexity scoring (0–10)
- 🎯 **Framework Selection**: Heuristic-based selection of the optimal reasoning strategy
- 💾 **Persistence**: SQLite storage for reasoning traces and analytics
- 📈 **Usage Statistics**: Track framework usage and effectiveness

## Installation

```bash
git clone https://github.com/your-org/promptcore
cd promptcore
uv sync
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `recommend_strategy` | Analyze a task and recommend the optimal reasoning framework |
| `generate_meta_prompt` | Generate an optimized meta-prompt for a task |
| `log_execution_feedback` | Record feedback about prompt effectiveness |
| `list_available_frameworks` | List all available reasoning frameworks |
| `get_usage_stats` | Get usage statistics and analytics |

## Usage

### As MCP Server

Add to your MCP client configuration (e.g. `.mcp.json` in your project root):

```json
{
  "mcpServers": {
    "promptcore": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/promptcore", "python", "-m", "promptcore.main"],
      "env": {
        "PYTHONPATH": "/path/to/promptcore/src",
        "UV_LINK_MODE": "copy",
        "FASTMCP_SHOW_STARTUP_BANNER": "false"
      }
    }
  }
}
```

### Programmatic Usage

```python
from promptcore.domain import FrameworkSelector, PromptBuilder

# Analyze a task
selector = FrameworkSelector()
analysis = selector.analyze("Write a recursive function to calculate fibonacci numbers")

print(f"Category: {analysis.category}")               # code
print(f"Complexity: {analysis.complexity_score}")     # ~3.3
print(f"Framework: {analysis.recommended_framework}") # program_of_thoughts

# Generate a meta-prompt
builder = PromptBuilder()
result = builder.build(analysis.task, analysis=analysis)
print(result.meta_prompt)
```

## Reasoning Frameworks

40 frameworks across 8 categories, selected automatically based on task type and complexity.

| Framework | Best For | Complexity Threshold |
|-----------|----------|---------------------|
| Role Prompting | Creative, General, Research | 1.0 |
| Emotion Prompting | Creative, General | 1.0 |
| Rephrase and Respond | General, Research | 2.0 |
| Chain of Thought | Math, Logic, Code | 2.0 |
| System 2 Attention | Logic, Research, General | 3.0 |
| Thread of Thought | Research, Data, General | 3.0 |
| Tab-CoT | Data, Math, Logic | 3.0 |
| Directional Stimulus | Creative, General | 3.0 |
| Skeleton of Thought | Creative, General, Planning | 3.0 |
| Self-Calibration | Math, Logic, General | 3.0 |
| Chain of Density | Research, Data, General | 3.0 |
| Prompt Paraphrasing | General, Logic | 3.0 |
| Sim-to-M | Logic, General | 4.0 |
| Self-Ask | Research, Logic, General | 4.0 |
| Step Back | Research, Logic, General | 4.0 |
| Analogical | General, Creative, Code | 4.0 |
| Program of Thoughts | Math, Code, Data | 4.0 |
| Plan and Solve | Planning, Code, Math | 4.0 |
| Self-Consistency | Math, Logic | 4.0 |
| Self-Refine | Creative, Code, General | 4.0 |
| Chain of Table | Data | 4.0 |
| Least to Most | Code, Math, Planning | 5.0 |
| Contrastive CoT | Math, Logic, Code | 5.0 |
| Active Prompting | General, Research, Logic | 5.0 |
| Faithful CoT | Math, Logic, Code | 5.0 |
| Demonstration Ensembling | General, Data, Logic | 5.0 |
| Maieutic | Research, Logic, General | 5.0 |
| Chain of Verification | Research, General, Data | 5.0 |
| Reverse CoT | Math, Logic, Code | 5.0 |
| Buffer of Thoughts | General, Math, Code | 5.0 |
| Complexity-Based | Math, Logic | 6.0 |
| Tree of Thoughts | Creative, Planning, Research | 6.0 |
| Mixture of Reasoning | General, Research, Logic | 6.0 |
| Meta-CoT | Logic, Math, Research | 6.0 |
| Cumulative Reasoning | Logic, Math, Research | 6.0 |
| Recursion of Thought | Math, Code, Logic | 7.0 |
| ReAct | Research, Code, Data | 7.0 |
| Reflexion | Code, Math, Logic | 8.0 |
| Graph of Thoughts | Planning, Research, Logic | 8.0 |
| Reasoning via Planning | Planning, Logic, Code | 8.0 |

## Architecture

```
src/promptcore/
├── main.py              # MCP Server entry point
├── domain/
│   ├── frameworks.py    # 40 reasoning framework implementations
│   ├── selector.py      # Task analysis and framework selection
│   └── builder.py       # Meta-prompt assembly
├── persistence/
│   ├── models.py        # SQLAlchemy/Pydantic models
│   └── storage.py       # SQLite operations
└── utils/
    └── complexity.py    # Text complexity analysis
```

## Integration with Other Agents

PromptCore is designed to be called by other MCP-enabled agents.

```python
result = mcp_call("promptcore", "generate_meta_prompt", {
    "task": user_query,
    "context": relevant_context,
})
enhanced_response = llm.generate(result["meta_prompt"])
```

## License

MIT
