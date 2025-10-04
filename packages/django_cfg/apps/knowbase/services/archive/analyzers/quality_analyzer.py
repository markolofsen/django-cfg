"""
Code quality analyzer.

Assesses code quality based on documentation and formatting.
"""


class QualityAnalyzer:
    """Assess code quality."""

    @staticmethod
    def assess_code_quality(content: str) -> float:
        """
        Assess code quality score.

        Simple quality assessment based on documentation and formatting.

        Args:
            content: Code content to analyze

        Returns:
            Quality score between 0.0 and 1.0
        """
        # Simple quality assessment
        quality = 0.5  # Base quality

        # Boost for docstrings
        if '"""' in content or "'''" in content:
            quality += 0.2

        # Boost for comments
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        quality += min(0.2, comment_lines / 10.0)

        # Penalty for very long lines
        long_lines = len([line for line in content.split('\n') if len(line) > 100])
        quality -= min(0.2, long_lines / 10.0)

        return max(0.0, min(1.0, quality))
