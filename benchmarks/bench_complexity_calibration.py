#!/usr/bin/env python3
"""Benchmark: Complexity Scoring Calibration

Measures the correlation between PromptCore's automated complexity scores
and human-rated complexity judgments.

Usage:
    uv run python benchmarks/bench_complexity_calibration.py
    uv run python benchmarks/bench_complexity_calibration.py --output custom_results.json
"""

import argparse
import json
import logging
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from promptcore.domain.selector import FrameworkSelector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bench_complexity_calibration")


# Test tasks with human-rated complexity (1-10 scale)
# These ratings represent what a human expert would assign
COMPLEXITY_TEST_TASKS: list[dict[str, Any]] = [
    # Very Simple (1-2)
    {"task": "What is 2+2?", "human_complexity": 1, "category": "general"},
    {"task": "Say hello in Spanish.", "human_complexity": 1, "category": "general"},
    {"task": "List three primary colors.", "human_complexity": 1, "category": "general"},
    {"task": "What is the capital of Japan?", "human_complexity": 1, "category": "general"},
    {"task": "Define 'photosynthesis' in one sentence.", "human_complexity": 2, "category": "general"},
    
    # Simple (2-3)
    {"task": "Write a Python function that returns the square of a number.", "human_complexity": 2, "category": "code"},
    {"task": "Calculate 15% of 200.", "human_complexity": 2, "category": "math"},
    {"task": "Write a haiku about nature.", "human_complexity": 2, "category": "creative"},
    {"task": "Is this statement true: All squares are rectangles?", "human_complexity": 2, "category": "logic"},
    {"task": "Filter this list to show only even numbers.", "human_complexity": 3, "category": "data"},
    
    # Easy-Medium (3-4)
    {"task": "Explain the difference between a list and a tuple in Python.", "human_complexity": 3, "category": "code"},
    {"task": "Solve for x: 2x + 5 = 15", "human_complexity": 3, "category": "math"},
    {"task": "Summarize this one-paragraph article.", "human_complexity": 3, "category": "research"},
    {"task": "Create a weekly meal plan.", "human_complexity": 4, "category": "planning"},
    {"task": "Debug this simple syntax error in JavaScript.", "human_complexity": 3, "category": "code"},
    
    # Medium (4-5)
    {"task": "Implement a function to check if a string is a palindrome.", "human_complexity": 4, "category": "code"},
    {"task": "Calculate the area of a triangle given three side lengths using Heron's formula.", "human_complexity": 4, "category": "math"},
    {"task": "Identify the logical fallacy in this argument.", "human_complexity": 5, "category": "logic"},
    {"task": "Write a short story with a plot twist.", "human_complexity": 4, "category": "creative"},
    {"task": "Analyze the correlation between two variables in this small dataset.", "human_complexity": 5, "category": "data"},
    
    # Medium-Hard (5-6)
    {"task": "Refactor this code to use the Strategy pattern.", "human_complexity": 5, "category": "code"},
    {"task": "Prove that the sum of angles in a triangle equals 180 degrees.", "human_complexity": 6, "category": "math"},
    {"task": "Compare and contrast two approaches to API design.", "human_complexity": 5, "category": "research"},
    {"task": "Plan a project with 5 milestones and resource constraints.", "human_complexity": 6, "category": "planning"},
    {"task": "Solve this logic puzzle with multiple constraints.", "human_complexity": 6, "category": "logic"},
    
    # Hard (6-7)
    {"task": "Implement a balanced binary search tree with insertion and deletion.", "human_complexity": 7, "category": "code"},
    {"task": "Calculate the probability of getting at least one six when rolling 4 dice.", "human_complexity": 6, "category": "math"},
    {"task": "Evaluate the methodology and limitations of this research study.", "human_complexity": 7, "category": "research"},
    {"task": "Design a database schema for a multi-tenant SaaS application.", "human_complexity": 6, "category": "code"},
    {"task": "Optimize this SQL query that's performing poorly on large datasets.", "human_complexity": 7, "category": "data"},
    
    # Hard-Very Hard (7-8)
    {"task": "Build a concurrent task scheduler with priority queues and deadlock prevention.", "human_complexity": 8, "category": "code"},
    {"task": "Solve this system of differential equations.", "human_complexity": 8, "category": "math"},
    {"task": "Synthesize findings from 5 conflicting research papers on the same topic.", "human_complexity": 8, "category": "research"},
    {"task": "Create a 12-month strategic roadmap with risk analysis.", "human_complexity": 7, "category": "planning"},
    {"task": "Prove by induction that n³ + 2n is divisible by 3 for all positive integers.", "human_complexity": 8, "category": "math"},
    
    # Very Hard (8-9)
    {"task": "Design a distributed consensus protocol that handles network partitions.", "human_complexity": 9, "category": "code"},
    {"task": "Prove the halting problem is undecidable.", "human_complexity": 9, "category": "logic"},
    {"task": "Develop a comprehensive literature review addressing gaps in quantum computing research.", "human_complexity": 8, "category": "research"},
    {"task": "Create an optimization algorithm for resource allocation across 1000+ variables.", "human_complexity": 9, "category": "code"},
    {"task": "Analyze the time and space complexity of this recursive algorithm with memoization.", "human_complexity": 8, "category": "code"},
    
    # Expert (9-10)
    {"task": "Design and prove the correctness of a Byzantine fault-tolerant consensus algorithm.", "human_complexity": 10, "category": "code"},
    {"task": "Develop a novel proof for a previously unproven theorem in number theory.", "human_complexity": 10, "category": "math"},
    {"task": "Create a comprehensive research framework addressing multiple confounding variables in longitudinal studies.", "human_complexity": 9, "category": "research"},
    {"task": "Architect a system that guarantees exactly-once message delivery across unreliable networks.", "human_complexity": 10, "category": "code"},
    {"task": "Prove P ≠ NP or provide a polynomial-time algorithm for an NP-complete problem.", "human_complexity": 10, "category": "math"},
]


def calculate_pearson_correlation(x: list[float], y: list[float]) -> float:
    """Calculate Pearson correlation coefficient."""
    n = len(x)
    if n != len(y) or n == 0:
        return 0.0
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    denominator_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    denominator_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    
    if denominator_x == 0 or denominator_y == 0:
        return 0.0
    
    return numerator / (denominator_x * denominator_y)


def calculate_spearman_correlation(x: list[float], y: list[float]) -> float:
    """Calculate Spearman rank correlation coefficient."""
    n = len(x)
    if n != len(y) or n == 0:
        return 0.0
    
    # Convert to ranks
    def rank(data: list[float]) -> list[float]:
        sorted_data = sorted((v, i) for i, v in enumerate(data))
        ranks = [0.0] * len(data)
        i = 0
        while i < len(sorted_data):
            j = i
            while j < len(sorted_data) and sorted_data[j][0] == sorted_data[i][0]:
                j += 1
            # Average rank for ties
            avg_rank = (i + j + 1) / 2
            for k in range(i, j):
                ranks[sorted_data[k][1]] = avg_rank
            i = j
        return ranks
    
    rank_x = rank(x)
    rank_y = rank(y)
    
    return calculate_pearson_correlation(rank_x, rank_y)


def calculate_mae(predicted: list[float], actual: list[float]) -> float:
    """Calculate Mean Absolute Error."""
    n = len(predicted)
    if n == 0 or n != len(actual):
        return 0.0
    return sum(abs(p - a) for p, a in zip(predicted, actual)) / n


def calculate_rmse(predicted: list[float], actual: list[float]) -> float:
    """Calculate Root Mean Square Error."""
    n = len(predicted)
    if n == 0 or n != len(actual):
        return 0.0
    return math.sqrt(sum((p - a) ** 2 for p, a in zip(predicted, actual)) / n)


def run_benchmark() -> dict[str, Any]:
    """Run the complexity calibration benchmark."""
    logger.info("Starting complexity calibration benchmark")
    logger.info(f"Total test tasks: {len(COMPLEXITY_TEST_TASKS)}")
    
    selector = FrameworkSelector()
    
    results = []
    human_scores = []
    machine_scores = []
    
    for i, test_case in enumerate(COMPLEXITY_TEST_TASKS):
        task_text = test_case["task"]
        human_complexity = test_case["human_complexity"]
        category = test_case["category"]
        
        # Run analysis
        analysis = selector.analyze(task_text)
        machine_complexity = analysis.complexity_score
        
        human_scores.append(human_complexity)
        machine_scores.append(machine_complexity)
        
        error = abs(human_complexity - machine_complexity)
        
        result = {
            "task": task_text[:80] + "..." if len(task_text) > 80 else task_text,
            "category": category,
            "human_complexity": human_complexity,
            "machine_complexity": machine_complexity,
            "absolute_error": error,
            "squared_error": error ** 2,
        }
        results.append(result)
        
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(COMPLEXITY_TEST_TASKS)} tasks")
    
    # Calculate correlation metrics
    pearson_r = calculate_pearson_correlation(human_scores, machine_scores)
    spearman_r = calculate_spearman_correlation(human_scores, machine_scores)
    mae = calculate_mae(machine_scores, human_scores)
    rmse = calculate_rmse(machine_scores, human_scores)
    
    # Calculate by complexity range
    range_stats = {
        "1-3 (Simple)": {"count": 0, "mae": []},
        "4-6 (Medium)": {"count": 0, "mae": []},
        "7-10 (Hard)": {"count": 0, "mae": []},
    }
    
    for r in results:
        h = r["human_complexity"]
        error = r["absolute_error"]
        if h <= 3:
            range_stats["1-3 (Simple)"]["count"] += 1
            range_stats["1-3 (Simple)"]["mae"].append(error)
        elif h <= 6:
            range_stats["4-6 (Medium)"]["count"] += 1
            range_stats["4-6 (Medium)"]["mae"].append(error)
        else:
            range_stats["7-10 (Hard)"]["count"] += 1
            range_stats["7-10 (Hard)"]["mae"].append(error)
    
    for range_name, stats in range_stats.items():
        if stats["mae"]:
            stats["mae_avg"] = round(sum(stats["mae"]) / len(stats["mae"]), 2)
        else:
            stats["mae_avg"] = 0
        del stats["mae"]  # Remove raw list for cleaner output
    
    summary = {
        "total_tasks": len(COMPLEXITY_TEST_TASKS),
        "pearson_correlation": round(pearson_r, 4),
        "spearman_correlation": round(spearman_r, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "range_breakdown": range_stats,
    }
    
    logger.info(f"Benchmark complete. Pearson r: {pearson_r:.3f}, Spearman r: {spearman_r:.3f}")
    logger.info(f"MAE: {mae:.3f}, RMSE: {rmse:.3f}")
    
    return {
        "summary": summary,
        "detailed_results": results,
    }


def generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate a markdown report from benchmark results."""
    summary = data["summary"]
    
    lines = [
        "# Complexity Calibration Benchmark",
        "",
        f"**Date:** {datetime.now().isoformat()}",
        f"**Total Tasks:** {summary['total_tasks']}",
        "",
        "## Summary",
        "",
        "| Metric | Value | Interpretation |",
        "|--------|-------|----------------|",
        f"| Pearson Correlation (r) | {summary['pearson_correlation']:.4f} | Linear relationship strength |",
        f"| Spearman Correlation (ρ) | {summary['spearman_correlation']:.4f} | Rank-order relationship |",
        f"| Mean Absolute Error (MAE) | {summary['mae']:.4f} | Avg absolute difference |",
        f"| Root Mean Square Error (RMSE) | {summary['rmse']:.4f} | Penalizes large errors |",
        "",
        "## Correlation Interpretation",
        "",
        "| Correlation | Strength |",
        "|-------------|----------|",
        "| 0.90 - 1.00 | Very Strong |",
        "| 0.70 - 0.89 | Strong |",
        "| 0.50 - 0.69 | Moderate |",
        "| 0.30 - 0.49 | Weak |",
        "| 0.00 - 0.29 | Very Weak / None |",
        "",
        f"### Current Status: ",
    ]
    
    pearson = summary['pearson_correlation']
    if pearson >= 0.70:
        lines.append(f"**{pearson:.3f} = Strong correlation ✓**")
    elif pearson >= 0.50:
        lines.append(f"**{pearson:.3f} = Moderate correlation (acceptable)**")
    else:
        lines.append(f"**{pearson:.3f} = Weak correlation (needs improvement)**")
    
    lines.extend([
        "",
        "## Performance by Complexity Range",
        "",
        "| Range | Count | MAE |",
        "|-------|-------|-----|",
    ])
    
    for range_name, stats in summary["range_breakdown"].items():
        lines.append(f"| {range_name} | {stats['count']} | {stats['mae_avg']:.2f} |")
    
    lines.extend([
        "",
        "## Target Benchmarks",
        "",
        "Based on the COMPARISON.md benchmark plan:",
        "",
        "| Target | Threshold | Status |",
        "|--------|-----------|--------|",
    ])
    
    if pearson >= 0.7:
        lines.append(f"| Strong correlation | r > 0.70 | **PASS** |")
    else:
        lines.append(f"| Strong correlation | r > 0.70 | **NEEDS WORK** |")
    
    if pearson >= 0.5:
        lines.append(f"| Acceptable correlation | r > 0.50 | **PASS** |")
    else:
        lines.append(f"| Acceptable correlation | r > 0.50 | **NEEDS WORK** |")
    
    lines.extend([
        "",
        "## Methodology Notes",
        "",
        "- Human complexity ratings based on estimated cognitive load and domain expertise required",
        "- Pearson r measures linear correlation (sensitive to outliers)",
        "- Spearman ρ measures rank correlation (robust to non-linear relationships)",
        "- MAE reports average error in complexity points (0-10 scale)",
        "",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark complexity scoring calibration"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/results/complexity_calibration.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--markdown",
        type=str,
        default="benchmarks/results/complexity_calibration.md",
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
    print("COMPLEXITY CALIBRATION BENCHMARK")
    print("=" * 60)
    print(f"Pearson r: {results['summary']['pearson_correlation']:.3f}")
    print(f"Spearman ρ: {results['summary']['spearman_correlation']:.3f}")
    print(f"MAE: {results['summary']['mae']:.3f} points")
    print(f"RMSE: {results['summary']['rmse']:.3f} points")
    print("=" * 60)


if __name__ == "__main__":
    main()
