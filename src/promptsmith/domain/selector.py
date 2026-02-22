"""Framework Selector - Analyzes tasks and recommends reasoning strategies."""

import re
from enum import Enum
from pydantic import BaseModel, Field

from .frameworks import (
    TaskCategory,
    ReasoningFramework,
    FRAMEWORK_REGISTRY,
    ChainOfThought,
    TreeOfThoughts,
    ChainOfTable,
    LeastToMost,
    SelfConsistency,
    Maieutic,
    DirectionalStimulus,
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
    
    # Keywords for category detection
    CATEGORY_KEYWORDS: dict[TaskCategory, list[str]] = {
        TaskCategory.CODE: [
            "code", "function", "implement", "program", "debug", "fix", "refactor",
            "class", "method", "api", "algorithm", "compile", "syntax", "bug",
            "python", "javascript", "typescript", "java", "rust", "go", "sql",
        ],
        TaskCategory.MATH: [
            "calculate", "compute", "equation", "formula", "solve", "math",
            "number", "sum", "product", "derivative", "integral", "probability",
            "statistics", "algebra", "geometry", "percentage", "ratio",
        ],
        TaskCategory.LOGIC: [
            "prove", "deduce", "infer", "logic", "paradox", "contradiction",
            "valid", "invalid", "premise", "conclusion", "syllogism", "argument",
            "if and only if", "therefore", "implies", "boolean",
        ],
        TaskCategory.CREATIVE: [
            "write", "create", "imagine", "story", "poem", "design", "creative",
            "brainstorm", "innovate", "generate ideas", "narrative", "art",
            "compose", "invent", "novel", "unique", "original",
        ],
        TaskCategory.DATA: [
            "data", "table", "csv", "json", "database", "query", "filter",
            "aggregate", "group by", "join", "dataset", "rows", "columns",
            "analyze data", "spreadsheet", "records", "entries",
        ],
        TaskCategory.RESEARCH: [
            "research", "investigate", "explore", "study", "survey", "review",
            "literature", "sources", "evidence", "findings", "compare",
            "evaluate", "assess", "analyze", "examine", "investigate",
        ],
        TaskCategory.PLANNING: [
            "plan", "schedule", "organize", "strategy", "roadmap", "timeline",
            "steps", "phases", "milestones", "project", "goals", "objectives",
            "prioritize", "allocate", "coordinate", "manage",
        ],
    }
    
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
        """Detect the primary category of the task."""
        scores: dict[TaskCategory, int] = {cat: 0 for cat in TaskCategory}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1
        
        # Find category with highest score
        best_category = max(scores, key=scores.get)  # type: ignore
        
        # If no keywords matched, default to GENERAL
        if scores[best_category] == 0:
            return TaskCategory.GENERAL
        
        return best_category
    
    def _calculate_complexity(self, task: str, context: str) -> float:
        """Calculate complexity score (0-10) based on heuristics."""
        full_text = f"{task} {context}"
        
        # Base complexity from length (normalized)
        word_count = len(full_text.split())
        length_score = min(word_count / 50, 3.0)  # Max 3 points from length
        
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
        
        # Add base complexity of 2 (nothing is truly trivial)
        total += 2.0
        
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
        
        # Score each framework
        for framework_cls in FRAMEWORK_REGISTRY.values():
            score = 0.0
            reasons = []
            
            # 1. Intent Match (Highest Priority)
            intent_match = False
            for intent in intents:
                if intent in framework_cls.capabilities:
                    score += 4.0
                    reasons.append(f"matches intent '{intent}'")
                    intent_match = True
            
            # 2. Category Match
            if category in framework_cls.best_for:
                score += 2.0
                reasons.append(f"matches {category.value} category")
            
            # 3. Complexity Fit & Sizing
            if complexity >= framework_cls.complexity_threshold:
                score += 2.0
                # Penalty for overkill: subtract distance
                # e.g., Task 3.0 vs Threshold 2.0 -> penalty 0.5
                # e.g., Task 3.0 vs Threshold 6.0 (not met) -> N/A
                overkill = (complexity - framework_cls.complexity_threshold) * 0.5
                score -= min(overkill, 1.5) # Cap penalty
                reasons.append(f"complexity fit")
            else:
                # Penalty if task is simpler than framework needs
                score -= 2.0
            
            # 4. Tie-Breaker Bias (Simplicity)
            # Add a tiny fraction of inverse threshold to prefer simpler tools in ties
            score += (10 - framework_cls.complexity_threshold) * 0.01

            candidates.append((framework_cls, score, "; ".join(reasons) if reasons else "default option"))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Best choice
        best = candidates[0]
        
        # Alternatives (other high scorers)
        alternatives = [
            c[0].name for c in candidates[1:4] 
            if c[1] > 0
        ]
        
        reasoning = f"Selected {best[0].name}: {best[2]}"
        
        return best[0].name, reasoning, alternatives
