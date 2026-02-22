"""Prompt Builder - Assembles meta-prompts using selected frameworks."""

from pydantic import BaseModel, Field
from typing import Optional

from .frameworks import FRAMEWORK_REGISTRY, get_framework, ReasoningFramework
from .selector import TaskAnalysis


class GeneratedPrompt(BaseModel):
    """Result of prompt generation."""
    
    task: str = Field(..., description="Original task")
    framework_used: str = Field(..., description="Framework that generated this prompt")
    meta_prompt: str = Field(..., description="The generated meta-prompt")
    analysis: Optional[TaskAnalysis] = Field(None, description="Task analysis if available")


class PromptBuilder:
    """Builds optimized meta-prompts using reasoning frameworks."""
    
    def __init__(self):
        pass
    
    def build(
        self, 
        task: str, 
        context: str = "",
        framework_name: Optional[str] = None,
        analysis: Optional[TaskAnalysis] = None,
    ) -> GeneratedPrompt:
        """
        Build a meta-prompt for the given task.
        
        Args:
            task: The task/question to create a prompt for
            context: Additional context to include
            framework_name: Explicit framework to use (overrides analysis)
            analysis: Pre-computed task analysis (provides framework if not explicit)
        
        Returns:
            GeneratedPrompt with the assembled meta-prompt
        """
        # Determine which framework to use
        if framework_name:
            selected_framework = framework_name
        elif analysis:
            selected_framework = analysis.recommended_framework
        else:
            # Default to chain of thought
            selected_framework = "chain_of_thought"
        
        # Get framework class and instantiate
        framework_cls = get_framework(selected_framework)
        framework: ReasoningFramework = framework_cls()
        
        # Generate the prompt
        meta_prompt = framework.generate_prompt_template(task, context)
        
        return GeneratedPrompt(
            task=task,
            framework_used=selected_framework,
            meta_prompt=meta_prompt,
            analysis=analysis,
        )
    
    def build_with_analysis(
        self,
        analysis: TaskAnalysis,
        context: str = "",
        override_framework: Optional[str] = None,
    ) -> GeneratedPrompt:
        """
        Build a meta-prompt using an existing analysis.
        
        Args:
            analysis: Pre-computed task analysis
            context: Additional context
            override_framework: Use this framework instead of the recommended one
        
        Returns:
            GeneratedPrompt with the assembled meta-prompt
        """
        return self.build(
            task=analysis.task,
            context=context,
            framework_name=override_framework,
            analysis=analysis,
        )
    
    def build_custom(
        self,
        task: str,
        framework_name: str,
        context: str = "",
    ) -> GeneratedPrompt:
        """
        Build a meta-prompt with an explicitly specified framework.
        
        Args:
            task: The task to create a prompt for
            framework_name: Name of the framework to use
            context: Additional context
        
        Returns:
            GeneratedPrompt with the assembled meta-prompt
        """
        return self.build(
            task=task,
            context=context,
            framework_name=framework_name,
            analysis=None,
        )
    
    @staticmethod
    def available_frameworks() -> list[str]:
        """List all available framework names."""
        return list(FRAMEWORK_REGISTRY.keys())
