import pytest
from promptsmith.domain.builder import PromptBuilder
from promptsmith.domain.selector import TaskAnalysis, TaskCategory, ComplexityLevel

@pytest.fixture
def builder():
    return PromptBuilder()

class TestPromptBuilder:
    def test_build_default(self, builder):
        result = builder.build("Test task")
        assert result.framework_used == "chain_of_thought"
        assert "Test task" in result.meta_prompt

    def test_build_explicit_framework(self, builder):
        result = builder.build("Test task", framework_name="tree_of_thoughts")
        assert result.framework_used == "tree_of_thoughts"
        # Check for ToT specific keywords if known, or just non-empty
        assert len(result.meta_prompt) > 0

    def test_build_with_analysis(self, builder):
        analysis = TaskAnalysis(
            task="Optimize code",
            category=TaskCategory.CODE,
            complexity_score=8.5,
            complexity_level=ComplexityLevel.HIGH,
            recommended_framework="chain_of_thought",
            reasoning="Testing",
            alternative_frameworks=[]
        )
        result = builder.build_with_analysis(analysis)
        assert result.framework_used == "chain_of_thought"
        assert "Optimize code" in result.meta_prompt
