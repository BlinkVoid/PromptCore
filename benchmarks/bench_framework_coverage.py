#!/usr/bin/env python3
"""Benchmark: Framework Coverage and Utilization

Analyzes which frameworks are selected across diverse tasks to identify
usage patterns and potential 'dead' frameworks that are never selected.

Usage:
    uv run python benchmarks/bench_framework_coverage.py
    uv run python benchmarks/bench_framework_coverage.py --tasks 1000
"""

import argparse
import json
import logging
import random
import sys
from collections import Counter, defaultdict
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
logger = logging.getLogger("bench_framework_coverage")


# Diverse task templates for generating test cases
TASK_TEMPLATES: dict[TaskCategory, list[str]] = {
    TaskCategory.CODE: [
        "Write a {language} function to {action}.",
        "Debug this {language} error: {error}",
        "Refactor this code to use {pattern}.",
        "Implement {data_structure} in {language}.",
        "Optimize this {algorithm_type} algorithm.",
        "Create a {language} class for {purpose}.",
        "Fix the {issue} in this {language} code.",
        "Write unit tests for this {language} function.",
        "Convert this {language_a} code to {language_b}.",
        "Design an API endpoint for {functionality}.",
    ],
    TaskCategory.MATH: [
        "Calculate {calculation}.",
        "Solve for x: {equation}",
        "Find the {math_operation} of {values}.",
        "Prove that {theorem}.",
        "What is the probability of {event}?",
        "Calculate the {statistic} for this dataset.",
        "Optimize this {optimization_type} problem.",
        "Verify this {proof_type} proof.",
        "Estimate {value} to within {precision}.",
        "Analyze the convergence of {sequence}.",
    ],
    TaskCategory.LOGIC: [
        "Prove that {statement}.",
        "Identify the fallacy in: {argument}",
        "Is this syllogism valid? {syllogism}",
        "Find the contradiction in {set_of_statements}.",
        "Determine if {expressions} are equivalent.",
        "Evaluate this nested conditional.",
        "Is this reasoning deductive or inductive?",
        "Spot the flaw in this proof.",
        "Translate this to propositional logic.",
        "What conclusions follow from {premises}?",
    ],
    TaskCategory.CREATIVE: [
        "Write a {genre} about {topic}.",
        "Brainstorm {number} ideas for {purpose}.",
        "Create a {creative_type} for {context}.",
        "Design a {design_target}.",
        "Generate names for {naming_context}.",
        "Draft an opening for {content_type}.",
        "Come up with a solution to {problem}.",
        "Compose {content} in the style of {style}.",
        "Imagine you are {persona}. Describe {scenario}.",
        "Develop a concept for {project_type}.",
    ],
    TaskCategory.DATA: [
        "Analyze {dataset} and find {relationship}.",
        "Filter {data} to show {condition}.",
        "Group {records} by {dimension}.",
        "What insights can you extract from {data}?",
        "Clean this dataset: handle {issues}.",
        "Calculate {metric} for {time_period}.",
        "Join {table_a} and {table_b} on {key}.",
        "Visualize the distribution of {variable}.",
        "Identify trends in {time_series}.",
        "Detect anomalies in {data_source}.",
    ],
    TaskCategory.RESEARCH: [
        "Summarize the key findings from {source}.",
        "Compare {approach_a} and {approach_b}.",
        "What are the limitations of {methodology}?",
        "Evaluate the credibility of {sources}.",
        "Synthesize information from {number} papers on {topic}.",
        "What gaps exist in {research_area}?",
        "Assess the methodology used in {study}.",
        "Review the evidence for {hypothesis}.",
        "Extract the main arguments from {text}.",
        "Investigate whether {claim} is supported.",
    ],
    TaskCategory.PLANNING: [
        "Create a plan for {project} in {timeframe}.",
        "Prioritize these items by {criteria}.",
        "Break down {goal} into milestones.",
        "Schedule {tasks} with dependencies.",
        "Develop a roadmap for {transition}.",
        "Allocate {resources} across {constraints}.",
        "What risks should we consider for {event}?",
        "Plan {activity} for {time_period}.",
        "Sequence {operations} to minimize {objective}.",
        "Design a rollout for {system_change}.",
    ],
    TaskCategory.GENERAL: [
        "What is {fact}?",
        "Explain how {process} works.",
        "Who {accomplishment}?",
        "What are the differences between {a} and {b}?",
        "Define {term}.",
        "List the benefits of {activity}.",
        "How does {technology} work?",
        "What time is it in {location}?",
        "Explain {concept}.",
        "What is {superlative} in {category}?",
    ],
}

# Fill-in values for templates
FILL_VALUES = {
    "language": ["Python", "JavaScript", "TypeScript", "Java", "Rust", "Go", "C++", "Ruby"],
    "action": ["sort an array", "validate email addresses", "parse JSON", "fetch data from an API", "implement pagination"],
    "error": ["NullPointerException", "undefined variable", "type mismatch", "syntax error", "import error"],
    "pattern": ["dependency injection", "the observer pattern", "MVC architecture", "functional programming", "async/await"],
    "data_structure": ["a binary search tree", "a hash map", "a priority queue", "a trie", "a graph"],
    "algorithm_type": ["sorting", "searching", "dynamic programming", "greedy", "backtracking"],
    "purpose": ["managing user sessions", "handling payments", "caching results", "logging events", "authentication"],
    "issue": ["memory leak", "race condition", "infinite loop", "null reference", "buffer overflow"],
    "language_a": ["Python", "Java", "C#", "Ruby"],
    "language_b": ["JavaScript", "Go", "Rust", "Kotlin"],
    "functionality": ["user registration", "file uploads", "real-time chat", "search", "notifications"],
    "calculation": ["compound interest over 10 years", "the standard deviation", "eigenvalues of this matrix", "a Fourier transform"],
    "equation": ["3x² - 2x + 1 = 0", "sin(x) = cos(x)", "e^x = x²", "ln(x) = 2"],
    "math_operation": ["mean", "median", "mode", "variance", "standard deviation", "correlation"],
    "values": ["these numbers", "the dataset", "the samples", "the observations"],
    "theorem": ["the Pythagorean theorem", "Fermat's Last Theorem", "the fundamental theorem of calculus"],
    "event": ["rolling doubles with two dice", "drawing a royal flush", "getting at least one heads in 3 flips"],
    "statistic": ["95% confidence interval", "p-value", "effect size", "chi-squared statistic"],
    "optimization_type": ["linear programming", "convex optimization", "integer programming", "genetic algorithm"],
    "proof_type": ["induction", "contradiction", "direct", "cases"],
    "value": ["π", "e", "√2", "ln(2)"],
    "precision": ["0.01", "0.001", "1%", "3 decimal places"],
    "sequence": ["this series", "the recursive formula", "the iterative method"],
    "statement": ["all primes greater than 2 are odd", "√2 is irrational", "there are infinitely many primes"],
    "argument": ["this political claim", "this advertisement", "this conspiracy theory"],
    "syllogism": ["All A are B. All B are C. Therefore all A are C.", "Some X are Y. No Y are Z. Therefore some X are not Z."],
    "set_of_statements": ["these three claims", "the witness testimonies", "the system requirements"],
    "expressions": ["A ∧ (B ∨ C) and (A ∧ B) ∨ (A ∧ C)", "¬(A ∧ B) and ¬A ∨ ¬B"],
    "premises": ["these assumptions", "the given conditions", "the experimental data"],
    "genre": ["haiku", "sonnet", "short story", "poem", "dialogue"],
    "topic": ["artificial intelligence", "space exploration", "lost love", "nature", "technology"],
    "number": ["5", "10", "20", "50"],
    "purpose": ["a marketing campaign", "a product launch", "a team building event"],
    "creative_type": ["logo", "character", "scene", "world", "system"],
    "context": ["a fantasy RPG", "a sci-fi movie", "a mystery novel", "a children's book"],
    "design_target": ["a mobile app UI", "a brand identity", "a dashboard layout", "an icon set"],
    "naming_context": ["a new programming language", "a tech startup", "a product line"],
    "content_type": ["a thriller", "a romance", "a sci-fi adventure", "a comedy"],
    "problem": ["reducing carbon emissions", "improving education access", "sustainable food production"],
    "content": ["a song", "a speech", "a letter", "a recipe"],
    "style": ["Shakespeare", "Hemingway", "Dr. Seuss", "a technical manual"],
    "persona": ["a medieval knight", "an alien visitor", "a time traveler", "a detective"],
    "scenario": ["your first day on Earth", "a typical morning", "encountering modern technology"],
    "project_type": ["a board game", "a mobile app", "a community space", "a learning platform"],
    "dataset": ["this sales data", "the customer survey", "the website analytics"],
    "relationship": ["correlations", "patterns", "outliers", "trends"],
    "data": ["this table", "the results", "the records"],
    "condition": ["values > 100", "status = active", "date within last month"],
    "records": ["transactions", "users", "events", "sessions"],
    "dimension": ["region", "category", "month", "user type"],
    "issues": ["missing values", "duplicates", "outliers", "inconsistent formats"],
    "metric": ["the rolling average", "cumulative sum", "year-over-year growth"],
    "time_period": ["the last 30 days", "Q3 2024", "the past year"],
    "table_a": ["orders", "users", "products"],
    "table_b": ["customers", "purchases", "categories"],
    "key": ["user_id", "order_id", "product_id"],
    "variable": ["age", "income", "purchase_amount", "session_duration"],
    "time_series": ["these stock prices", "the website traffic", "the temperature readings"],
    "data_source": ["this log file", "the sensor data", "the transaction history"],
    "source": ["this research paper", "the meta-analysis", "the review article"],
    "approach_a": ["supervised learning", "REST APIs", "monolithic architecture"],
    "approach_b": ["unsupervised learning", "GraphQL", "microservices"],
    "methodology": ["this experimental design", "the survey methodology", "the analysis approach"],
    "sources": ["these websites", "the cited papers", "the expert interviews"],
    "number": ["3", "5", "10"],
    "topic": ["transformer architectures", "climate change", "economic policy"],
    "research_area": ["reinforcement learning", "quantum computing", " CRISPR applications"],
    "study": ["this psychology experiment", "the clinical trial", "the observational study"],
    "hypothesis": ["sleep improves memory", "social media affects mental health", "exercise reduces anxiety"],
    "text": ["this philosophical essay", "the legal document", "the policy brief"],
    "claim": ["correlation implies causation", "organic food is healthier", "AI will replace all jobs"],
    "project": ["a mobile app launch", "a website redesign", "a database migration"],
    "timeframe": ["3 months", "6 months", "1 year"],
    "criteria": ["impact and effort", "urgency and importance", "cost and benefit"],
    "goal": ["increasing user engagement", "reducing churn", "improving performance"],
    "tasks": ["these deliverables", "the milestones", "the work items"],
    "transition": ["migrating to the cloud", "adopting agile methodology", "implementing DevOps"],
    "resources": ["the budget", "the team", "the equipment"],
    "constraints": ["three teams", "limited time", "fixed costs"],
    "event": ["this product launch", "the system migration", "the conference"],
    "activity": ["content creation", "user testing", "market research"],
    "time_period": ["Q4", "the next quarter", "2024"],
    "operations": ["these manufacturing steps", "the deployment tasks", "the data migrations"],
    "objective": ["downtime", "cost", "time to completion"],
    "system_change": ["the new authentication system", "the API version upgrade", "the infrastructure migration"],
    "fact": ["the capital of Australia", "the speed of light", "the atomic number of carbon"],
    "process": ["photosynthesis", "protein synthesis", "the water cycle"],
    "accomplishment": ["invented the telephone", "wrote Romeo and Juliet", "discovered penicillin"],
    "a": ["Python", "REST", "SQL", "HTTP"],
    "b": ["JavaScript", "GraphQL", "NoSQL", "HTTPS"],
    "term": ["machine learning", "blockchain", "API", "algorithm"],
    "activity": ["regular exercise", "reading", "meditation", "sleep"],
    "technology": ["blockchain", "quantum computing", "neural networks", "CRISPR"],
    "location": ["Tokyo", "London", "Sydney", "New York"],
    "concept": ["supply and demand", "natural selection", "opportunity cost"],
    "superlative": ["the tallest", "the fastest", "the oldest", "the largest"],
    "category": ["mammal", "planet", "element", "country"],
}


def generate_task(category: TaskCategory) -> str:
    """Generate a random task for the given category."""
    templates = TASK_TEMPLATES[category]
    template = random.choice(templates)
    
    # Find all placeholders in template
    import re
    placeholders = re.findall(r'\{(\w+)\}', template)
    
    # Fill in values
    values = {}
    for ph in placeholders:
        if ph in FILL_VALUES:
            values[ph] = random.choice(FILL_VALUES[ph])
        else:
            values[ph] = "unknown"
    
    return template.format(**values)


def run_benchmark(num_tasks: int) -> dict[str, Any]:
    """Run the framework coverage benchmark."""
    logger.info(f"Starting framework coverage benchmark")
    logger.info(f"Generating {num_tasks} diverse tasks")
    
    selector = FrameworkSelector()
    
    # Track selections
    framework_counts = Counter()
    category_framework_counts = defaultdict(Counter)
    complexity_distribution = defaultdict(list)
    
    # Categories for task generation
    categories = list(TaskCategory)
    
    for i in range(num_tasks):
        # Distribute evenly across categories
        category = categories[i % len(categories)]
        
        # Generate task
        task = generate_task(category)
        
        # Run analysis
        analysis = selector.analyze(task)
        
        # Track results
        framework = analysis.recommended_framework
        framework_counts[framework] += 1
        category_framework_counts[category.value][framework] += 1
        complexity_distribution[framework].append(analysis.complexity_score)
        
        if (i + 1) % 100 == 0:
            logger.info(f"Processed {i + 1}/{num_tasks} tasks")
    
    # Calculate utilization stats
    total_frameworks = len(FRAMEWORK_REGISTRY)
    used_frameworks = len(framework_counts)
    unused_frameworks = total_frameworks - used_frameworks
    
    # Find dead frameworks
    all_framework_names = set(FRAMEWORK_REGISTRY.keys())
    used_framework_names = set(framework_counts.keys())
    dead_frameworks = sorted(all_framework_names - used_framework_names)
    
    # Calculate framework stats
    framework_stats = []
    for fw_name, count in framework_counts.most_common():
        pct = (count / num_tasks) * 100
        complexities = complexity_distribution[fw_name]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        framework_stats.append({
            "framework": fw_name,
            "selections": count,
            "percentage": round(pct, 2),
            "avg_complexity": round(avg_complexity, 2),
        })
    
    # Category breakdown
    category_breakdown = {}
    for cat, fw_counts in category_framework_counts.items():
        total = sum(fw_counts.values())
        category_breakdown[cat] = {
            "total_tasks": total,
            "top_frameworks": [
                {"framework": fw, "count": count, "pct": round((count/total)*100, 2)}
                for fw, count in fw_counts.most_common(5)
            ]
        }
    
    summary = {
        "total_tasks": num_tasks,
        "total_frameworks": total_frameworks,
        "frameworks_used": used_frameworks,
        "frameworks_unused": unused_frameworks,
        "utilization_rate": round((used_frameworks / total_frameworks) * 100, 2),
        "dead_frameworks": dead_frameworks,
        "framework_stats": framework_stats,
        "category_breakdown": category_breakdown,
    }
    
    logger.info(f"Benchmark complete. {used_frameworks}/{total_frameworks} frameworks utilized")
    if dead_frameworks:
        logger.warning(f"Dead frameworks detected: {dead_frameworks}")
    
    return summary


def generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate a markdown report from benchmark results."""
    lines = [
        "# Framework Coverage and Utilization Benchmark",
        "",
        f"**Date:** {datetime.now().isoformat()}",
        f"**Total Tasks:** {data['total_tasks']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Frameworks | {data['total_frameworks']} |",
        f"| Frameworks Used | {data['frameworks_used']} |",
        f"| Frameworks Unused | {data['frameworks_unused']} |",
        f"| Utilization Rate | {data['utilization_rate']}% |",
        "",
    ]
    
    if data['dead_frameworks']:
        lines.extend([
            "## Unused (Dead) Frameworks",
            "",
            "The following frameworks were never selected:",
            "",
        ])
        for fw in data['dead_frameworks']:
            lines.append(f"- `{fw}`")
        lines.append("")
        lines.extend([
            "*These frameworks may need:",
            "- Better capability keywords to match user intents",
            "- Lower complexity thresholds",
            "- Different category associations",
            "- Or may be candidates for removal*",
            "",
        ])
    else:
        lines.extend([
            "## Framework Utilization",
            "",
            "✓ All frameworks were selected at least once",
            "",
        ])
    
    lines.extend([
        "## Framework Selection Distribution",
        "",
        "| Rank | Framework | Selections | % of Tasks | Avg Complexity |",
        "|------|-----------|------------|------------|----------------|",
    ])
    
    for i, stat in enumerate(data['framework_stats'], 1):
        lines.append(
            f"| {i} | {stat['framework']} | {stat['selections']} | "
            f"{stat['percentage']}% | {stat['avg_complexity']} |"
        )
    
    lines.extend([
        "",
        "## Category Breakdown",
        "",
        "Top frameworks selected per category:",
        "",
    ])
    
    for cat, info in data['category_breakdown'].items():
        lines.extend([
            f"### {cat.title()}",
            "",
            f"Total tasks: {info['total_tasks']}",
            "",
            "| Framework | Count | % |",
            "|-----------|-------|---|",
        ])
        for fw in info['top_frameworks']:
            lines.append(f"| {fw['framework']} | {fw['count']} | {fw['pct']}% |")
        lines.append("")
    
    lines.extend([
        "## Analysis",
        "",
        "### Highly Utilized Frameworks",
        "",
        "Frameworks with >10% selection rate are workhorses:",
        "",
    ])
    
    workhorses = [s for s in data['framework_stats'] if s['percentage'] >= 10]
    if workhorses:
        for stat in workhorses:
            lines.append(f"- **{stat['framework']}**: {stat['percentage']}% ({stat['selections']} selections)")
    else:
        lines.append("- No framework exceeds 10% selection rate (good diversity)")
    
    lines.extend([
        "",
        "### Underutilized Frameworks",
        "",
        "Frameworks with <1% selection rate may need attention:",
        "",
    ])
    
    underutilized = [s for s in data['framework_stats'] if s['percentage'] < 1]
    if underutilized:
        for stat in underutilized[:10]:  # Show first 10
            lines.append(f"- **{stat['framework']}**: {stat['percentage']}% ({stat['selections']} selections)")
        if len(underutilized) > 10:
            lines.append(f"- ... and {len(underutilized) - 10} more")
    else:
        lines.append("- All frameworks have reasonable utilization")
    
    lines.extend([
        "",
        "## Recommendations",
        "",
    ])
    
    if data['utilization_rate'] < 50:
        lines.append("⚠ **Low utilization**: Many frameworks are not being selected.")
        lines.append("   Consider reviewing framework capability definitions.")
    elif data['utilization_rate'] < 80:
        lines.append("✓ **Moderate utilization**: Most frameworks see some use.")
        lines.append("   Some specialization is expected and healthy.")
    else:
        lines.append("✓ **High utilization**: Most frameworks are actively used.")
        lines.append("   Good coverage across the framework library.")
    
    if len(data['dead_frameworks']) > 5:
        lines.append("")
        lines.append(f"⚠ {len(data['dead_frameworks'])} frameworks never selected.")
        lines.append("   Consider removing or revising these frameworks.")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark framework coverage and utilization"
    )
    parser.add_argument(
        "--tasks",
        type=int,
        default=500,
        help="Number of tasks to generate (default: 500)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmarks/results/framework_coverage.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--markdown",
        type=str,
        default="benchmarks/results/framework_coverage.md",
        help="Output markdown report path",
    )
    args = parser.parse_args()
    
    # Run benchmark
    results = run_benchmark(args.tasks)
    
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
    print("FRAMEWORK COVERAGE BENCHMARK")
    print("=" * 60)
    print(f"Total tasks: {results['total_tasks']}")
    print(f"Frameworks used: {results['frameworks_used']}/{results['total_frameworks']}")
    print(f"Utilization rate: {results['utilization_rate']}%")
    if results['dead_frameworks']:
        print(f"Dead frameworks: {len(results['dead_frameworks'])}")
    print("-" * 60)
    print("Top 5 frameworks:")
    for stat in results['framework_stats'][:5]:
        print(f"  {stat['framework']}: {stat['percentage']}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
