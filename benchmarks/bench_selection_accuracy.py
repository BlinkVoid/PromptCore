#!/usr/bin/env python3
"""Benchmark: Framework Selection Accuracy

Measures how often PromptCore's automatic framework selection matches
expert-selected 'ground truth' frameworks across diverse task types.

Usage:
    uv run python benchmarks/bench_selection_accuracy.py
    uv run python benchmarks/bench_selection_accuracy.py --output custom_results.json
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from promptcore.domain.selector import FrameworkSelector, TaskCategory
from promptcore.domain.frameworks import FRAMEWORK_REGISTRY


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bench_selection_accuracy")


# Test tasks with expert-selected "ground truth" frameworks
# These represent what an expert prompt engineer would choose
TEST_TASKS: list[dict[str, Any]] = [
    # CODE category (12 tasks)
    {"task": "Write a Python function to reverse a linked list in-place.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Debug this JavaScript error: 'Cannot read property of undefined'. Here's the code...", "category": TaskCategory.CODE, "expert_framework": "self_ask", "complexity": 4},
    {"task": "Refactor this 500-line class to use dependency injection and proper separation of concerns.", "category": TaskCategory.CODE, "expert_framework": "step_back", "complexity": 8},
    {"task": "Implement a thread-safe LRU cache in Rust.", "category": TaskCategory.CODE, "expert_framework": "plan_and_solve", "complexity": 7},
    {"task": "Fix this SQL query that's running slowly on large datasets.", "category": TaskCategory.CODE, "expert_framework": "self_refinement", "complexity": 6},
    {"task": "Create a React hook for managing form state with validation.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Build a distributed rate limiter that works across multiple servers.", "category": TaskCategory.CODE, "expert_framework": "tree_of_thoughts", "complexity": 9},
    {"task": "Optimize this algorithm from O(n²) to O(n log n).", "category": TaskCategory.CODE, "expert_framework": "analogical_reasoning", "complexity": 7},
    {"task": "Write a function to parse and validate email addresses according to RFC 5322.", "category": TaskCategory.CODE, "expert_framework": "program_of_thoughts", "complexity": 6},
    {"task": "Create a TypeScript type definition for this complex nested API response.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Design a system that handles 10,000 concurrent websocket connections.", "category": TaskCategory.CODE, "expert_framework": "tree_of_thoughts", "complexity": 9},
    {"task": "Explain how this async/await code executes step by step.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 4},
    
    # MATH category (12 tasks)
    {"task": "Calculate the compound interest on $10,000 at 5% annual rate over 10 years.", "category": TaskCategory.MATH, "expert_framework": "program_of_thoughts", "complexity": 4},
    {"task": "Solve for x: 2x² + 5x - 3 = 0", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Find the probability of drawing two aces from a standard deck without replacement.", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Prove that the square root of 2 is irrational.", "category": TaskCategory.MATH, "expert_framework": "maieutic", "complexity": 7},
    {"task": "Optimize this linear programming problem to maximize profit.", "category": TaskCategory.MATH, "expert_framework": "plan_and_solve", "complexity": 8},
    {"task": "Calculate the expected value of this probability distribution.", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 6},
    {"task": "Find the shortest path through this weighted graph.", "category": TaskCategory.MATH, "expert_framework": "tree_of_thoughts", "complexity": 7},
    {"task": "Is this statistical result significant at p < 0.05?", "category": TaskCategory.MATH, "expert_framework": "self_calibration", "complexity": 6},
    {"task": "Compute the derivative of f(x) = x³ · sin(x) · e^x.", "category": TaskCategory.MATH, "expert_framework": "program_of_thoughts", "complexity": 5},
    {"task": "Verify this proof by induction for all positive integers n.", "category": TaskCategory.MATH, "expert_framework": "chain_of_verification", "complexity": 7},
    {"task": "Solve this system of three linear equations with three variables.", "category": TaskCategory.MATH, "expert_framework": "least_to_most", "complexity": 6},
    {"task": "What are the possible values of x that satisfy |2x - 5| < 3?", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 4},
    
    # LOGIC category (12 tasks)
    {"task": "Prove that if all cats are mammals and some mammals are pets, then some cats are pets.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Identify the logical fallacy in this argument.", "category": TaskCategory.LOGIC, "expert_framework": "maieutic", "complexity": 6},
    {"task": "Is this syllogism valid or invalid?", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Determine if these two boolean expressions are logically equivalent.", "category": TaskCategory.LOGIC, "expert_framework": "contrastive", "complexity": 5},
    {"task": "Find the contradiction in this set of statements.", "category": TaskCategory.LOGIC, "expert_framework": "self_ask", "complexity": 6},
    {"task": "If P implies Q and not-Q is true, what can we conclude about P?", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Evaluate this complex nested conditional statement.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Is this reasoning deductive or inductive? Explain why.", "category": TaskCategory.LOGIC, "expert_framework": "step_back", "complexity": 5},
    {"task": "Spot the flaw in this proof that 1 = 2.", "category": TaskCategory.LOGIC, "expert_framework": "reverse", "complexity": 6},
    {"task": "Translate this English statement into propositional logic.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Show that this argument commits the fallacy of affirming the consequent.", "category": TaskCategory.LOGIC, "expert_framework": "maieutic", "complexity": 6},
    {"task": "Given these premises, what conclusions can be validly drawn?", "category": TaskCategory.LOGIC, "expert_framework": "tree_of_thoughts", "complexity": 7},
    
    # CREATIVE category (12 tasks)
    {"task": "Write a haiku about machine learning.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 3},
    {"task": "Brainstorm 10 unique marketing slogans for a sustainable coffee brand.", "category": TaskCategory.CREATIVE, "expert_framework": "emotion_prompting", "complexity": 4},
    {"task": "Create a short story about a robot discovering emotions.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 5},
    {"task": "Design a logo concept for a fintech startup.", "category": TaskCategory.CREATIVE, "expert_framework": "directional_stimulus", "complexity": 5},
    {"task": "Write a poem about the changing seasons in free verse.", "category": TaskCategory.CREATIVE, "expert_framework": "emotion_prompting", "complexity": 4},
    {"task": "Imagine you're a medieval alchemist. Describe your latest experiment.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 5},
    {"task": "Generate creative names for a new productivity app.", "category": TaskCategory.CREATIVE, "expert_framework": "analogical", "complexity": 4},
    {"task": "Draft an engaging opening paragraph for a mystery novel.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 5},
    {"task": "Come up with an innovative solution to reduce plastic waste.", "category": TaskCategory.CREATIVE, "expert_framework": "directional_stimulus", "complexity": 6},
    {"task": "Compose a dialogue between two philosophers debating free will.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 6},
    {"task": "Design a unique user interface for a smart home control panel.", "category": TaskCategory.CREATIVE, "expert_framework": "directional_stimulus", "complexity": 6},
    {"task": "Create a backstory for a character in a fantasy RPG.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 5},
    
    # DATA category (12 tasks)
    {"task": "Analyze this CSV file and find the correlation between sales and advertising spend.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 6},
    {"task": "Filter this dataset to show only records where revenue > $100K.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 4},
    {"task": "Group these sales records by region and calculate total revenue per region.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 5},
    {"task": "What insights can you extract from this customer churn dataset?", "category": TaskCategory.DATA, "expert_framework": "step_back", "complexity": 7},
    {"task": "Clean this messy dataset: handle missing values, outliers, and duplicates.", "category": TaskCategory.DATA, "expert_framework": "plan_and_solve", "complexity": 6},
    {"task": "Calculate the rolling 7-day average of these daily temperature readings.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 5},
    {"task": "Join these two tables on customer_id and aggregate the results.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 6},
    {"task": "Visualize the distribution of this numerical column.", "category": TaskCategory.DATA, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Identify trends in this time series data.", "category": TaskCategory.DATA, "expert_framework": "thread_of_thought", "complexity": 6},
    {"task": "Normalize these features for machine learning preprocessing.", "category": TaskCategory.DATA, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Write a SQL query to find the top 5 customers by total order value.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 5},
    {"task": "Detect anomalies in this network traffic log.", "category": TaskCategory.DATA, "expert_framework": "contrastive", "complexity": 7},
    
    # RESEARCH category (12 tasks)
    {"task": "Summarize the key findings from this research paper on climate change.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_density", "complexity": 6},
    {"task": "Compare and contrast the approaches in these two studies.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive", "complexity": 6},
    {"task": "What are the limitations of this experimental design?", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "complexity": 7},
    {"task": "Evaluate the credibility of these sources.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_verification", "complexity": 6},
    {"task": "Synthesize information from these five papers on transformer architectures.", "category": TaskCategory.RESEARCH, "expert_framework": "step_back", "complexity": 8},
    {"task": "What gaps exist in the current literature on reinforcement learning?", "category": TaskCategory.RESEARCH, "expert_framework": "self_ask", "complexity": 7},
    {"task": "Assess the methodology used in this psychology study.", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "complexity": 6},
    {"task": "Review the evidence for and against this hypothesis.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive", "complexity": 7},
    {"task": "Extract the main arguments from this philosophical text.", "category": TaskCategory.RESEARCH, "expert_framework": "thread_of_thought", "complexity": 6},
    {"task": "Investigate whether this correlation implies causation.", "category": TaskCategory.RESEARCH, "expert_framework": "step_back", "complexity": 7},
    {"task": "Survey the current state of quantum computing research.", "category": TaskCategory.RESEARCH, "expert_framework": "step_back", "complexity": 8},
    {"task": "Analyze the statistical significance of these results.", "category": TaskCategory.RESEARCH, "expert_framework": "self_calibration", "complexity": 6},
    
    # PLANNING category (12 tasks)
    {"task": "Create a project plan for launching a mobile app in 6 months.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "complexity": 6},
    {"task": "Prioritize these features based on impact and effort.", "category": TaskCategory.PLANNING, "expert_framework": "tree_of_thoughts", "complexity": 6},
    {"task": "Break down this goal into actionable milestones.", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "complexity": 5},
    {"task": "Schedule these tasks with dependencies using a Gantt chart approach.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "complexity": 7},
    {"task": "Develop a roadmap for migrating from monolith to microservices.", "category": TaskCategory.PLANNING, "expert_framework": "reasoning_via_planning", "complexity": 8},
    {"task": "Allocate resources across three teams with different constraints.", "category": TaskCategory.PLANNING, "expert_framework": "tree_of_thoughts", "complexity": 7},
    {"task": "What risks should we consider for this product launch?", "category": TaskCategory.PLANNING, "expert_framework": "self_ask", "complexity": 6},
    {"task": "Plan a content calendar for the next quarter.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "complexity": 5},
    {"task": "Sequence these database migrations to minimize downtime.", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "complexity": 6},
    {"task": "Create a budget allocation strategy for marketing channels.", "category": TaskCategory.PLANNING, "expert_framework": "tree_of_thoughts", "complexity": 7},
    {"task": "Design a rollout plan for a new authentication system.", "category": TaskCategory.PLANNING, "expert_framework": "reasoning_via_planning", "complexity": 8},
    {"task": "How should we phase this feature implementation?", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "complexity": 5},
    
    # GENERAL category (16 tasks)
    {"task": "What is the capital of France?", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 1},
    {"task": "Explain how photosynthesis works.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Who won the World Cup in 2018?", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 1},
    {"task": "What are the main differences between REST and GraphQL?", "category": TaskCategory.GENERAL, "expert_framework": "contrastive", "complexity": 5},
    {"task": "Define machine learning in simple terms.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "List the benefits of regular exercise.", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 2},
    {"task": "How does blockchain technology work?", "category": TaskCategory.GENERAL, "expert_framework": "analogical", "complexity": 5},
    {"task": "What time is it in Tokyo right now?", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 1},
    {"task": "Explain the concept of supply and demand.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "What are NFTs and how do they work?", "category": TaskCategory.GENERAL, "expert_framework": "analogical", "complexity": 5},
    {"task": "Describe the water cycle.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "Who wrote 'To Kill a Mockingbird'?", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 1},
    {"task": "What is the difference between HTTP and HTTPS?", "category": TaskCategory.GENERAL, "expert_framework": "contrastive", "complexity": 4},
    {"task": "Explain the theory of evolution.", "category": TaskCategory.GENERAL, "expert_framework": "step_back", "complexity": 6},
    {"task": "What is the tallest mountain in the world?", "category": TaskCategory.GENERAL, "expert_framework": "zero_shot", "complexity": 1},
    {"task": "How do vaccines work?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},
]


def run_benchmark() -> dict[str, Any]:
    """Run the framework selection accuracy benchmark."""
    logger.info("Starting framework selection accuracy benchmark")
    logger.info(f"Total test tasks: {len(TEST_TASKS)}")
    
    selector = FrameworkSelector()
    
    results = []
    exact_matches = 0
    top3_matches = 0
    category_correct = 0
    
    # Category-level tracking
    category_stats = defaultdict(lambda: {"total": 0, "correct": 0})
    
    # Framework-level confusion matrix data
    framework_predictions = defaultdict(lambda: defaultdict(int))
    
    for i, test_case in enumerate(TEST_TASKS):
        task_text = test_case["task"]
        expert_framework = test_case["expert_framework"]
        expected_category = test_case["category"]
        expected_complexity = test_case["complexity"]
        
        # Run analysis
        analysis = selector.analyze(task_text)
        
        # Check exact match
        exact_match = analysis.recommended_framework == expert_framework
        if exact_match:
            exact_matches += 1
        
        # Check top-3 match
        top3_match = expert_framework in analysis.alternative_frameworks or exact_match
        if top3_match:
            top3_matches += 1
        
        # Check category detection
        category_match = analysis.category == expected_category
        if category_match:
            category_correct += 1
        
        # Update category stats
        category_stats[expected_category.value]["total"] += 1
        if exact_match:
            category_stats[expected_category.value]["correct"] += 1
        
        # Update confusion matrix
        framework_predictions[expert_framework][analysis.recommended_framework] += 1
        
        result = {
            "task": task_text[:100] + "..." if len(task_text) > 100 else task_text,
            "expected_framework": expert_framework,
            "predicted_framework": analysis.recommended_framework,
            "alternatives": analysis.alternative_frameworks,
            "exact_match": exact_match,
            "top3_match": top3_match,
            "expected_category": expected_category.value,
            "predicted_category": analysis.category.value,
            "category_match": category_match,
            "expected_complexity": expected_complexity,
            "predicted_complexity": analysis.complexity_score,
            "complexity_error": abs(expected_complexity - analysis.complexity_score),
            "reasoning": analysis.reasoning,
        }
        results.append(result)
        
        if (i + 1) % 20 == 0:
            logger.info(f"Processed {i + 1}/{len(TEST_TASKS)} tasks")
    
    # Calculate aggregate metrics
    total_tasks = len(TEST_TASKS)
    exact_match_rate = exact_matches / total_tasks
    top3_match_rate = top3_matches / total_tasks
    category_accuracy = category_correct / total_tasks
    
    # Calculate category-level accuracies
    category_accuracies = {
        cat: stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        for cat, stats in category_stats.items()
    }
    
    # Build confusion matrix
    all_frameworks = sorted(set(
        list(FRAMEWORK_REGISTRY.keys()) + 
        [tc["expert_framework"] for tc in TEST_TASKS]
    ))
    confusion_matrix = {
        "frameworks": all_frameworks,
        "matrix": [
            [framework_predictions[true][pred] for pred in all_frameworks]
            for true in all_frameworks
        ]
    }
    
    summary = {
        "total_tasks": total_tasks,
        "exact_match_rate": round(exact_match_rate, 4),
        "exact_matches": exact_matches,
        "top3_match_rate": round(top3_match_rate, 4),
        "top3_matches": top3_matches,
        "category_detection_accuracy": round(category_accuracy, 4),
        "category_correct": category_correct,
        "category_breakdown": {
            cat: {
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": round(stats["correct"] / stats["total"], 4) if stats["total"] > 0 else 0
            }
            for cat, stats in category_stats.items()
        },
        "confusion_matrix": confusion_matrix,
    }
    
    logger.info(f"Benchmark complete. Exact match rate: {exact_match_rate:.2%}")
    logger.info(f"Top-3 match rate: {top3_match_rate:.2%}")
    logger.info(f"Category detection accuracy: {category_accuracy:.2%}")
    
    return {
        "summary": summary,
        "detailed_results": results,
    }


def generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate a markdown report from benchmark results."""
    summary = data["summary"]
    
    lines = [
        "# Framework Selection Accuracy Benchmark",
        "",
        f"**Date:** {datetime.now().isoformat()}",
        f"**Total Tasks:** {summary['total_tasks']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Exact Match Rate | {summary['exact_match_rate']:.2%} |",
        f"| Top-3 Match Rate | {summary['top3_match_rate']:.2%} |",
        f"| Category Detection Accuracy | {summary['category_detection_accuracy']:.2%} |",
        "",
        "## Category Breakdown",
        "",
        "| Category | Total | Correct | Accuracy |",
        "|----------|-------|---------|----------|",
    ]
    
    for cat, stats in summary["category_breakdown"].items():
        lines.append(f"| {cat} | {stats['total']} | {stats['correct']} | {stats['accuracy']:.2%} |")
    
    lines.extend([
        "",
        "## Confusion Matrix",
        "",
        "Top predicted frameworks per expert selection:",
        "",
    ])
    
    # Simplified confusion matrix - show top predictions
    cm = summary["confusion_matrix"]
    frameworks = cm["frameworks"]
    
    lines.append("| Expert \\ Predicted | Count |")
    lines.append("|---------------------|-------|")
    
    # Find most common misclassifications
    misclassifications = []
    for i, true_fw in enumerate(frameworks):
        for j, pred_fw in enumerate(frameworks):
            count = cm["matrix"][i][j]
            if count > 0 and true_fw != pred_fw:
                misclassifications.append((true_fw, pred_fw, count))
    
    misclassifications.sort(key=lambda x: x[2], reverse=True)
    for true_fw, pred_fw, count in misclassifications[:20]:
        lines.append(f"| {true_fw} → {pred_fw} | {count} |")
    
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- **Exact Match Rate** measures how often PromptCore selects the same framework as an expert would",
        "- **Top-3 Match Rate** is more forgiving - considers the recommendation valid if the expert's choice is in the top 3",
        "- **Category Detection** measures whether the task category (code/math/etc.) is correctly identified",
        "",
        "### Target Benchmarks",
        "",
        "Based on the COMPARISON.md benchmark plan:",
        "- **Target:** 70%+ agreement rate validates the heuristic approach",
        "- **Minimum acceptable:** 50% agreement rate",
        "",
        f"### Current Status: {'PASS ✓' if summary['exact_match_rate'] >= 0.50 else 'NEEDS IMPROVEMENT ✗'}",
        "",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark framework selection accuracy"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/results/selection_accuracy.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--markdown",
        type=str,
        default="benchmarks/results/selection_accuracy.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()
    
    # Run benchmark
    results = run_benchmark()
    
    # Save JSON results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"JSON results saved to {output_path}")
    
    # Save markdown report
    markdown = generate_markdown_report(results)
    markdown_path = Path(args.markdown)
    with open(markdown_path, "w") as f:
        f.write(markdown)
    logger.info(f"Markdown report saved to {markdown_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("FRAMEWORK SELECTION ACCURACY BENCHMARK")
    print("=" * 60)
    print(f"Exact Match Rate: {results['summary']['exact_match_rate']:.2%}")
    print(f"Top-3 Match Rate: {results['summary']['top3_match_rate']:.2%}")
    print(f"Category Detection: {results['summary']['category_detection_accuracy']:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
