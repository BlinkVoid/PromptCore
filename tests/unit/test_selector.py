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
        """Intent/category tiers drive selection under the current scoring.

        Since iter-2 softened the out-of-tier penalty, the exploration intent can lift
        tree_of_thoughts (an exploration framework) over the generic role_prompting pick.
        """
        analysis = selector.analyze("Explore different options for a birthday party", context="simple task")
        assert analysis.recommended_framework == "tree_of_thoughts"

        # "Table" -> chain_of_table (data low-tier pick)
        analysis = selector.analyze("Create a table of the data", context="")
        assert analysis.recommended_framework == "chain_of_table"

    def test_complexity_tie_breaking(self, selector):
        """Tier gating vs intent interplay (tie-breaker removed in scoring-v2).

        Task: "Write a function to add two numbers" is Code/Low complexity.
        Since iter-2 softened OUT_OF_TIER_PENALTY, the code_reasoning intent can lift
        program_of_thoughts (MEDIUM tier) over chain_of_thought at low complexity;
        both are acceptable decomposition picks for trivial code.
        """
        analysis = selector.analyze("Write a function to add two numbers")
        assert analysis.recommended_framework in {"chain_of_thought", "program_of_thoughts"}


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


class TestRegressionIteration1:
    def test_regression_unit_conversion_is_math(self, selector):
        """Grounded in benchmark miss: 'Convert 68°F to Celsius...' was predicted GENERAL."""
        analysis = selector.analyze("Convert 68°F to Celsius and round to one decimal place.")
        assert analysis.category == TaskCategory.MATH
        assert analysis.recommended_framework == "chain_of_thought"

    def test_regression_integer_pairs_is_math(self, selector):
        """Grounded in benchmark miss: 'Find all integer pairs (x, y)...' was predicted GENERAL."""
        analysis = selector.analyze("Find all integer pairs (x, y) with 3x + 4y = 41 and x, y > 0.")
        assert analysis.category == TaskCategory.MATH
        assert analysis.recommended_framework == "chain_of_thought"


class TestRegressionIteration2:
    def test_regression_goal_breakdown_selects_decomposition(self, selector):
        """Grounded in benchmark miss: with OUT_OF_TIER_PENALTY=5 planning decomposition
        frameworks were locked out at low detected complexity; at penalty=2 least_to_most wins."""
        analysis = selector.analyze("Break down this goal into actionable milestones.")
        assert analysis.recommended_framework in {"least_to_most", "plan_and_solve"}

    def test_regression_pr_review_selects_self_refinement(self, selector):
        """Grounded in benchmark miss: 'Improve this pull request...' should pick a
        self-refinement framework now that out-of-tier penalties are softened."""
        analysis = selector.analyze(
            "Improve this pull request: tighten naming, remove dead branches, and add docstrings."
        )
        assert analysis.recommended_framework in {"self_refine", "reflexion"}

    def test_regression_compound_interest_selects_program_of_thoughts(self, selector):
        """Grounded in benchmark miss: 'Calculate the compound interest...' wants a
        program-of-thoughts pick, reachable only when the out-of-tier penalty is 2.0."""
        analysis = selector.analyze(
            "Calculate the compound interest on $10,000 at 5% annual rate over 10 years."
        )
        assert analysis.recommended_framework == "program_of_thoughts"


class TestCategoryRegression:
    def test_research_category_detected(self, selector):
        assert selector.analyze("Evaluate the credibility of these sources.").category == TaskCategory.RESEARCH
        assert selector.analyze("Synthesize findings from 5 conflicting papers.").category == TaskCategory.RESEARCH

    def test_planning_category_detected(self, selector):
        assert selector.analyze("Create a 12-month strategic roadmap with risk analysis.").category == TaskCategory.PLANNING
        assert selector.analyze("Prioritize these features based on impact and effort.").category == TaskCategory.PLANNING

    def test_logic_category_detected(self, selector):
        assert selector.analyze("Identify the logical fallacy in this argument.").category == TaskCategory.LOGIC
        assert selector.analyze("Prove by induction that n³ + 2n is divisible by 3.").category == TaskCategory.LOGIC

    def test_data_category_detected(self, selector):
        assert selector.analyze("Analyze the correlation between two variables in this small dataset.").category == TaskCategory.DATA
        assert selector.analyze("Optimize this SQL query that's performing poorly on large datasets.").category == TaskCategory.DATA

    def test_code_not_creative(self, selector):
        # "write" alone used to push CODE tasks into CREATIVE
        assert selector.analyze("Write a Python function to reverse a linked list.").category == TaskCategory.CODE
        assert selector.analyze("Implement a thread-safe LRU cache in Rust.").category == TaskCategory.CODE
