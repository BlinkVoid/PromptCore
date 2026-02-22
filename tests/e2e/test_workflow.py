import pytest
import datetime
from unittest.mock import MagicMock
from promptsmith.main import recommend_strategy, generate_meta_prompt
from promptsmith.domain.selector import TaskAnalysis, TaskCategory, ComplexityLevel
from promptsmith.domain.builder import GeneratedPrompt

# In a real E2E test, we might use a separate process or the fastmcp test client.
# Since fastmcp's test client details aren't fully exposed here, we will simulate
# the "User Scenario" by invoking the tools in sequence as an agent would,
# but still mocking the internal logic to keep it deterministic (Component-Level E2E).

class TestWorkflowScenario:
    def test_complete_reasoning_workflow(self, override_deps):
        """
        Scenario: User wants to generate a prompt for a complex coding task.
        1. User asks for strategy recommendation.
        2. User accepts recommendation and asks for the prompt.
        3. User provides feedback on the result.
        """
        
        # ------------------------------------------------------------------
        # Step 1: Recommend Strategy
        # ------------------------------------------------------------------
        task_text = "Refactor the legacy authentication system to use OAuth2."
        context_text = "Must support Google and GitHub login."
        
        # Mock analysis result
        override_deps.selector.analyze.return_value = TaskAnalysis(
            task=task_text,
            category=TaskCategory.CODE,
            complexity_score=7.5,
            complexity_level=ComplexityLevel.HIGH,
            recommended_framework="chain_of_thought",
            reasoning="Authenticaion is complex.",
            alternative_frameworks=["tree_of_thoughts"]
        )
        
        strategy = recommend_strategy(task=task_text, context=context_text)
        
        assert strategy["category"] == "code"
        assert strategy["recommended_framework"] == "chain_of_thought"
        # In a real scenario, the Agent would "read" this output.
        
        # ------------------------------------------------------------------
        # Step 2: Generate Meta-Prompt
        # ------------------------------------------------------------------
        # Mock builder result
        override_deps.builder.build.return_value = GeneratedPrompt(
            task=task_text,
            framework_used="chain_of_thought",
            meta_prompt="Context: ... Instructions: Think step-by-step..."
        )
        
        # Mock storage creation (simulate DB returning an ID)
        mock_log = MagicMock()
        mock_log.id = "task-uuid-1234"
        override_deps.storage.create_log.return_value = mock_log
        
        result = generate_meta_prompt(
            task=task_text, 
            context=context_text,
            framework="chain_of_thought" # User chooses the recommended one
        )
        
        assert result["task_id"] == "task-uuid-1234"
        assert "Think step-by-step" in result["meta_prompt"]
        
        # ------------------------------------------------------------------
        # Step 3: Log Feedback (Post-Execution)
        # ------------------------------------------------------------------
        # Mock storage update
        # update_feedback returns the log if successful, None if failed
        override_deps.storage.update_feedback.return_value = MagicMock(execution_feedback="Great prompt!")
        
        # We need to import this tool locally as it wasn't imported in top level
        from promptsmith.main import log_execution_feedback
        
        feedback_result = log_execution_feedback(
            task_id="task-uuid-1234",
            feedback="Great prompt! The agent handled the oauth flow perfectly."
        )
        
        assert feedback_result["success"] is True
        
        # Verify the entire chain of calls
        override_deps.selector.analyze.assert_called()
        override_deps.builder.build.assert_called()
        override_deps.storage.create_log.assert_called_once()
        override_deps.storage.update_feedback.assert_called_with("task-uuid-1234", "Great prompt! The agent handled the oauth flow perfectly.")
