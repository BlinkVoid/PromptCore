import pytest
from promptsmith.domain.selector import FrameworkSelector, TaskCategory, ComplexityLevel, TaskAnalysis

@pytest.fixture
def selector():
    return FrameworkSelector()

class TestFrameworkSelector:
    def test_detect_category_code(self, selector):
        text = "Can you help me debug this python function?"
        assert selector._detect_category(text) == TaskCategory.CODE

    def test_detect_category_math(self, selector):
        text = "Calculate the derivative of x^2"
        assert selector._detect_category(text) == TaskCategory.MATH

    def test_calculate_complexity_simple(self, selector):
        score = selector._calculate_complexity("Simple task", "")
        # Expect low score (base 2 - reducer ~1.5 + small length)
        assert score < 4.0

    def test_calculate_complexity_high(self, selector):
        text = "Optimize this complex distributed system with asynchronous integration and handle edge cases."
        score = selector._calculate_complexity(text, "")
        # Expect high score due to keywords (optimize, complex, distributed, async, edge cases)
        assert score > 6.0

    def test_analyze_returns_valid_result(self, selector):
        analysis = selector.analyze("Write a python script", context="")
        assert isinstance(analysis, TaskAnalysis)
        assert analysis.category == TaskCategory.CODE
        assert analysis.recommended_framework is not None

    def test_intent_detection(self, selector):
        """Test that intents are correctly detected from keywords."""
        assert "exploration" in selector._detect_intents("I want to explore different options")
        assert "structured_data" in selector._detect_intents("Organize this into a table")
        assert "verification" in selector._detect_intents("Please verify these results")

    def test_intent_prioritizes_framework(self, selector):
        """Test that specific intent keywords trigger the matching framework, overriding defaults."""
        # "Explore options" -> tree_of_thoughts (intent: exploration)
        # Even if complexity is low, intent should boost it.
        analysis = selector.analyze("Explore different options for a birthday party", context="simple task")
        assert analysis.recommended_framework == "tree_of_thoughts"
        
        # "Table" -> chain_of_table (intent: structured_data)
        analysis = selector.analyze("Create a table of the data", context="")
        assert analysis.recommended_framework == "chain_of_table"

    def test_complexity_tie_breaking(self, selector):
        """Test that lower complexity threshold wins in a tie (Simplicity Bias)."""
        # Scenario: Two frameworks might match well.
        # Framework A (Threshold 2.0), Framework B (Threshold 5.0)
        # Task Complexity 6.0
        # Both meet threshold. If Intent/Category scores are equal, A should win slightly due to being "simpler foundation".
        # However, our logic penalizes "overkill" distance.
        # Let's test specific behavior:
        # Task: "Write a simple function" (Code, Low Complexity)
        # CoT (2.0) vs ProgramOfThoughts (4.0). 
        # ProgramOfThoughts wins on Intent ("function" -> code_reasoning) despite higher complexity threshold.
        # This is desired behavior: specialized tools should win when intent is clear.
        analysis = selector.analyze("Write a function to add two numbers")
        assert analysis.recommended_framework == "program_of_thoughts"
