"""Text Complexity Analysis Utilities."""

import re
from dataclasses import dataclass


@dataclass
class ComplexityMetrics:
    """Detailed complexity metrics for a text."""
    
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    unique_word_ratio: float  # Vocabulary richness
    question_count: int
    has_code_blocks: bool
    has_lists: bool
    has_constraints: bool
    nested_structure_depth: int
    estimated_complexity: float  # Final 0-10 score


class ComplexityAnalyzer:
    """Analyzes text complexity using various metrics."""
    
    # Indicators of structural complexity
    NESTING_MARKERS = [
        (r'\bif\b.*\bif\b', 2),  # Nested conditionals
        (r'\bfor\b.*\bfor\b', 2),  # Nested loops
        (r'\(.*\(.*\)', 1),  # Nested parentheses
        (r'\[.*\[.*\]', 1),  # Nested brackets
    ]
    
    CONSTRAINT_KEYWORDS = [
        "must", "should", "required", "constraint", "ensure",
        "cannot", "must not", "only", "exactly", "at least",
        "at most", "no more than", "no less than",
    ]
    
    def analyze(self, text: str) -> ComplexityMetrics:
        """
        Perform comprehensive complexity analysis on text.
        
        Args:
            text: The text to analyze
        
        Returns:
            ComplexityMetrics with detailed breakdown
        """
        # Basic counts
        words = text.split()
        word_count = len(words)
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Vocabulary richness
        unique_words = set(w.lower() for w in words)
        unique_word_ratio = len(unique_words) / max(word_count, 1)
        
        # Question complexity
        question_count = text.count('?')
        
        # Structural markers
        has_code_blocks = bool(re.search(r'```|`[^`]+`', text))
        has_lists = bool(re.search(r'^\s*[-*•]\s+|\d+\.\s+', text, re.MULTILINE))
        
        # Constraint detection
        text_lower = text.lower()
        has_constraints = any(kw in text_lower for kw in self.CONSTRAINT_KEYWORDS)
        
        # Nesting depth
        nested_structure_depth = 0
        for pattern, depth in self.NESTING_MARKERS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                nested_structure_depth = max(nested_structure_depth, depth)
        
        # Calculate final complexity score
        estimated_complexity = self._calculate_score(
            word_count=word_count,
            avg_sentence_length=avg_sentence_length,
            unique_word_ratio=unique_word_ratio,
            question_count=question_count,
            has_code_blocks=has_code_blocks,
            has_lists=has_lists,
            has_constraints=has_constraints,
            nested_structure_depth=nested_structure_depth,
        )
        
        return ComplexityMetrics(
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=round(avg_sentence_length, 2),
            unique_word_ratio=round(unique_word_ratio, 3),
            question_count=question_count,
            has_code_blocks=has_code_blocks,
            has_lists=has_lists,
            has_constraints=has_constraints,
            nested_structure_depth=nested_structure_depth,
            estimated_complexity=round(estimated_complexity, 2),
        )
    
    def _calculate_score(
        self,
        word_count: int,
        avg_sentence_length: float,
        unique_word_ratio: float,
        question_count: int,
        has_code_blocks: bool,
        has_lists: bool,
        has_constraints: bool,
        nested_structure_depth: int,
    ) -> float:
        """Calculate the final complexity score (0-10)."""
        score = 2.0  # Base score
        
        # Length contribution (0-2 points)
        score += min(word_count / 100, 2.0)
        
        # Sentence complexity (0-1.5 points)
        score += min(avg_sentence_length / 20, 1.5)
        
        # Vocabulary richness (0-1 point)
        # High ratio = more diverse vocabulary = more complex
        score += unique_word_ratio * 1.0
        
        # Multiple questions (0-1 point)
        score += min(question_count * 0.3, 1.0)
        
        # Structural complexity (0-2 points)
        if has_code_blocks:
            score += 0.5
        if has_lists:
            score += 0.3
        if has_constraints:
            score += 0.7
        score += nested_structure_depth * 0.5
        
        return max(0.0, min(10.0, score))
    
    def quick_score(self, text: str) -> float:
        """
        Get just the complexity score without full analysis.
        
        Args:
            text: The text to analyze
        
        Returns:
            Complexity score (0-10)
        """
        return self.analyze(text).estimated_complexity
