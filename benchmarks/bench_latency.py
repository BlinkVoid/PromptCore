#!/usr/bin/env python3
"""Benchmark: Latency and Performance

Measures execution time for framework selection operations to ensure
PromptCore adds negligible overhead to agent workflows.

Usage:
    uv run python benchmarks/bench_latency.py
    uv run python benchmarks/bench_latency.py --iterations 5000
"""

import argparse
import json
import logging
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from promptcore.domain.selector import FrameworkSelector
from promptcore.domain.builder import PromptBuilder


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bench_latency")


# Sample tasks for testing (varied complexity and categories)
SAMPLE_TASKS = [
    "What is the capital of France?",
    "Write a Python function to calculate factorial.",
    "Solve for x: 2x + 5 = 15",
    "Explain the difference between REST and GraphQL APIs.",
    "Design a database schema for an e-commerce application with users, products, orders, and inventory management.",
    "Analyze the time and space complexity of merge sort and compare it to quicksort.",
    "Create a comprehensive project plan for migrating from a monolithic architecture to microservices.",
    "Write a poem about machine learning and artificial intelligence.",
    "Calculate the probability of drawing two aces from a standard deck.",
    "Debug this race condition in concurrent code.",
]


def measure_latency(func, iterations: int, warmup: int = 100) -> dict[str, float]:
    """Measure execution latency of a function over multiple iterations."""
    # Warmup runs
    for _ in range(warmup):
        func()
    
    # Actual measurements
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    times.sort()
    
    return {
        "iterations": iterations,
        "p50": round(statistics.median(times), 4),
        "p95": round(times[int(len(times) * 0.95)], 4),
        "p99": round(times[int(len(times) * 0.99)], 4),
        "mean": round(statistics.mean(times), 4),
        "stdev": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
        "min": round(times[0], 4),
        "max": round(times[-1], 4),
    }


def benchmark_analyze(selector: FrameworkSelector, iterations: int) -> dict[str, Any]:
    """Benchmark the analyze() operation."""
    logger.info(f"Benchmarking analyze() with {iterations} iterations")
    
    # Test with varied tasks
    task_idx = 0
    
    def run_analyze():
        nonlocal task_idx
        task = SAMPLE_TASKS[task_idx % len(SAMPLE_TASKS)]
        task_idx += 1
        selector.analyze(task)
    
    results = measure_latency(run_analyze, iterations)
    results["operation"] = "FrameworkSelector.analyze()"
    results["description"] = "Task analysis with category detection, complexity scoring, and framework selection"
    
    logger.info(f"analyze() p50: {results['p50']:.4f}ms, p95: {results['p95']:.4f}ms")
    return results


def benchmark_build(builder: PromptBuilder, selector: FrameworkSelector, iterations: int) -> dict[str, Any]:
    """Benchmark the build() operation (meta-prompt generation)."""
    logger.info(f"Benchmarking build() with {iterations} iterations")
    
    task_idx = 0
    
    def run_build():
        nonlocal task_idx
        task = SAMPLE_TASKS[task_idx % len(SAMPLE_TASKS)]
        task_idx += 1
        # First analyze, then build
        analysis = selector.analyze(task)
        builder.build_with_analysis(analysis)
    
    results = measure_latency(run_build, iterations)
    results["operation"] = "PromptBuilder.build_with_analysis()"
    results["description"] = "Full pipeline: analyze task + generate meta-prompt"
    
    logger.info(f"build() p50: {results['p50']:.4f}ms, p95: {results['p95']:.4f}ms")
    return results


def benchmark_full_pipeline(builder: PromptBuilder, selector: FrameworkSelector, iterations: int) -> dict[str, Any]:
    """Benchmark the full end-to-end pipeline."""
    logger.info(f"Benchmarking full pipeline with {iterations} iterations")
    
    task_idx = 0
    
    def run_pipeline():
        nonlocal task_idx
        task = SAMPLE_TASKS[task_idx % len(SAMPLE_TASKS)]
        task_idx += 1
        # Complete workflow: analyze + build
        analysis = selector.analyze(task)
        prompt = builder.build_with_analysis(analysis)
        # Access the result to ensure it's fully computed
        _ = prompt.meta_prompt
    
    results = measure_latency(run_pipeline, iterations)
    results["operation"] = "Full Pipeline (analyze + build + access)"
    results["description"] = "End-to-end: task analysis, framework selection, meta-prompt generation"
    
    logger.info(f"Full pipeline p50: {results['p50']:.4f}ms, p95: {results['p95']:.4f}ms")
    return results


def benchmark_framework_lookup(iterations: int) -> dict[str, Any]:
    """Benchmark framework registry lookup."""
    logger.info(f"Benchmarking framework lookup with {iterations} iterations")
    
    from promptcore.domain.frameworks import FRAMEWORK_REGISTRY, get_framework
    
    framework_names = list(FRAMEWORK_REGISTRY.keys())
    idx = 0
    
    def run_lookup():
        nonlocal idx
        name = framework_names[idx % len(framework_names)]
        idx += 1
        _ = get_framework(name)
    
    results = measure_latency(run_lookup, iterations)
    results["operation"] = "get_framework() lookup"
    results["description"] = "Framework registry lookup by name"
    
    logger.info(f"Framework lookup p50: {results['p50']:.4f}ms")
    return results


def run_benchmark(iterations: int) -> dict[str, Any]:
    """Run all latency benchmarks."""
    logger.info("Starting latency benchmark suite")
    logger.info(f"Iterations per test: {iterations}")
    
    selector = FrameworkSelector()
    builder = PromptBuilder()
    
    benchmarks = []
    
    # Run each benchmark
    benchmarks.append(benchmark_analyze(selector, iterations))
    benchmarks.append(benchmark_build(builder, selector, iterations))
    benchmarks.append(benchmark_full_pipeline(builder, selector, iterations))
    benchmarks.append(benchmark_framework_lookup(iterations))
    
    # Calculate overhead relative to baseline
    analyze_time = next(b for b in benchmarks if "analyze" in b["operation"])["p50"]
    full_pipeline_time = next(b for b in benchmarks if "Full Pipeline" in b["operation"])["p50"]
    
    # Typical LLM API latency for comparison
    typical_llm_latency_ms = 500  # 500ms is reasonable for GPT-4 class models
    
    overhead_ratio = full_pipeline_time / typical_llm_latency_ms
    
    summary = {
        "iterations": iterations,
        "sample_tasks": len(SAMPLE_TASKS),
        "benchmarks": benchmarks,
        "overhead_analysis": {
            "typical_llm_latency_ms": typical_llm_latency_ms,
            "promptcore_latency_ms": full_pipeline_time,
            "overhead_ratio": round(overhead_ratio, 6),
            "overhead_percentage": round(overhead_ratio * 100, 4),
        },
        "performance_grade": "EXCELLENT" if overhead_ratio < 0.01 else "GOOD" if overhead_ratio < 0.05 else "ACCEPTABLE" if overhead_ratio < 0.10 else "NEEDS OPTIMIZATION",
    }
    
    return summary


def generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate a markdown report from benchmark results."""
    lines = [
        "# Latency and Performance Benchmark",
        "",
        f"**Date:** {datetime.now().isoformat()}",
        f"**Iterations per test:** {data['iterations']}",
        "",
        "## Summary",
        "",
        f"**Performance Grade:** {data['performance_grade']}",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| PromptCore latency (p50) | {data['overhead_analysis']['promptcore_latency_ms']:.4f} ms |",
        f"| Typical LLM API latency | {data['overhead_analysis']['typical_llm_latency_ms']} ms |",
        f"| Overhead ratio | {data['overhead_analysis']['overhead_ratio']:.4f}x |",
        f"| Overhead percentage | {data['overhead_analysis']['overhead_percentage']:.4f}% |",
        "",
        "## Detailed Results",
        "",
    ]
    
    for bench in data["benchmarks"]:
        lines.extend([
            f"### {bench['operation']}",
            "",
            f"*{bench['description']}*",
            "",
            "| Percentile | Latency (ms) |",
            "|------------|--------------|",
            f"| p50 (median) | {bench['p50']:.4f} |",
            f"| p95 | {bench['p95']:.4f} |",
            f"| p99 | {bench['p99']:.4f} |",
            f"| mean | {bench['mean']:.4f} |",
            f"| stdev | {bench['stdev']:.4f} |",
            f"| min | {bench['min']:.4f} |",
            f"| max | {bench['max']:.4f} |",
            "",
        ])
    
    lines.extend([
        "## Interpretation",
        "",
        "### Latency Targets",
        "",
        "| Target | Threshold | Status |",
        "|--------|-----------|--------|",
    ])
    
    overhead_pct = data['overhead_analysis']['overhead_percentage']
    
    if overhead_pct < 1.0:
        lines.append(f"| Sub-1% overhead | < 1% | **PASS** ({overhead_pct:.3f}%) |")
    else:
        lines.append(f"| Sub-1% overhead | < 1% | **FAIL** ({overhead_pct:.3f}%) |")
    
    if overhead_pct < 5.0:
        lines.append(f"| Sub-5% overhead | < 5% | **PASS** ({overhead_pct:.3f}%) |")
    else:
        lines.append(f"| Sub-5% overhead | < 5% | **FAIL** ({overhead_pct:.3f}%) |")
    
    lines.extend([
        "",
        "### Context",
        "",
        "- **LLM API latency** (~500ms) includes network round-trip, queuing, and generation",
        "- **PromptCore latency** (~1-2ms) is purely local computation",
        "- **Overhead ratio** = PromptCore time / LLM time",
        "",
        "Even a 5% overhead (25ms) is imperceptible to end users,",
        "while a 0.1% overhead (< 1ms) is effectively free.",
        "",
        "## Conclusion",
        "",
    ])
    
    if data['performance_grade'] == "EXCELLENT":
        lines.append("✓ **PromptCore adds negligible latency to agent workflows.**")
    elif data['performance_grade'] == "GOOD":
        lines.append("✓ **PromptCore overhead is acceptable for production use.**")
    else:
        lines.append("⚠ **Consider optimization if running at very high scale.**")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark PromptCore latency and performance"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of iterations per benchmark (default: 1000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/results/latency.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--markdown",
        type=str,
        default="benchmarks/results/latency.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()
    
    # Run benchmark
    results = run_benchmark(args.iterations)
    
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
    print("LATENCY BENCHMARK")
    print("=" * 60)
    
    for bench in results["benchmarks"]:
        print(f"{bench['operation']}: p50={bench['p50']:.4f}ms, p95={bench['p95']:.4f}ms")
    
    print("-" * 60)
    print(f"Overhead vs LLM API: {results['overhead_analysis']['overhead_percentage']:.4f}%")
    print(f"Grade: {results['performance_grade']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
