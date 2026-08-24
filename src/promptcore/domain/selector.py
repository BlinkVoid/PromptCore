"""Framework Selector - Analyzes tasks and recommends reasoning strategies."""

import re
from enum import Enum
from pydantic import BaseModel, Field

from .frameworks import (
    FRAMEWORK_REGISTRY,
    ReasoningFramework,
    TaskCategory,
)


class ComplexityLevel(str, Enum):
    """Complexity levels for tasks."""
    LOW = "low"           # 0-3
    MEDIUM = "medium"     # 4-6
    HIGH = "high"         # 7-10


class TaskAnalysis(BaseModel):
    """Result of analyzing a task for framework selection."""
    
    task: str = Field(..., description="The original task text")
    category: TaskCategory = Field(..., description="Detected task category")
    complexity_score: float = Field(..., ge=0, le=10, description="Complexity score 0-10")
    complexity_level: ComplexityLevel = Field(..., description="Complexity bucket")
    recommended_framework: str = Field(..., description="Name of recommended framework")
    reasoning: str = Field(..., description="Why this framework was chosen")
    alternative_frameworks: list[str] = Field(default_factory=list, description="Other viable options")


class FrameworkSelector:
    """Analyzes tasks and selects the optimal reasoning framework."""
    
    # Keyword weights: generic domain verbs = 1, specific technical terms = 2,
    # rare/strong category markers = 3
    CATEGORY_KEYWORDS: dict[TaskCategory, dict[str, int]] = {
        TaskCategory.CODE: {
            "code": 2, "function": 2, "implement": 2, "program": 2, "debug": 2,
            "fix": 1, "refactor": 2, "class": 1, "method": 2, "api": 2,
            "algorithm": 2, "compile": 2, "syntax": 2, "bug": 2,
            "python": 2, "javascript": 2, "typescript": 2, "java": 2, "rust": 2,
            "go": 1, "sql": 2, "script": 2, "pull request": 2, "module": 2,
        },
        TaskCategory.MATH: {
            "calculate": 1, "compute": 1, "equation": 2, "formula": 2, "solve": 1,
            "math": 2, "number": 1, "sum": 1, "product": 1, "derivative": 3,
            "integral": 3, "probability": 2, "statistics": 2, "algebra": 2,
            "geometry": 2, "percentage": 1, "ratio": 1, "shortest path": 3,
            "weighted graph": 3, "statistical": 2, "significant": 1,
            "integer": 2, "infinite series": 3, "surface area": 2, "celsius": 1,
            "arranged": 1, "differential equations": 3, "proof": 2, "by induction": 3,
            "divisible": 2, "probability of": 2, "heron's formula": 3,
        },
        TaskCategory.LOGIC: {
            "prove": 2, "deduce": 2, "infer": 1, "logic": 2, "paradox": 3,
            "contradiction": 2, "valid": 2, "invalid": 2, "premise": 2,
            "conclusion": 1, "syllogism": 3, "argument": 1, "if and only if": 2,
            "therefore": 1, "implies": 1, "boolean": 2, "deductive": 2,
            "inductive": 2, "negation": 2, "flaw": 1, "logical fallacy": 3,
            "fallacy": 2, "by induction": 3, "undecidable": 3, "halting problem": 3,
        },
        TaskCategory.CREATIVE: {
            "write": 1, "create": 1, "imagine": 1, "story": 2, "poem": 2,
            "design": 1, "creative": 2, "brainstorm": 2, "innovate": 1,
            "generate ideas": 2, "narrative": 2, "art": 2, "compose": 1,
            "invent": 1, "novel": 2, "unique": 1, "original": 1, "haiku": 3,
            "limerick": 3, "plot twist": 3, "dialogue": 2, "backstory": 2,
        },
        TaskCategory.DATA: {
            "data": 2, "table": 2, "csv": 3, "json": 2, "database": 2,
            "query": 2, "filter": 1, "aggregate": 2, "group by": 3,
            "group": 1, "join": 2, "dataset": 2, "rows": 2, "columns": 2,
            "analyze data": 2, "spreadsheet": 2, "records": 1, "entries": 1,
            "revenue": 1, "sales": 1, "column": 1, "anomalies": 2,
            "features": 1, "sensor": 1, "sql": 2, "correlation": 2,
            "rolling": 2, "normalize": 1, "pivot": 2,
        },
        TaskCategory.RESEARCH: {
            "research": 3, "investigate": 2, "explore": 1, "study": 2,
            "survey": 2, "review": 1, "literature": 3, "sources": 2,
            "evidence": 2, "findings": 2, "compare": 1, "evaluate": 1,
            "assess": 1, "analyze": 1, "examine": 1,
            "methodology": 2, "limitations": 2, "synthesize": 3, "conflicting": 2,
            "longitudinal": 3, "confounding": 3, "credibility": 2,
        },
        TaskCategory.PLANNING: {
            "plan": 2, "schedule": 2, "organize": 1, "strategy": 2,
            "roadmap": 3, "timeline": 2, "steps": 1, "phases": 2,
            "milestones": 3, "project": 1, "goals": 1, "objectives": 1,
            "prioritize": 2, "allocate": 2, "coordinate": 1, "manage": 1,
            "resource": 2, "constraints": 1, "risk analysis": 2,
        },
    }

    # Phrase-level disambiguation rules: (trigger phrase, forced category, min_score_bonus)
    # Applied after keyword scoring to override frequent ambiguous verbs.
    CATEGORY_DISAMBIGUATION: list[tuple[str, TaskCategory, int]] = [
        # CODE beats CREATIVE when "write" is followed by code terms
        ("write a function", TaskCategory.CODE, 10),
        ("write a python", TaskCategory.CODE, 10),
        ("write a script", TaskCategory.CODE, 10),
        ("write a program", TaskCategory.CODE, 10),
        ("write code", TaskCategory.CODE, 10),
        ("implement", TaskCategory.CODE, 5),
        ("debug", TaskCategory.CODE, 5),
        ("refactor", TaskCategory.CODE, 5),
        # CREATIVE beats others only with creative content words
        ("write a story", TaskCategory.CREATIVE, 10),
        ("write a poem", TaskCategory.CREATIVE, 10),
        ("write a haiku", TaskCategory.CREATIVE, 10),
        ("write a limerick", TaskCategory.CREATIVE, 10),
        ("plot twist", TaskCategory.CREATIVE, 10),
        ("short story", TaskCategory.CREATIVE, 5),
        # LOGIC beats MATH for proof-style phrasing
        ("prove by induction", TaskCategory.LOGIC, 5),
        # DATA beats RESEARCH for data-specific phrasing
        ("dataset", TaskCategory.DATA, 5),
        ("this dataset", TaskCategory.DATA, 8),
        ("sql query", TaskCategory.DATA, 8),
        ("csv", TaskCategory.DATA, 5),
        # RESEARCH beats GENERAL for paper/source phrasing
        ("research paper", TaskCategory.RESEARCH, 8),
        ("literature review", TaskCategory.RESEARCH, 10),
        ("conflicting papers", TaskCategory.RESEARCH, 10),
        ("methodology", TaskCategory.RESEARCH, 5),
        ("sources", TaskCategory.RESEARCH, 5),
        # PLANNING beats RESEARCH for action-oriented phrasing
        ("roadmap", TaskCategory.PLANNING, 10),
        ("milestones", TaskCategory.PLANNING, 8),
        ("project plan", TaskCategory.PLANNING, 10),
        ("resource constraints", TaskCategory.PLANNING, 8),
    ]

    # Complexity indicators
    COMPLEXITY_BOOSTERS: list[tuple[str, float]] = [
        (r"\b(complex|complicated|difficult|challenging|hard)\b", 1.5),
        (r"\b(multiple|several|many|various)\b", 0.8),
        (r"\b(optimize|optimize|efficient|performance)\b", 1.0),
        (r"\b(edge cases?|corner cases?|exceptions?)\b", 1.2),
        (r"\b(concurrent|parallel|async|distributed)\b", 1.5),
        (r"\b(security|authentication|authorization)\b", 1.2),
        (r"\b(integrate|integration|combine)\b", 0.8),
        (r"\band\b.*\band\b.*\band\b", 1.0),  # Multiple "and"s suggest complexity
    ]
    
    COMPLEXITY_REDUCERS: list[tuple[str, float]] = [
        (r"\b(simple|basic|easy|straightforward)\b", -1.5),
        (r"\b(single|one|just)\b", -0.5),
        (r"\b(example|sample|demo)\b", -0.8),
    ]
    # Intent indicators
    INTENT_KEYWORDS: dict[str, list[str]] = {
        # Existing intents
        "exploration": ["explore", "brainstorm", "options", "alternatives", "possibilities", "paths", "strategies", "ideas"],
        "step_by_step": ["step by step", "how to", "process", "guide", "walkthrough", "procedure", "instructions"],
        "decomposition": ["break down", "subproblems", "divide", "parts", "components", "structure", "decompose"],
        "verification": ["verify", "check", "confirm", "validate", "ensure", "double check", "audit", "consistency"],
        "structured_data": ["table", "csv", "spreadsheet", "columns", "rows", "organize data", "filter", "sort"],
        "self_correction": ["fix", "correct", "improve", "refine", "critique", "debug", "error"],
        "tool_use": ["search", "lookup", "api", "execute", "run", "query", "fetch", "get"],
        # New intents for expanded frameworks
        "abstraction": ["principle", "fundamental", "concept", "theory", "abstract", "high-level", "big picture", "underlying"],
        "summarization": ["summarize", "summary", "condense", "tldr", "brief", "digest", "key points", "overview"],
        "planning": ["plan", "schedule", "roadmap", "strategy", "milestones", "phases", "prioritize", "sequence"],
        "code_reasoning": ["compute", "calculate", "formula", "equation", "algorithm", "program", "script", "function"],
        "outlining": ["outline", "skeleton", "draft", "structure first", "framework", "organize", "sections"],
        "persona": ["act as", "role", "expert", "pretend", "you are a", "imagine you", "perspective of"],
        "clarification": ["clarify", "rephrase", "rewrite", "what do you mean", "explain again", "simplify"],
        "perspective_taking": ["perspective", "point of view", "think like", "empathy", "viewpoint", "standpoint"],
        "error_awareness": ["pitfall", "mistake", "wrong", "avoid", "common error", "misconception", "trap"],
        "iterative_improvement": ["iterate", "revise", "draft", "polish", "version", "v2", "better", "enhance"],
        "confidence_estimation": ["how sure", "confidence", "certain", "probability", "likelihood", "reliable"],
        "graph_reasoning": ["graph", "network", "connections", "merge", "nodes", "relationships", "non-linear"],
    }

    # Plausible frameworks per category+complexity tier (GENERAL intentionally unconstrained)
    CATEGORY_TIERS: dict[TaskCategory, dict[ComplexityLevel, set[str]]] = {
        TaskCategory.CODE: {
            ComplexityLevel.LOW: {"chain_of_thought"},
            ComplexityLevel.MEDIUM: {"program_of_thoughts", "analogical", "self_ask", "self_refine", "contrastive_cot", "chain_of_draft"},
            ComplexityLevel.HIGH: {"plan_and_solve", "least_to_most", "reflexion", "faithful_cot", "recursion_of_thought", "critic", "chain_of_code"},
        },
        TaskCategory.MATH: {
            ComplexityLevel.LOW: {"chain_of_thought", "chain_of_draft", "re2_re_reading"},
            ComplexityLevel.MEDIUM: {"program_of_thoughts", "chain_of_thought", "tab_cot", "self_consistency"},
            ComplexityLevel.HIGH: {"least_to_most", "complexity_based", "cumulative_reasoning", "meta_cot", "reverse_cot", "chain_of_code", "chain_of_abstraction"},
        },
        TaskCategory.LOGIC: {
            ComplexityLevel.LOW: {"chain_of_thought", "prompt_paraphrasing", "chain_of_draft", "re2_re_reading"},
            ComplexityLevel.MEDIUM: {"chain_of_thought", "sim_to_m", "step_back", "contrastive_cot", "system2_attention"},
            ComplexityLevel.HIGH: {"maieutic", "meta_cot", "tree_of_thoughts", "cumulative_reasoning", "self_ask", "self_discover", "chain_of_code"},
        },
        TaskCategory.CREATIVE: {
            ComplexityLevel.LOW: {"role_prompting", "emotion_prompting"},
            ComplexityLevel.MEDIUM: {"directional_stimulus", "analogical", "skeleton_of_thought", "role_prompting", "chain_of_draft", "deliberate_then_generate"},
            ComplexityLevel.HIGH: {"tree_of_thoughts", "skeleton_of_thought", "self_refine", "deliberate_then_generate"},
        },
        TaskCategory.DATA: {
            ComplexityLevel.LOW: {"chain_of_table", "tab_cot"},
            ComplexityLevel.MEDIUM: {"chain_of_table", "thread_of_thought", "program_of_thoughts", "tab_cot", "chain_of_abstraction", "chain_of_code"},
            ComplexityLevel.HIGH: {"react", "plan_and_solve", "chain_of_density", "contrastive_cot", "critic", "chain_of_code"},
        },
        TaskCategory.RESEARCH: {
            ComplexityLevel.LOW: {"rephrase_and_respond", "role_prompting"},
            ComplexityLevel.MEDIUM: {"step_back", "self_ask", "chain_of_verification", "thread_of_thought", "chain_of_density", "deliberate_then_generate", "chain_of_abstraction"},
            ComplexityLevel.HIGH: {"maieutic", "graph_of_thoughts", "step_back", "meta_cot", "active_prompting", "mixture_of_reasoning", "critic", "self_discover"},
        },
        TaskCategory.PLANNING: {
            ComplexityLevel.LOW: {"skeleton_of_thought", "plan_and_solve"},
            ComplexityLevel.MEDIUM: {"plan_and_solve", "least_to_most", "tree_of_thoughts", "self_ask"},
            ComplexityLevel.HIGH: {"reasoning_via_planning", "graph_of_thoughts", "tree_of_thoughts", "buffer_of_thoughts", "self_discover"},
        },
    }
    OUT_OF_TIER_PENALTY = 2.0
    INTENT_BONUS_CAP = 4.0
    
    def __init__(self):
        pass
    
    def analyze(self, task: str, context: str = "") -> TaskAnalysis:
        """Analyze a task and recommend a reasoning framework."""
        full_text = f"{task} {context}".lower()
        
        # Detect category
        category = self._detect_category(full_text)
        
        # Calculate complexity
        complexity_score = self._calculate_complexity(task, context)
        complexity_level = self._score_to_level(complexity_score)
        
        # Detect intent
        intents = self._detect_intents(full_text)
        
        # Select framework
        framework, reasoning, alternatives = self._select_framework(
            category, complexity_score, intents, full_text
        )
        
        return TaskAnalysis(
            task=task,
            category=category,
            complexity_score=round(complexity_score, 2),
            complexity_level=complexity_level,
            recommended_framework=framework,
            reasoning=reasoning,
            alternative_frameworks=alternatives,
        )
        
    def _detect_intents(self, text: str) -> list[str]:
        """Detect user intents based on keywords."""
        detected = []
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(intent)
                    break
        return detected
    
    def _detect_category(self, text: str) -> TaskCategory:
        """Detect the primary category using weighted keywords + disambiguation."""
        scores: dict[TaskCategory, float] = {cat: 0 for cat in TaskCategory}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword, weight in keywords.items():
                if keyword in text:
                    scores[category] += weight

        # Apply phrase-level disambiguation
        for phrase, category, bonus in self.CATEGORY_DISAMBIGUATION:
            if phrase in text:
                scores[category] += bonus

        best_category = max(scores, key=scores.get)  # type: ignore

        if scores[best_category] == 0:
            return TaskCategory.GENERAL

        return best_category
    
    def _calculate_complexity(self, task: str, context: str) -> float:
        """Calculate complexity score (0-10) based on heuristics."""
        full_text = f"{task} {context}"
        
        # Base complexity from length (normalized)
        word_count = len(full_text.split())
        length_score = min(word_count / 65, 3.0)  # Max 3 points from length
        
        # Sentence complexity
        sentences = re.split(r'[.!?]+', full_text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        sentence_score = min(avg_sentence_length / 10, 2.0)  # Max 2 points
        
        # Keyword boosters/reducers
        modifier_score = 0.0
        text_lower = full_text.lower()
        
        for pattern, boost in self.COMPLEXITY_BOOSTERS:
            if re.search(pattern, text_lower):
                modifier_score += boost
        
        for pattern, reduction in self.COMPLEXITY_REDUCERS:
            if re.search(pattern, text_lower):
                modifier_score += reduction  # Already negative
        
        # Question complexity (multiple questions = more complex)
        question_count = full_text.count("?")
        question_score = min(question_count * 0.5, 1.5)
        
        # Combine scores
        total = length_score + sentence_score + modifier_score + question_score
        
        # Add base complexity of 1
        total += 1.0
        
        # Clamp to 0-10
        return max(0.0, min(10.0, total))
    
    def _score_to_level(self, score: float) -> ComplexityLevel:
        """Convert numeric score to complexity level."""
        if score <= 3:
            return ComplexityLevel.LOW
        elif score <= 6:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.HIGH
    
    def _select_framework(
        self, 
        category: TaskCategory, 
        complexity: float,
        intents: list[str],
        text: str
    ) -> tuple[str, str, list[str]]:
        """Select the best framework based on intent, category and complexity."""
        
        candidates: list[tuple[type[ReasoningFramework], float, str]] = []

        tier = self.CATEGORY_TIERS.get(category)
        allowed = tier.get(self._score_to_level(complexity)) if tier else None

        for framework_cls in FRAMEWORK_REGISTRY.values():
            score = 0.0
            reasons = []

            # 1. Intent match, capped aggregate bonus
            matched_intents = [
                i for i in intents if i in framework_cls.capabilities
            ]
            if matched_intents:
                score += self.INTENT_BONUS_CAP
                reasons.append(f"matches intent(s) {matched_intents}")

            # 2. Category match
            if category in framework_cls.best_for:
                score += 2.0
                reasons.append(f"matches {category.value} category")

            # 3. Complexity fit
            if complexity >= framework_cls.complexity_threshold:
                score += 2.0
                overkill = (complexity - framework_cls.complexity_threshold) * 0.75
                score -= min(overkill, 3.0)
                reasons.append("complexity fit")
            else:
                score -= 2.0

            # 4. Tier gating
            if allowed is not None and framework_cls.name not in allowed:
                score -= self.OUT_OF_TIER_PENALTY

            candidates.append((framework_cls, score, "; ".join(reasons) if reasons else "default option"))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Best choice
        best = candidates[0]
        
        # Alternatives (next best scorers, regardless of sign so tier penalties
        # don't hide viable options from top-3 consideration)
        alternatives = [
            c[0].name for c in candidates[1:4]
        ]
        
        reasoning = f"Selected {best[0].name}: {best[2]}"
        
        return best[0].name, reasoning, alternatives
