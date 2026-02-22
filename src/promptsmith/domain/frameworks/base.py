"""Reasoning Framework Base Classes and Registry.

Defines the base class, task categories, and auto-registration
mechanism used by all framework submodules.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar, Optional
from pydantic import BaseModel


class TaskCategory(str, Enum):
    """Categories of tasks for framework selection."""
    CODE = "code"
    MATH = "math"
    LOGIC = "logic"
    CREATIVE = "creative"
    DATA = "data"
    RESEARCH = "research"
    PLANNING = "planning"
    GENERAL = "general"


# Framework Registry - Populated automatically via __init_subclass__
FRAMEWORK_REGISTRY: dict[str, type["ReasoningFramework"]] = {}


class ReasoningFramework(BaseModel, ABC):
    """Base class for all reasoning frameworks with auto-registration."""
    
    name: ClassVar[str]
    description: ClassVar[str]
    best_for: ClassVar[list[TaskCategory]]
    capabilities: ClassVar[list[str]]  # Core capabilities this framework provides
    complexity_threshold: ClassVar[float]  # Min complexity to use (0-10)
    
    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses."""
        super().__init_subclass__(**kwargs)
        # Only register if all required ClassVars are set (basic check)
        if hasattr(cls, "name") and cls.name:
            FRAMEWORK_REGISTRY[cls.name] = cls

    @abstractmethod
    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        """Generate a meta-prompt using this framework's structure.
        
        Args:
            task: The main task to solve.
            context: Additional context or background info.
            examples: Optional list of few-shot examples to include.
        """
        pass
    
    @classmethod
    def get_info(cls) -> dict:
        """Return framework metadata."""
        return {
            "name": cls.name,
            "description": cls.description,
            "best_for": [cat.value for cat in cls.best_for],
            "capabilities": cls.capabilities,
            "complexity_threshold": cls.complexity_threshold,
        }
    
    def _format_section(self, title: str, content: str) -> str:
        """Helper to format a section if content exists."""
        if not content:
            return ""
        return f"## {title}\n{content}\n\n"


def get_framework(name: str) -> type[ReasoningFramework]:
    """Get a framework class by name."""
    if name not in FRAMEWORK_REGISTRY:
        raise ValueError(f"Unknown framework: {name}. Available: {list(FRAMEWORK_REGISTRY.keys())}")
    return FRAMEWORK_REGISTRY[name]


def list_frameworks() -> list[dict]:
    """List all available frameworks with their metadata."""
    return [cls.get_info() for cls in FRAMEWORK_REGISTRY.values()]
