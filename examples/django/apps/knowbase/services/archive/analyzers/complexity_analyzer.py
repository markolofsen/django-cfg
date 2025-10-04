"""
Code complexity analyzer.

Calculates complexity score for code chunks.
"""


class ComplexityAnalyzer:
    """Analyze code complexity."""

    @staticmethod
    def calculate_code_complexity(content: str) -> float:
        """
        Calculate code complexity score.

        Simple complexity metric based on lines and control structures.

        Args:
            content: Code content to analyze

        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Simple complexity based on lines and control structures
        lines = content.split('\n')
        complexity = len(lines) / 100.0  # Base complexity

        # Add complexity for control structures
        control_keywords = ['if', 'for', 'while', 'try', 'except', 'with']
        for keyword in control_keywords:
            complexity += content.count(keyword) * 0.1

        return min(1.0, complexity)
