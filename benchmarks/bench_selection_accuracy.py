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
    {"task": "Fix this SQL query that's running slowly on large datasets.", "category": TaskCategory.CODE, "expert_framework": "self_refine", "complexity": 6},
    {"task": "Create a React hook for managing form state with validation.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Build a distributed rate limiter that works across multiple servers.", "category": TaskCategory.CODE, "expert_framework": "tree_of_thoughts", "complexity": 9},
    {"task": "Optimize this algorithm from O(n²) to O(n log n).", "category": TaskCategory.CODE, "expert_framework": "analogical", "complexity": 7},
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
    {"task": "Determine if these two boolean expressions are logically equivalent.", "category": TaskCategory.LOGIC, "expert_framework": "contrastive_cot", "complexity": 5},
    {"task": "Find the contradiction in this set of statements.", "category": TaskCategory.LOGIC, "expert_framework": "self_ask", "complexity": 6},
    {"task": "If P implies Q and not-Q is true, what can we conclude about P?", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Evaluate this complex nested conditional statement.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Is this reasoning deductive or inductive? Explain why.", "category": TaskCategory.LOGIC, "expert_framework": "step_back", "complexity": 5},
    {"task": "Spot the flaw in this proof that 1 = 2.", "category": TaskCategory.LOGIC, "expert_framework": "reverse_cot", "complexity": 6},
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
    {"task": "Detect anomalies in this network traffic log.", "category": TaskCategory.DATA, "expert_framework": "contrastive_cot", "complexity": 7},
    
    # RESEARCH category (12 tasks)
    {"task": "Summarize the key findings from this research paper on climate change.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_density", "complexity": 6},
    {"task": "Compare and contrast the approaches in these two studies.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive_cot", "complexity": 6},
    {"task": "What are the limitations of this experimental design?", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "complexity": 7},
    {"task": "Evaluate the credibility of these sources.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_verification", "complexity": 6},
    {"task": "Synthesize information from these five papers on transformer architectures.", "category": TaskCategory.RESEARCH, "expert_framework": "step_back", "complexity": 8},
    {"task": "What gaps exist in the current literature on reinforcement learning?", "category": TaskCategory.RESEARCH, "expert_framework": "self_ask", "complexity": 7},
    {"task": "Assess the methodology used in this psychology study.", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "complexity": 6},
    {"task": "Review the evidence for and against this hypothesis.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive_cot", "complexity": 7},
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
    {"task": "What is the capital of France?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "Explain how photosynthesis works.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "Who won the World Cup in 2018?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "What are the main differences between REST and GraphQL?", "category": TaskCategory.GENERAL, "expert_framework": "contrastive_cot", "complexity": 5},
    {"task": "Define machine learning in simple terms.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "List the benefits of regular exercise.", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "How does blockchain technology work?", "category": TaskCategory.GENERAL, "expert_framework": "analogical", "complexity": 5},
    {"task": "What time is it in Tokyo right now?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "Explain the concept of supply and demand.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},
    {"task": "What are NFTs and how do they work?", "category": TaskCategory.GENERAL, "expert_framework": "analogical", "complexity": 5},
    {"task": "Describe the water cycle.", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "Who wrote 'To Kill a Mockingbird'?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "What is the difference between HTTP and HTTPS?", "category": TaskCategory.GENERAL, "expert_framework": "contrastive_cot", "complexity": 4},
    {"task": "Explain the theory of evolution.", "category": TaskCategory.GENERAL, "expert_framework": "step_back", "complexity": 6},
    {"task": "What is the tallest mountain in the world?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "How do vaccines work?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 4},

    # --- Expansion batch (Task 2, frozen eval set): +13 per category below, +12 PLANNING, +10 GENERAL ---
    # CODE additions (13)
    {"task": "Write a bash one-liner that counts unique client IPs in an nginx access log.", "category": TaskCategory.CODE, "expert_framework": "program_of_thoughts", "complexity": 2},
    {"task": "Add validation to this function that parses user-supplied ages so it rejects negatives and non-numbers.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "acceptable": ["program_of_thoughts"], "complexity": 3},
    {"task": "Convert this callback-based file reader to use async/await.", "category": TaskCategory.CODE, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "Add cursor-based pagination to this REST endpoint that returns sorted search results.", "category": TaskCategory.CODE, "expert_framework": "least_to_most", "acceptable": ["plan_and_solve"], "complexity": 5},
    {"task": "Write integration tests for a checkout flow, mocking the payment gateway.", "category": TaskCategory.CODE, "expert_framework": "plan_and_solve", "complexity": 6},
    {"task": "Refactor these three duplicated date-formatting snippets into one shared utility.", "category": TaskCategory.CODE, "expert_framework": "step_back", "complexity": 4},
    {"task": "Figure out why this React component re-renders on every keystroke.", "category": TaskCategory.CODE, "expert_framework": "self_ask", "complexity": 5},
    {"task": "Improve this pull request: tighten naming, remove dead branches, and add docstrings.", "category": TaskCategory.CODE, "expert_framework": "self_refine", "acceptable": ["reflexion"], "complexity": 6},
    {"task": "Sequence the work to port this Python ETL pipeline to Go without breaking downstream consumers.", "category": TaskCategory.CODE, "expert_framework": "least_to_most", "acceptable": ["plan_and_solve"], "complexity": 7},
    {"task": "Design a cache-invalidation strategy for a CDN-backed product catalog with regional pricing.", "category": TaskCategory.CODE, "expert_framework": "tree_of_thoughts", "acceptable": ["graph_of_thoughts"], "complexity": 8},
    {"task": "Hunt down an intermittent memory leak in a long-running Node.js worker process.", "category": TaskCategory.CODE, "expert_framework": "reflexion", "acceptable": ["self_refine"], "complexity": 8},
    {"task": "Architect an offline-first sync engine that merges conflicting edits from many devices.", "category": TaskCategory.CODE, "expert_framework": "graph_of_thoughts", "acceptable": ["tree_of_thoughts"], "complexity": 9},
    {"task": "Implement an expression parser that handles nested parentheses and operator precedence.", "category": TaskCategory.CODE, "expert_framework": "recursion_of_thought", "acceptable": ["least_to_most"], "complexity": 7},
    {"task": "Design a retry-and-backoff policy for a flaky third-party API whose rate limits reset hourly.", "category": TaskCategory.CODE, "expert_framework": "reasoning_via_planning", "acceptable": ["plan_and_solve"], "complexity": 8},

    # MATH additions (13)
    {"task": "If a shirt costs $45 after a 25% discount, what was its original price?", "category": TaskCategory.MATH, "expert_framework": "program_of_thoughts", "complexity": 2},
    {"task": "A recipe serves 4 and calls for 350 g of flour; how much flour do I need for 7 servings?", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "acceptable": ["program_of_thoughts"], "complexity": 2},
    {"task": "Compute a 15% tip on an $83.60 bill split three ways, to the nearest cent.", "category": TaskCategory.MATH, "expert_framework": "faithful_cot", "acceptable": ["chain_of_thought"], "complexity": 3},
    {"task": "Convert 68°F to Celsius and round to one decimal place.", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 2},
    {"task": "How many distinct ways can the letters of 'LEVEL' be arranged?", "category": TaskCategory.MATH, "expert_framework": "program_of_thoughts", "complexity": 5},
    {"task": "Two dice are rolled; what is the probability the sum is 8 given that at least one die shows a 5?", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "acceptable": ["faithful_cot"], "complexity": 6},
    {"task": "Solve the recurrence T(n) = 2T(n/2) + n by unrolling it step by step.", "category": TaskCategory.MATH, "expert_framework": "least_to_most", "complexity": 5},
    {"task": "Estimate how many piano tuners work in Chicago, then state your confidence in the estimate.", "category": TaskCategory.MATH, "expert_framework": "self_calibration", "complexity": 6},
    {"task": "Find all integer pairs (x, y) with 3x + 4y = 41 and x, y > 0.", "category": TaskCategory.MATH, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Determine whether the infinite series Σ 1/(n·ln n) converges or diverges.", "category": TaskCategory.MATH, "expert_framework": "cumulative_reasoning", "complexity": 7},
    {"task": "You have two ropes that each burn for exactly 60 minutes but non-uniformly. Measure exactly 45 minutes.", "category": TaskCategory.MATH, "expert_framework": "tree_of_thoughts", "acceptable": ["mixture_of_reasoning"], "complexity": 8},
    {"task": "Prove that among any 13 people, at least two share a birth month.", "category": TaskCategory.MATH, "expert_framework": "meta_cot", "acceptable": ["step_back"], "complexity": 7},
    {"task": "Minimize the surface area of an open-top box with a volume of 1000 cm³.", "category": TaskCategory.MATH, "expert_framework": "mixture_of_reasoning", "acceptable": ["tree_of_thoughts"], "complexity": 8},

    # LOGIC additions (13)
    {"task": "What comes next in the sequence 2, 4, 8, 16, ...? Justify your answer.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 2},
    {"task": "Is 'some dogs are not trained' the logical negation of 'all dogs are trained'?", "category": TaskCategory.LOGIC, "expert_framework": "self_ask", "complexity": 3},
    {"task": "Which syllogism form is valid: (a) All A are B, X is A, therefore X is B; or (b) All A are B, X is B, therefore X is A?", "category": TaskCategory.LOGIC, "expert_framework": "contrastive_cot", "acceptable": ["chain_of_thought"], "complexity": 3},
    {"task": "If today is Thursday, what day comes three days after the day before yesterday?", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "Knights always tell the truth and knaves always lie. An islander says 'I am a knave.' What is he?", "category": TaskCategory.LOGIC, "expert_framework": "self_ask", "complexity": 5},
    {"task": "Four friends each rank five movies; given their pairwise disagreements, reconstruct everyone's full ranking.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_thought", "complexity": 5},
    {"task": "Given alibi timelines that partially conflict, determine which of five suspects must be lying.", "category": TaskCategory.LOGIC, "expert_framework": "tree_of_thoughts", "complexity": 6},
    {"task": "Identify the implicit premise this argument depends on but never states.", "category": TaskCategory.LOGIC, "expert_framework": "step_back", "acceptable": ["meta_cot"], "complexity": 5},
    {"task": "Verify each inference step in this legal-style argument chain and flag any unsupported leaps.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_verification", "complexity": 6},
    {"task": "Does the barber paradox reveal a genuine contradiction or rest on a faulty premise? Resolve it.", "category": TaskCategory.LOGIC, "expert_framework": "cumulative_reasoning", "acceptable": ["tree_of_thoughts"], "complexity": 8},
    {"task": "Analyze this modal argument about necessity and possibility for equivocation on the word 'must'.", "category": TaskCategory.LOGIC, "expert_framework": "meta_cot", "acceptable": ["step_back"], "complexity": 8},
    {"task": "Eight constraint clues describe a tournament schedule; derive the full fixture list or prove it inconsistent.", "category": TaskCategory.LOGIC, "expert_framework": "graph_of_thoughts", "complexity": 8},
    {"task": "Evaluate whether this Bayesian argument commits the base-rate fallacy, showing both analyses side by side.", "category": TaskCategory.LOGIC, "expert_framework": "contrastive_cot", "complexity": 7},

    # CREATIVE additions (13)
    {"task": "Write a bedtime story about a sleepy dragon for a 4-year-old.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "acceptable": ["emotion_prompting"], "complexity": 3},
    {"task": "Compose a short encouraging note for a friend who failed their driving test.", "category": TaskCategory.CREATIVE, "expert_framework": "emotion_prompting", "complexity": 2},
    {"task": "As a pirate captain, announce to your crew that rum rations are being halved.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 2},
    {"task": "Write hint-only clues for a children's scavenger hunt around the house.", "category": TaskCategory.CREATIVE, "expert_framework": "directional_stimulus", "acceptable": ["analogical"], "complexity": 3},
    {"task": "Write a limerick about a cat who steals socks.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 2},
    {"task": "Describe the internet to a medieval blacksmith using only farming metaphors.", "category": TaskCategory.CREATIVE, "expert_framework": "analogical", "complexity": 3},
    {"task": "Write a best man's speech that teases the groom without embarrassing him.", "category": TaskCategory.CREATIVE, "expert_framework": "role_prompting", "complexity": 5},
    {"task": "Draft a heartfelt resignation letter thanking a team you loved working with.", "category": TaskCategory.CREATIVE, "expert_framework": "emotion_prompting", "acceptable": ["role_prompting"], "complexity": 4},
    {"task": "Create mood-board keywords for a noir graphic novel set in rainy Lisbon.", "category": TaskCategory.CREATIVE, "expert_framework": "directional_stimulus", "complexity": 5},
    {"task": "Compress this 300-word bio into punchier versions at 150, 75, and 30 words.", "category": TaskCategory.CREATIVE, "expert_framework": "chain_of_density", "complexity": 4},
    {"task": "Sketch six taglines for an eco-friendly sneaker launch, then flesh out the two best ones.", "category": TaskCategory.CREATIVE, "expert_framework": "skeleton_of_thought", "complexity": 5},
    {"task": "Generate five distinct plot twists for a heist story and pick the most surprising yet coherent one.", "category": TaskCategory.CREATIVE, "expert_framework": "self_consistency", "acceptable": ["demonstration_ensembling"], "complexity": 6},
    {"task": "Weave three separate character arcs into one novel outline where their storylines converge.", "category": TaskCategory.CREATIVE, "expert_framework": "graph_of_thoughts", "acceptable": ["cumulative_reasoning"], "complexity": 7},

    # DATA additions (13)
    {"task": "From this table, list all orders placed in March sorted by amount.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 3},
    {"task": "Count how many rows in this dataset have a missing value in the 'email' column.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 2},
    {"task": "Compute the median and mode of this list of delivery times.", "category": TaskCategory.DATA, "expert_framework": "program_of_thoughts", "complexity": 3},
    {"task": "Cross-tabulate these survey responses by age group and satisfaction level.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "complexity": 5},
    {"task": "Using this pricing table, compute each invoice total with tiered discounts applied.", "category": TaskCategory.DATA, "expert_framework": "tab_cot", "acceptable": ["chain_of_table"], "complexity": 5},
    {"task": "De-duplicate customer records where names match but emails differ, and document your merge rules.", "category": TaskCategory.DATA, "expert_framework": "plan_and_solve", "complexity": 6},
    {"task": "Walk through this streaming sensor buffer segment by segment and note where drift begins.", "category": TaskCategory.DATA, "expert_framework": "thread_of_thought", "complexity": 6},
    {"task": "Decide which of these three features to drop before running the regression, given the collinearity stats.", "category": TaskCategory.DATA, "expert_framework": "chain_of_thought", "complexity": 6},
    {"task": "Before crunching this A/B test dump, identify which metric definitions could distort the comparison.", "category": TaskCategory.DATA, "expert_framework": "step_back", "complexity": 7},
    {"task": "Compare z-score versus IQR methods for flagging outliers in this sensor dataset and report where they disagree.", "category": TaskCategory.DATA, "expert_framework": "contrastive_cot", "complexity": 6},
    {"task": "From this multi-sheet workbook, build a cohort retention matrix grouped by signup month.", "category": TaskCategory.DATA, "expert_framework": "chain_of_table", "acceptable": ["program_of_thoughts"], "complexity": 8},
    {"task": "Rate your confidence in each insight you draw from this 40-row sample before recommending action.", "category": TaskCategory.DATA, "expert_framework": "self_calibration", "complexity": 7},
    {"task": "Model relationships across these five joined tables and explain why nightly revenue aggregates disagree with finance's numbers.", "category": TaskCategory.DATA, "expert_framework": "graph_of_thoughts", "complexity": 8},

    # RESEARCH additions (13)
    {"task": "Summarize this paper's abstract in plain language for a general audience.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_thought", "complexity": 3},
    {"task": "List peer-reviewed databases where I can find studies on sleep and memory consolidation.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_thought", "complexity": 2},
    {"task": "Acting as a research librarian, show me how to structure a literature-search query on urban heat islands.", "category": TaskCategory.RESEARCH, "expert_framework": "role_prompting", "complexity": 3},
    {"task": "Question each assumption behind this study's operationalization of 'productivity'.", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "complexity": 6},
    {"task": "Trace how the argument in this essay builds from paragraph to paragraph.", "category": TaskCategory.RESEARCH, "expert_framework": "thread_of_thought", "complexity": 5},
    {"task": "Fact-check these five cited claims about vitamin D and verify each against its source type.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_verification", "complexity": 6},
    {"task": "State how confident you are in each takeaway from this preliminary study, and why.", "category": TaskCategory.RESEARCH, "expert_framework": "self_calibration", "complexity": 5},
    {"task": "Draw parallels between the replication crisis in psychology and current issues in AI benchmarking.", "category": TaskCategory.RESEARCH, "expert_framework": "analogical", "complexity": 6},
    {"task": "Step back from individual deep-learning papers and characterize how the field's core assumptions shifted over the last decade.", "category": TaskCategory.RESEARCH, "expert_framework": "step_back", "complexity": 8},
    {"task": "Weigh the competing evidence on whether moderate caffeine intake helps or harms long-term heart health.", "category": TaskCategory.RESEARCH, "expert_framework": "contrastive_cot", "complexity": 7},
    {"task": "Map the rival hypotheses for why the Harappan civilization declined and weigh the archaeological evidence for each.", "category": TaskCategory.RESEARCH, "expert_framework": "tree_of_thoughts", "acceptable": ["graph_of_thoughts"], "complexity": 8},
    {"task": "Interrogate whether this economics paper's identification strategy actually supports its causal headline.", "category": TaskCategory.RESEARCH, "expert_framework": "maieutic", "acceptable": ["meta_cot"], "complexity": 8},
    {"task": "Assess whether the conclusions of this meta-analysis actually follow from its inclusion criteria.", "category": TaskCategory.RESEARCH, "expert_framework": "meta_cot", "complexity": 7},

    # PLANNING additions (12)
    {"task": "Plan a weekend study schedule to prepare for a Saturday morning exam.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "complexity": 3},
    {"task": "Break 'clean out the garage this weekend' into small ordered steps.", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "complexity": 2},
    {"task": "Sketch a bare-bones outline for a 20-minute conference talk on caching basics.", "category": TaskCategory.PLANNING, "expert_framework": "skeleton_of_thought", "complexity": 3},
    {"task": "Help me choose between three job offers with different salary, growth, and location trade-offs.", "category": TaskCategory.PLANNING, "expert_framework": "tree_of_thoughts", "complexity": 6},
    {"task": "Organize a two-week sprint that has to absorb an unplanned production incident fix.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "complexity": 5},
    {"task": "Plan a cross-country road trip, adjusting each day's route for weather and road closures as updates arrive.", "category": TaskCategory.PLANNING, "expert_framework": "react", "complexity": 6},
    {"task": "What questions must we answer before committing to a company-wide remote-work policy?", "category": TaskCategory.PLANNING, "expert_framework": "self_ask", "complexity": 5},
    {"task": "Devise a plan to cut cloud spend 30% within two quarters without stalling feature work.", "category": TaskCategory.PLANNING, "expert_framework": "reasoning_via_planning", "acceptable": ["plan_and_solve"], "complexity": 6},
    {"task": "Sequence the steps to migrate a blog from WordPress to a static site generator.", "category": TaskCategory.PLANNING, "expert_framework": "least_to_most", "complexity": 6},
    {"task": "Allocate a fixed engineering budget across maintenance, tech debt, and new bets for next year.", "category": TaskCategory.PLANNING, "expert_framework": "tree_of_thoughts", "acceptable": ["reasoning_via_planning"], "complexity": 8},
    {"task": "Coordinate a product launch across engineering, marketing, and support under hard regulatory deadlines.", "category": TaskCategory.PLANNING, "expert_framework": "plan_and_solve", "acceptable": ["reasoning_via_planning"], "complexity": 7},
    {"task": "Restructure our incident-response process, accounting for interdependent on-call rotations and escalation paths.", "category": TaskCategory.PLANNING, "expert_framework": "graph_of_thoughts", "acceptable": ["tree_of_thoughts"], "complexity": 8},

    # GENERAL additions (10)
    {"task": "What is the chemical symbol for gold?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "Who painted 'The Starry Night'?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "Why does ice float on water?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "acceptable": ["step_back"], "complexity": 3},
    {"task": "How many minutes are there in a week?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "complexity": 2},
    {"task": "In plain terms, what does a DNS server do?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "acceptable": ["role_prompting"], "complexity": 3},
    {"task": "What currency is used in Japan?", "category": TaskCategory.GENERAL, "expert_framework": "role_prompting", "acceptable": ["rephrase_and_respond", "prompt_paraphrasing", "system2_attention"], "complexity": 1},
    {"task": "Explain what an API is using a restaurant analogy.", "category": TaskCategory.GENERAL, "expert_framework": "analogical", "complexity": 3},
    {"task": "Roughly how tall is the Eiffel Tower compared to a football field?", "category": TaskCategory.GENERAL, "expert_framework": "chain_of_thought", "acceptable": ["prompt_paraphrasing"], "complexity": 2},
    {"task": "What is the difference between weather and climate?", "category": TaskCategory.GENERAL, "expert_framework": "contrastive_cot", "complexity": 4},
    {"task": "Why do cities tend to be warmer than the surrounding countryside?", "category": TaskCategory.GENERAL, "expert_framework": "step_back", "acceptable": ["chain_of_thought"], "complexity": 5},

    # --- Modern frameworks batch (Task 7, post-2023 wave): 19 tasks ---
    # chain_of_draft
    {"task": "Briefly compute the average of 17, 23, 31, and 49, showing each working step in under five words.", "category": TaskCategory.MATH, "expert_framework": "chain_of_draft", "acceptable": ["chain_of_thought"], "complexity": 3},
    {"task": "Return the kth largest element of this list in code, keeping each reasoning step terse and condensed.", "category": TaskCategory.CODE, "expert_framework": "chain_of_draft", "acceptable": ["chain_of_thought", "program_of_thoughts"], "complexity": 4},
    {"task": "Give a terse, condensed proof that the sum of two odd integers is even.", "category": TaskCategory.LOGIC, "expert_framework": "chain_of_draft", "acceptable": ["chain_of_thought"], "complexity": 3},
    # re2_re_reading
    {"task": "Solve: a train leaves at 14:03 traveling 80 km/h; another leaves at 15:00 at 100 km/h. When does the second catch up?", "category": TaskCategory.MATH, "expert_framework": "re2_re_reading", "acceptable": ["chain_of_thought"], "complexity": 4},
    {"task": "If the statement 'not all glorks are fleems' is true, must the conclusion 'some glorks are not fleems' follow?", "category": TaskCategory.LOGIC, "expert_framework": "re2_re_reading", "acceptable": ["chain_of_thought", "self_ask", "prompt_paraphrasing"], "complexity": 3},
    {"task": "Clarify what this question is really asking by re-reading it slowly, then answer: if today is Wednesday, what day of the week is it 100 days later?", "category": TaskCategory.LOGIC, "expert_framework": "re2_re_reading", "acceptable": ["chain_of_thought", "rephrase_and_respond", "system2_attention"], "complexity": 3},
    {"task": "Read the question twice before answering: how many months have 28 days?", "category": TaskCategory.GENERAL, "expert_framework": "re2_re_reading", "acceptable": ["role_prompting", "rephrase_and_respond", "prompt_paraphrasing", "system2_attention", "chain_of_thought"], "complexity": 1},
    # critic
    {"task": "Fact-check this complex literature review using external sources: verify every citation against the original study, assess the evidence, and correct any claim that fails verification.", "category": TaskCategory.RESEARCH, "expert_framework": "critic", "acceptable": ["chain_of_verification"], "complexity": 7},
    {"task": "Audit this complex analytics dashboard: verify each metric against the raw event records, trace mismatches across the joined tables, and correct the tracking logic; several metrics combine multiple event streams.", "category": TaskCategory.DATA, "expert_framework": "critic", "acceptable": ["chain_of_verification", "self_calibration"], "complexity": 7},
    {"task": "Debug this challenging distributed worker queue with tricky edge cases: verify each hypothesized cause against the stack traces, then correct the root cause without breaking the public API.", "category": TaskCategory.CODE, "expert_framework": "critic", "acceptable": ["reflexion", "react"], "complexity": 7},
    # chain_of_code
    {"task": "Write a Python script that computes checksums for huge log files on a distributed cluster; where a step cannot be executed directly, emulate it in pseudocode, combining real execution with simulated semantic functions.", "category": TaskCategory.CODE, "expert_framework": "chain_of_code", "acceptable": ["program_of_thoughts"], "complexity": 7},
    {"task": "This is a difficult computation: compute the determinant of this complex 4x4 matrix by writing and executing short code for each cofactor expansion, combining numeric fragments into a single program, and emulating any semantic sub-step in pseudocode.", "category": TaskCategory.MATH, "expert_framework": "chain_of_code", "acceptable": ["program_of_thoughts"], "complexity": 7},
    {"task": "Group these purchase records by customer and compute lifetime totals; express each aggregation step as runnable code or pseudocode.", "category": TaskCategory.DATA, "expert_framework": "chain_of_code", "acceptable": ["program_of_thoughts", "chain_of_table"], "complexity": 6},
    # chain_of_abstraction
    {"task": "Reason about this physics problem using abstract placeholders like y1 and y2 for each unknown quantity, then infill their concrete values from the given data at the end.", "category": TaskCategory.MATH, "expert_framework": "chain_of_abstraction", "acceptable": ["least_to_most", "chain_of_thought"], "complexity": 7},
    {"task": "Explain the underlying theoretical model of this research paper using abstract variables for each key quantity, then ground them with cited evidence from several sources.", "category": TaskCategory.RESEARCH, "expert_framework": "chain_of_abstraction", "acceptable": ["chain_of_density", "thread_of_thought", "step_back"], "complexity": 6},
    # deliberate_then_generate
    {"task": "Write an original tagline for a new brand, then deliberately critique a flawed version of it, listing several common mistakes and pitfalls, before composing the final polished line.", "category": TaskCategory.CREATIVE, "expert_framework": "deliberate_then_generate", "acceptable": ["self_refine", "skeleton_of_thought"], "complexity": 5},
    {"task": "Before writing the final answer, point out the common mistakes a hasty response would typically make, then generate a clean final answer: propose a fair policy for splitting a dinner bill among friends with very different income levels and several dietary edge cases.", "category": TaskCategory.GENERAL, "expert_framework": "deliberate_then_generate", "acceptable": ["self_refine", "contrastive_cot"], "complexity": 5},
    # self_discover
    {"task": "Design a challenging strategy to coordinate a complex multi-quarter roadmap across four product teams with several competing dependencies and regulatory edge cases: first compose a custom reasoning structure tailored to this planning problem, then apply it to prioritize milestones, allocate resources, and sequence the phases.", "category": TaskCategory.PLANNING, "expert_framework": "self_discover", "acceptable": ["reasoning_via_planning", "tree_of_thoughts", "plan_and_solve"], "complexity": 8},
    {"task": "Devise a strategy to prove this challenging conjecture about deeply nested quantifiers and subtle edge cases: first compose your own custom reasoning procedure tailored to the theorem, then execute it step by step to reach a rigorous conclusion.", "category": TaskCategory.LOGIC, "expert_framework": "self_discover", "acceptable": ["tree_of_thoughts", "meta_cot", "self_ask"], "complexity": 8},
]


def validate_labels() -> None:
    """Fail fast if any ground-truth label is not a registered framework."""
    valid = set(FRAMEWORK_REGISTRY.keys())
    for tc in TEST_TASKS:
        labels = [tc["expert_framework"]] + tc.get("acceptable", [])
        bad = [l for l in labels if l not in valid]
        if bad:
            raise ValueError(f"Invalid framework labels {bad} in task: {tc['task'][:60]}")

    # Quota checks: ~25 per category, spread over complexity bands
    from collections import Counter
    cat_counts = Counter(tc["category"].value for tc in TEST_TASKS)
    band_counts = Counter(
        "low" if tc["complexity"] <= 3 else "mid" if tc["complexity"] <= 6 else "high"
        for tc in TEST_TASKS
    )
    for cat in TaskCategory:
        n = cat_counts[cat.value]
        assert 20 <= n <= 30, f"{cat.value}: {n} tasks, expected 20-30"
    assert band_counts["low"] >= 40 and band_counts["mid"] >= 60 and band_counts["high"] >= 40, band_counts
    # Acceptable sets must never contain the expert label itself duplicated
    for tc in TEST_TASKS:
        assert tc["expert_framework"] not in tc.get("acceptable", [])


def run_benchmark() -> dict[str, Any]:
    """Run the framework selection accuracy benchmark."""
    validate_labels()
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
        
        # Check exact match (predicted is the expert choice OR in its acceptable set)
        acceptable = set(test_case.get("acceptable", []))
        exact_match = (
            analysis.recommended_framework == expert_framework
            or analysis.recommended_framework in acceptable
        )
        if exact_match:
            exact_matches += 1

        # Check top-3 match (expert choice or any acceptable choice in top 3)
        top3_set = set(analysis.alternative_frameworks[:3])
        top3_match = (
            expert_framework in top3_set
            or bool(top3_set & acceptable)
            or exact_match
        )
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
