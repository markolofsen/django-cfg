"""
Code purpose detector.

Detects the purpose of code elements based on naming and content.
"""


class PurposeDetector:
    """Detect purpose of code elements."""

    @staticmethod
    def detect_code_purpose(element_name: str, content: str) -> str:
        """
        Detect purpose of code element.

        Args:
            element_name: Name of the code element
            content: Element content

        Returns:
            Purpose string (e.g., 'test', 'initialization', 'configuration')
        """
        name_lower = element_name.lower()

        if name_lower.startswith('test_'):
            return 'test'
        elif name_lower.startswith('_'):
            return 'private_method'
        elif 'config' in name_lower:
            return 'configuration'
        elif 'init' in name_lower:
            return 'initialization'
        elif 'main' in name_lower:
            return 'main_function'
        else:
            return 'implementation'
