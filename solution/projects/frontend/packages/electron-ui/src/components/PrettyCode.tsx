import { Highlight, type Language, themes } from 'prism-react-renderer';
import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { useCopy } from '@djangocfg/ui-core/hooks';

interface PrettyCodeProps {
  data: string | object;
  language: Language;
  className?: string;
  theme?: 'dark' | 'light';
  inline?: boolean;
  customBg?: string;
}

const PrettyCode = ({ data, language, className, theme = 'dark', inline = false, customBg }: PrettyCodeProps) => {
  const [copied, setCopied] = useState(false);
  const { copyToClipboard } = useCopy({
    successMessage: "Code copied to clipboard",
    errorMessage: "Failed to copy code"
  });

  const isDarkMode = theme === 'dark';
  const prismTheme = isDarkMode ? themes.vsDark : themes.vsLight;

  // Convert object to JSON string with proper formatting
  const contentJson = typeof data === 'string' ? data : JSON.stringify(data || {}, null, 2);

  // Handle copy
  const handleCopy = async () => {
    const success = await copyToClipboard(contentJson);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

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
      default:
        return lang.charAt(0).toUpperCase() + lang.slice(1);
    }
  };

  // Normalize language for Prism
  const normalizedLanguage = (() => {
    const lang = language.toLowerCase();

    switch (lang) {
      case 'javascript':
      case 'js':
        return 'javascript';
      case 'typescript':
      case 'ts':
        return 'typescript';
      case 'python':
      case 'py':
        return 'python';
      case 'json':
        return 'json';
      case 'css':
        return 'css';
      case 'html':
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
      default:
        return lang || 'text';
    }
  })();

  const displayLanguage = getLanguageDisplayName(language);

  if (inline) {
    const inlineBgClass = customBg || 'bg-muted dark:bg-[#1e1e1e]';
    return (
      <Highlight theme={prismTheme} code={contentJson} language={normalizedLanguage as Language}>
        {({ className: highlightClassName, style, tokens, getTokenProps }) => (
          <code
            className={`${highlightClassName} ${inlineBgClass} px-2 py-1 rounded text-sm font-mono inline-block`}
            style={{
              ...style,
              fontSize: '0.875rem',
              fontFamily: 'monospace',
            }}
          >
            {tokens.map((line, lineIdx) => (
              <React.Fragment key={lineIdx}>
                {line.map((token, tokenIdx) => (
                  <span key={tokenIdx} {...getTokenProps({ token })} />
                ))}
              </React.Fragment>
            ))}
          </code>
        )}
      </Highlight>
    );
  }

  const bgClass = customBg || 'bg-muted dark:bg-[#1e1e1e]';

  return (
    <div className={`relative h-full ${bgClass} rounded-sm border border-border dark:border-zinc-800 dark:shadow-sm ${className || ''}`}>
      {/* Header with language badge and copy button */}
      <div className="absolute top-2 left-3 right-3 z-10 flex items-center justify-between">
        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-background/80 text-muted-foreground border border-border/50 backdrop-blur-sm">
          {displayLanguage}
        </span>
        <button
          onClick={handleCopy}
          className="inline-flex items-center justify-center p-1.5 rounded text-muted-foreground hover:text-foreground bg-background/80 border border-border/50 backdrop-blur-sm transition-colors"
          title="Copy code"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>

      <div className="h-full overflow-auto">
        <Highlight theme={prismTheme} code={contentJson} language={normalizedLanguage as Language}>
          {({ className: highlightClassName, style, tokens, getLineProps, getTokenProps }) => (
            <pre
              className={highlightClassName}
              style={{
                ...style,
                margin: 0,
                padding: '2.5rem 1rem 1rem 1rem',
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

export { PrettyCode };
export type { PrettyCodeProps, Language };
