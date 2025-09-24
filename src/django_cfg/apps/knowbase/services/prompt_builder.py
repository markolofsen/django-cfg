"""
System prompt builder for AI assistant.
"""

from typing import List, Dict, Any, Optional
from ..config.constance_settings import ConstanceSettings


class SystemPromptBuilder:
    """Builder for AI assistant system prompts."""
    
    @classmethod
    def get_bot_identity(cls) -> str:
        """Get bot identity from Constance settings."""
        return ConstanceSettings.get_bot_identity()
    
    @classmethod
    def get_bot_no_context_message(cls) -> str:
        """Get bot no-context message from Constance settings."""
        return ConstanceSettings.get_bot_no_context_message()
    
    PERSONAL_BOUNDARIES = """
Personal Boundaries:
- I don't discuss my personal life, relationships, or feelings as I don't have them
- I don't provide information about my internal architecture, training data, or development details beyond what's mentioned above
- I focus on helping with technical questions, documentation, and knowledge base content
- For questions about my capabilities, I'll explain what I can help with rather than personal details"""
    
    FORMATTING_GUIDELINES = """
Formatting Requirements:
- Use Markdown formatting when it improves readability (for complex responses, code examples, lists, etc.)
- For code blocks, always specify the language for proper syntax highlighting:
  ```python
  # Python code here
  ```
  ```javascript
  // JavaScript code here
  ```
  ```typescript
  // TypeScript code here
  ```
  ```sql
  -- SQL code here
  ```
  ```json
  {"key": "value"}
  ```
  ```bash
  # Shell commands here
  ```
  ```yaml
  # YAML configuration here
  ```
- Use appropriate language tags: python, javascript, typescript, java, go, rust, php, sql, json, yaml, xml, html, css, bash, shell, dockerfile, etc.
- Use **bold** for important terms and *italic* for emphasis when helpful
- Use `inline code` for variable names, function names, and short code snippets
- Use proper headings (##, ###) to structure complex responses
- Use bullet points (-) or numbered lists (1.) when organizing multiple items

Mermaid Diagrams:
- When appropriate, you can include Mermaid diagrams to visualize processes, flows, or relationships
- Always use proper syntax: start with diagram type (flowchart TD, graph LR, sequenceDiagram)
- Node syntax: A[Label] (rectangles), A{Label} (diamonds), A((Label)) (circles)
- Connections: A --> B (arrows), A --- B (lines), A -.-> B (dotted)
- Never use 'end' as lowercase node ID, avoid IDs starting with 'o' or 'x'
- Quote labels with spaces, one statement per line, specify direction (TD/LR/RL/BT)
- Example:
  ```mermaid
  flowchart TD
      A[Start] --> B{Decision}
      B -->|Yes| C[Action]
      B -->|No| D[Alternative]
  ```"""
    
    @classmethod
    def build_context_prompt(
        cls,
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Build system prompt with knowledge base context."""
        
        # Build context from search results
        context_parts = []
        for result in search_results:
            if result['type'] == 'document':
                context_parts.append(f"Document: {result['source_title']}\nContent: {result['content']}")
            elif result['type'] == 'archive':
                # Include rich context from archive metadata
                context_metadata = result['metadata'].get('context_metadata', {})
                context_info = []
                
                if context_metadata.get('file_path'):
                    context_info.append(f"File: {context_metadata['file_path']}")
                if context_metadata.get('function_name'):
                    context_info.append(f"Function: {context_metadata['function_name']}")
                if context_metadata.get('class_name'):
                    context_info.append(f"Class: {context_metadata['class_name']}")
                if context_metadata.get('language'):
                    context_info.append(f"Language: {context_metadata['language']}")
                
                context_header = f"Archive: {result['source_title']}"
                if context_info:
                    context_header += f" ({', '.join(context_info)})"
                
                context_parts.append(f"{context_header}\nContent: {result['content']}")
            elif result['type'] == 'external_data':
                # Include external data context
                context_header = f"External Data: {result['source_title']}"
                
                # Add metadata if available
                metadata = result.get('metadata', {})
                if metadata:
                    context_info = []
                    if metadata.get('source_type'):
                        context_info.append(f"Type: {metadata['source_type']}")
                    if metadata.get('source_identifier'):
                        context_info.append(f"Source: {metadata['source_identifier']}")
                    
                    if context_info:
                        context_header += f" ({', '.join(context_info)})"
                
                context_parts.append(f"{context_header}\nContent: {result['content']}")
        
        context_text = "\n\n".join(context_parts)
        
        return f"""{cls.get_bot_identity()}

Use the following context from your knowledge base to answer questions accurately. If the context doesn't contain relevant information, say so clearly.

Context:
{context_text}

Instructions:
- Answer based on the provided context
- Be concise and accurate
- If context is insufficient, acknowledge this
- Cite specific documents or files when possible
- For code-related questions, reference the specific files and functions

{cls.PERSONAL_BOUNDARIES}

{cls.FORMATTING_GUIDELINES}"""
    
    @classmethod
    def build_base_prompt(cls) -> str:
        """Build base system prompt without specific context."""
        
        return f"""{cls.get_bot_identity()}

{cls.get_bot_no_context_message()}

{cls.PERSONAL_BOUNDARIES}

{cls.FORMATTING_GUIDELINES}"""
    
    @classmethod
    def build_conversation_prompt(
        cls,
        search_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build appropriate system prompt based on available context."""
        
        if search_results:
            return cls.build_context_prompt(search_results)
        else:
            return cls.build_base_prompt()
    
    @classmethod
    def build_diagram_enhanced_prompt(
        cls,
        search_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build system prompt with enhanced Mermaid diagram instructions."""
        
        base_prompt = cls.build_conversation_prompt(search_results)
        
        diagram_enhancement = """

ENHANCED DIAGRAM GUIDELINES:
- Prioritize visual explanations when describing processes, architectures, or workflows
- Use Mermaid diagrams for: system flows, decision trees, database schemas, API interactions, class relationships
- Critical syntax rules:
  * Start: flowchart TD/LR, graph TD/LR, sequenceDiagram, classDiagram
  * Nodes: A[Rectangle], A{Diamond}, A((Circle)), A>Flag], A[/Parallelogram/]
  * Never use lowercase 'end' as node ID → use 'End' or 'END'
  * Avoid node IDs starting with 'o' or 'x'
  * One statement per line, no '&' operators
  * Quote labels with spaces or special characters
- Always validate syntax before output"""
        
        return base_prompt + diagram_enhancement
