"""PromptSmith MCP Server - Reasoning as a Service.

Provides reasoning framework selection and meta-prompt generation
for AI agents via Model Context Protocol.
"""

from contextlib import asynccontextmanager
from typing import Annotated, Optional

from fastmcp import FastMCP, Context

from promptsmith.config import settings
from promptsmith.domain import (
    FrameworkSelector,
    PromptBuilder,
    list_frameworks,
)
from promptsmith.domain.frameworks import FRAMEWORK_REGISTRY
from promptsmith.persistence import Storage, ReasoningLogCreate


# ============================================================================
# Dependencies & Lifespan
# ============================================================================

class Dependencies:
    """Dependency container for dependency injection."""
    def __init__(self):
        self.selector = FrameworkSelector()
        self.builder = PromptBuilder()
        self.storage = Storage(db_url=settings.DB_PATH)

    def initialize(self):
        """Initialize resources."""
        self.storage.initialize()

# Global container (can be overridden in tests)
_deps: Optional[Dependencies] = None

def get_dependencies() -> Dependencies:
    """Get the dependency container."""
    global _deps
    if _deps is None:
        _deps = Dependencies()
    return _deps

@asynccontextmanager
async def lifespan(server: FastMCP):
    """Manage server lifespan."""
    deps = get_dependencies()
    deps.initialize()
    yield

# Initialize MCP Server
mcp = FastMCP("PromptSmith", lifespan=lifespan)


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
def recommend_strategy(
    task: Annotated[str, "The task or question to analyze"],
    context: Annotated[str, "Additional context about the task"] = "",
) -> dict:
    """
    Analyze a task and recommend the optimal reasoning framework.
    
    Returns the detected category, complexity_score, recommended framework,
    and alternative options.
    """
    deps = get_dependencies()
    analysis = deps.selector.analyze(task, context)
    
    return {
        "category": analysis.category.value,
        "complexity": {
            "score": analysis.complexity_score,
            "level": analysis.complexity_level.value,
        },
        "recommended_framework": analysis.recommended_framework,
        "reasoning": analysis.reasoning,
        "alternatives": analysis.alternative_frameworks,
    }


@mcp.tool()
def generate_meta_prompt(
    task: Annotated[str, "The task or question to create a prompt for"],
    context: Annotated[str, "Additional context to include in the prompt"] = "",
    framework: Annotated[Optional[str], "Specific framework to use (optional, auto-selects if not provided)"] = None,
    persist: Annotated[bool, "Whether to log this generation for analytics"] = True,
) -> dict:
    """
    Generate an optimized meta-prompt for the given task.
    
    Analyzes the task, selects the best reasoning framework (or uses the specified one),
    and generates a structured prompt designed to elicit high-quality reasoning.
    """
    deps = get_dependencies()
    
    # Analyze task
    analysis = deps.selector.analyze(task, context)
    
    # Build prompt (use override framework if specified)
    result = deps.builder.build(
        task=task,
        context=context,
        framework_name=framework,
        analysis=analysis,
    )
    
    # Persist if requested
    log_id = None
    if persist:
        log_data = ReasoningLogCreate(
            task_input=task,
            context=context if context else None,
            detected_category=analysis.category.value,
            complexity_score=analysis.complexity_score,
            selected_framework=result.framework_used,
            meta_prompt_generated=result.meta_prompt,
        )
        log = deps.storage.create_log(log_data)
        log_id = str(log.id)
    
    return {
        "task_id": log_id,
        "framework_used": result.framework_used,
        "analysis": {
            "category": analysis.category.value,
            "complexity_score": analysis.complexity_score,
            "complexity_level": analysis.complexity_level.value,
        },
        "meta_prompt": result.meta_prompt,
    }


@mcp.tool()
def log_execution_feedback(
    task_id: Annotated[str, "The task ID from generate_meta_prompt"],
    feedback: Annotated[str, "Feedback about how well the prompt worked"],
) -> dict:
    """
    Log feedback about how a generated prompt performed.
    
    Used to track effectiveness and improve framework selection over time.
    """
    deps = get_dependencies()
    updated = deps.storage.update_feedback(task_id, feedback)
    
    if not updated:
        return {
            "success": False,
            "error": f"Task ID not found: {task_id}",
        }
    
    return {
        "success": True,
        "message": f"Feedback logged for task {task_id}",
    }


@mcp.tool()
def list_available_frameworks() -> dict:
    """
    List all available reasoning frameworks with their descriptions.
    
    Use this to understand what frameworks are available and when each is best used.
    """
    # This tool reads from static registry, valid to stay static or move to selector
    # For consistency, we can leave it as is since FRAMEWORK_REGISTRY is a constant
    frameworks = []
    for name, cls in FRAMEWORK_REGISTRY.items():
        frameworks.append({
            "name": name,
            "description": cls.description,
            "best_for": [cat.value for cat in cls.best_for],
            "complexity_threshold": cls.complexity_threshold,
        })
    
    return {
        "frameworks": frameworks,
        "count": len(frameworks),
    }


@mcp.tool()
def get_usage_stats() -> dict:
    """
    Get usage statistics for PromptSmith.

    Shows total prompts generated, distribution by framework and category,
    and average complexity scores.
    """
    deps = get_dependencies()
    return deps.storage.get_stats()


# ============================================================================
# MCP Resources (optional - for inspecting logs)
# ============================================================================

@mcp.resource("logs://recent")
def get_recent_logs() -> str:
    """Get the most recent reasoning logs."""
    deps = get_dependencies()
    logs = deps.storage.list_logs(limit=20)
    
    lines = ["# Recent Reasoning Logs\n"]
    for log in logs:
        lines.append(f"## {log.id}")
        lines.append(f"- **Task**: {log.task_input[:100]}...")
        lines.append(f"- **Category**: {log.detected_category}")
        lines.append(f"- **Framework**: {log.selected_framework}")
        lines.append(f"- **Complexity**: {log.complexity_score}")
        lines.append(f"- **Time**: {log.timestamp}")
        lines.append("")
    
    return "\n".join(lines)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

