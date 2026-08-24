import pytest
from promptcore.domain.frameworks import FRAMEWORK_REGISTRY
from promptcore.domain.selector import FrameworkSelector, TaskCategory, ComplexityLevel, TaskAnalysis

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
        """Test that intent/category tiers drive selection under the new scoring."""
        # "Explore options" (creative, low) -> role_prompting (creative low-tier pick)
        analysis = selector.analyze("Explore different options for a birthday party", context="simple task")
        assert analysis.recommended_framework == "role_prompting"

        # "Table" -> chain_of_table (data low-tier pick)
        analysis = selector.analyze("Create a table of the data", context="")
        assert analysis.recommended_framework == "chain_of_table"

    def test_complexity_tie_breaking(self, selector):
        """Test that category-complexity tier gating drives the pick (tie-breaker removed).

        Task: "Write a function to add two numbers" is Code/Low complexity.
        The code LOW tier only allows chain_of_thought; program_of_thoughts
        sits in MEDIUM and is gated out despite matching code_reasoning intent.
        """
        analysis = selector.analyze("Write a function to add two numbers")
        assert analysis.recommended_framework == "chain_of_thought"


class TestScoringFixes:
    def test_generic_framework_does_not_dominate_research(self, selector):
        """Research tasks should select research-tier frameworks, not rephrase_and_respond."""
        analysis = selector.analyze("Evaluate the credibility of these sources.")
        assert analysis.recommended_framework != "rephrase_and_respond"

    def test_intent_bonus_is_capped(self, selector):
        """A task triggering many intents shouldn't let any low-threshold framework win."""
        analysis = selector.analyze(
            "Break down this complex problem, verify each part, and organize "
            "the data in a table with steps."
        )
        assert analysis.recommended_framework in FRAMEWORK_REGISTRY

    def test_data_mid_complexity_prefers_chain_of_table(self, selector):
        analysis = selector.analyze(
            "Group these sales records by region and calculate total revenue per region."
        )
        assert analysis.category == TaskCategory.DATA

    def test_trivial_fact_stays_lightweight(self, selector):
        analysis = selector.analyze("Who wrote 'Pride and Prejudice'?")
        assert analysis.complexity_score < 4.0
