import { Highlight, Language, themes } from 'prism-react-renderer';
import React from 'react';
import { useTheme } from '../hooks/useTheme';

interface PrettyCodeProps {
  data: string | object;
  language: Language;
  className?: string;
  mode?: 'dark' | 'light';
  inline?: boolean;
  customBg?: string; // Custom background class
}

const PrettyCode = ({ data, language, className, mode, inline = false, customBg }: PrettyCodeProps) => {
  const detectedTheme = useTheme();
  
  // Use provided mode or fall back to detected theme
  const currentTheme = mode || detectedTheme;
  const isDarkMode = currentTheme === 'dark';
  
  // Select the Prism theme based on the current theme
  const prismTheme = isDarkMode ? themes.vsDark : themes.vsLight;

  // Convert form object to JSON string with proper formatting
  const contentJson = typeof data === 'string' ? data : JSON.stringify(data || {}, null, 2);
  
  // Handle empty content
  if (!contentJson || contentJson.trim() === '') {
    const bgClass = customBg || 'bg-muted dark:bg-zinc-900';
    return (
      <div className={`relative h-full ${bgClass} rounded-sm border border-border dark:border-zinc-700 ${className || ''}`}>
        <div className="h-full overflow-auto p-4">
          <p className="text-muted-foreground text-sm italic">No content available</p>
        </div>
      </div>
    );
  }

  // Get display name for language badge
  const getLanguageDisplayName = (lang: string): string => {
    switch (lang.toLowerCase()) {
      case 'bash':
      case 'shell':
        return 'Bash';
      case 'python':
      case 'py':
        return 'Python';
      case 'javascript':
      case 'js':
        return 'JavaScript';
      case 'typescript':
      case 'ts':
        return 'TypeScript';
      case 'json':
        return 'JSON';
      case 'yaml':
      case 'yml':
        return 'YAML';
      case 'html':
        return 'HTML';
      case 'css':
        return 'CSS';
      case 'sql':
        return 'SQL';
      case 'xml':
        return 'XML';
      case 'markdown':
      case 'md':
        return 'Markdown';
      case 'plaintext':
      case 'text':
        return 'Text';
      case 'mermaid':
        return 'Mermaid';
      default:
        return lang.charAt(0).toUpperCase() + lang.slice(1);
    }
  };

  // Normalize language for Prism - use only basic supported languages
  const normalizedLanguage = (() => {
    const lang = language.toLowerCase();
    
    // Try basic languages that are definitely supported
    switch (lang) {
      case 'javascript':
      case 'js':
        return 'javascript';
      case 'typescript':
      case 'ts':
        return 'typescript'; // Try TypeScript first
      case 'python':
      case 'py':
        return 'python';
      case 'json':
        return 'json';
      case 'css':
        return 'css';
      case 'html':
        return 'markup';
      case 'xml':
        return 'markup';
      case 'bash':
      case 'shell':
        return 'bash';
      case 'sql':
        return 'sql';
      case 'yaml':
      case 'yml':
        return 'yaml';
      case 'markdown':
      case 'md':
        return 'markdown';
      case 'mermaid':
        return 'text'; // Mermaid is handled separately in MarkdownMessage
      default:
        // For unknown languages, try to use the original name first
        // If it doesn't work, Prism will fallback to plain text
        return lang || 'text';
    }
  })();

  const displayLanguage = getLanguageDisplayName(language);

  if (inline) {
    const inlineBgClass = customBg || 'bg-muted dark:bg-[#1e1e1e]';
    return (
      <Highlight theme={prismTheme} code={contentJson} language={normalizedLanguage as Language}>
        {({ className, style, tokens, getTokenProps }) => (
          <code
            className={`${className} ${inlineBgClass} px-2 py-1 rounded text-sm font-mono inline-block`}
            style={{
              ...style,
              fontSize: '0.875rem',
              fontFamily: 'monospace',
            }}
          >
            {tokens.map((line) => (
              line.map((token, key) => (
                <span key={key} {...getTokenProps({ token })} />
              ))
            ))}
          </code>
        )}
      </Highlight>
    );
  }

  const bgClass = customBg || 'bg-muted dark:bg-[#1e1e1e]';
  
  return (
    <div className={`relative h-full ${bgClass} rounded-sm border border-border dark:border-zinc-800 dark:shadow-sm ${className || ''}`}>
      {/* Language badge */}
      <div className="absolute top-2 left-3 z-10">
        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-background/80 text-muted-foreground border border-border/50 backdrop-blur-sm">
          {displayLanguage}
        </span>
      </div>
      
      <div className="h-full overflow-auto">
        <Highlight theme={prismTheme} code={contentJson} language={normalizedLanguage as Language}>
          {({ className, style, tokens, getLineProps, getTokenProps }) => (
            <pre
              className={`${className}`}
              style={{
                ...style,
                margin: 0,
                padding: '2.5rem 1rem 1rem 1rem', // Extra top padding for language badge
                fontSize: '0.875rem',
                lineHeight: 1.5,
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                overflowWrap: 'break-word',
              }}
            >
              {tokens.map((line, i) => (
                <div key={i} {...getLineProps({ line })}>
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </div>
              ))}
            </pre>
          )}
        </Highlight>
      </div>
    </div>
  );
};

export default PrettyCode; 