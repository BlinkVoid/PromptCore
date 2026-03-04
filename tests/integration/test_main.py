import pytest
from unittest.mock import MagicMock
from promptcore.main import recommend_strategy, generate_meta_prompt
from promptcore.domain.selector import TaskAnalysis, TaskCategory, ComplexityLevel
from promptcore.domain.builder import GeneratedPrompt
from promptcore.persistence import ReasoningLog

class TestMainIntegration:
    def test_recommend_strategy(self, override_deps):
        # Setup mock behavior
        analysis = TaskAnalysis(
            task="Test",
            category=TaskCategory.CODE,
            complexity_score=5.0,
            complexity_level=ComplexityLevel.MEDIUM,
            recommended_framework="chain_of_thought",
            reasoning="Reason",
            alternative_frameworks=[]
        )
        override_deps.selector.analyze.return_value = analysis
        
        from uuid import uuid4
        from datetime import datetime
        
        # Call tool directly (fastmcp 3.x no longer uses .fn wrapper)
        result = recommend_strategy("Test task")
        
        # Verify result structure
        assert result["category"] == "code"
        assert result["complexity"]["score"] == 5.0
        assert result["recommended_framework"] == "chain_of_thought"
        
        # Verify dependency interaction
        override_deps.selector.analyze.assert_called_once()

    def test_generate_meta_prompt(self, override_deps):
        # Setup mock behavior
        analysis = TaskAnalysis(
            task="Test",
            category=TaskCategory.CODE,
            complexity_score=5.0,
            complexity_level=ComplexityLevel.MEDIUM,
            recommended_framework="chain_of_thought",
            reasoning="Reason",
            alternative_frameworks=[]
        )
        override_deps.selector.analyze.return_value = analysis
        
        gen_prompt = GeneratedPrompt(
            task="Test",
            framework_used="chain_of_thought",
            meta_prompt="Generated Prompt"
        )
        override_deps.builder.build.return_value = gen_prompt
        
        from uuid import uuid4
        from datetime import datetime
        
        mock_log = ReasoningLog(
            id=uuid4(),
            timestamp=datetime.utcnow(),
            task_input="Test",
            detected_category="code",
            complexity_score=5.0,
            selected_framework="chain_of_thought",
            meta_prompt_generated="Generated Prompt"
        )
        override_deps.storage.create_log.return_value = mock_log
        
        # Call tool directly (fastmcp 3.x no longer uses .fn wrapper)
        result = generate_meta_prompt("Test task")
        
        # Verify
        assert result["task_id"] == str(mock_log.id)
        assert result["meta_prompt"] == "Generated Prompt"
        
        # Verify storage call
        override_deps.storage.create_log.assert_called_once()
