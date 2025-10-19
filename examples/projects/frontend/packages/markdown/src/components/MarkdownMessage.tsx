'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Mermaid, PrettyCode, Button, useCopy, useTheme } from '@djangocfg/ui';
import { Copy } from 'lucide-react';
import type { Components } from 'react-markdown';

// Helper function to extract text content from React children
const extractTextFromChildren = (children: React.ReactNode): string => {
  if (typeof children === 'string') {
    return children;
  }

  if (typeof children === 'number') {
    return String(children);
  }

  if (React.isValidElement(children)) {
    const props = children.props as { children?: React.ReactNode };
    return extractTextFromChildren(props.children);
  }

  if (Array.isArray(children)) {
    return children.map(extractTextFromChildren).join('');
  }

  return '';
};

interface MarkdownMessageProps {
  content: string;
  className?: string;
  isUser?: boolean;
}

// Code block component with copy functionality
interface CodeBlockProps {
  code: string;
  language: string;
  isUser: boolean;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ code, language, isUser }) => {
  const { copyToClipboard } = useCopy();
  const theme = useTheme();

  const handleCopy = () => {
    copyToClipboard(code, "Code copied to clipboard!");
  };

  return (
    <div className="relative group my-3">
      {/* Copy button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={handleCopy}
        className={`
          absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity
          h-8 w-8 p-0
          ${isUser
            ? 'hover:bg-white/20 text-white'
            : 'hover:bg-muted-foreground/20 text-muted-foreground hover:text-foreground'
          }
        `}
        title="Copy code"
      >
        <Copy className="h-4 w-4" />
      </Button>

      {/* Code content */}
      <PrettyCode
        data={code}
        language={language}
        className="text-xs"
        customBg={isUser ? "bg-white/10" : "bg-muted dark:bg-muted"}
        mode={theme}
      />
    </div>
  );
};

// Custom components for markdown in chat
const createMarkdownComponents = (isUser: boolean = false): Components => ({
  // Headings - smaller for chat context
  h1: ({ children }) => (
    <h1 className="text-lg font-bold mb-2 mt-3 first:mt-0">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold mb-2 mt-3 first:mt-0">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-bold mb-1 mt-2 first:mt-0">{children}</h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-sm font-semibold mb-1 mt-2 first:mt-0">{children}</h4>
  ),
  h5: ({ children }) => (
    <h5 className="text-sm font-semibold mb-1 mt-2 first:mt-0">{children}</h5>
  ),
  h6: ({ children }) => (
    <h6 className="text-sm font-medium mb-1 mt-2 first:mt-0">{children}</h6>
  ),

  // Paragraphs - compact spacing for chat
  p: ({ children }) => (
    <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
  ),

  // Lists - compact
  ul: ({ children }) => (
    <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="text-sm">{children}</li>
  ),

  // Links - appropriate for chat context
  a: ({ href, children }) => (
    <a
      href={href}
      className={`underline transition-colors ${
        isUser
          ? 'text-white hover:text-white/80'
          : 'text-primary hover:text-primary/80'
      }`}
      target={href?.startsWith('http') ? '_blank' : undefined}
      rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
    >
      {children}
    </a>
  ),

  // Code blocks - using CodeBlock component with copy functionality
  pre: ({ children }) => {
    // Extract code content and language
    let codeContent = '';
    let language = 'plaintext';

    if (React.isValidElement(children)) {
      const child = children;

      if (child.type === 'code' || (typeof child.type === 'function' && child.type.name === 'code')) {
        const codeProps = child.props as { className?: string; children?: React.ReactNode };
        const rawClassName = codeProps.className;
        language = rawClassName?.replace(/language-/, '').trim() || 'plaintext';
        codeContent = extractTextFromChildren(codeProps.children).trim();
      } else {
        codeContent = extractTextFromChildren(children).trim();
      }
    } else {
      codeContent = extractTextFromChildren(children).trim();
    }

    // If still no content, show placeholder
    if (!codeContent) {
      return (
        <div className="my-3 p-3 bg-muted rounded text-sm text-muted-foreground">
          No content available
        </div>
      );
    }

    // Handle Mermaid diagrams separately
    if (language === 'mermaid') {
      return (
        <div className="my-3">
          <Mermaid chart={codeContent} />
        </div>
      );
    }

    // Try to use CodeBlock component, fallback to simple pre if it fails
    try {
      return <CodeBlock code={codeContent} language={language} isUser={isUser} />;
    } catch (error) {
      // Fallback to simple pre element with copy button
      console.warn('CodeBlock failed, using fallback:', error);
      return (
        <div className="relative group my-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              navigator.clipboard.writeText(codeContent);
            }}
            className={`
              absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity
              h-8 w-8 p-0
              ${isUser
                ? 'hover:bg-white/20 text-white'
                : 'hover:bg-muted-foreground/20 text-muted-foreground hover:text-foreground'
              }
            `}
            title="Copy code"
          >
            <Copy className="h-4 w-4" />
          </Button>
          <pre className={`
            p-3 rounded text-xs font-mono overflow-x-auto
            ${isUser
              ? 'bg-white/10 text-white'
              : 'bg-muted text-foreground'
            }
          `}>
            <code>{codeContent}</code>
          </pre>
        </div>
      );
    }
  },

  // Inline code
  code: ({ children, className }) => {
    // If it's inside a pre tag, let pre handle it
    if (className?.includes('language-')) {
      return <code className={className}>{children}</code>;
    }

    // Extract text content safely
    const codeContent = extractTextFromChildren(children);

    // Inline code styling
    return (
      <code className={`
        px-1.5 py-0.5 rounded text-xs font-mono
        ${isUser
          ? 'bg-white/20 text-white'
          : 'bg-muted text-foreground'
        }
      `}>
        {codeContent}
      </code>
    );
  },

  // Blockquotes
  blockquote: ({ children }) => (
    <blockquote className={`
      border-l-2 pl-3 my-2 italic
      ${isUser
        ? 'border-white/30 text-white/90'
        : 'border-primary text-muted-foreground'
      }
    `}>
      {children}
    </blockquote>
  ),

  // Tables - compact for chat
  table: ({ children }) => (
    <div className="overflow-x-auto my-3">
      <table className="min-w-full text-xs border-collapse">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className={isUser ? 'bg-white/10' : 'bg-muted/50'}>
      {children}
    </thead>
  ),
  tbody: ({ children }) => (
    <tbody>{children}</tbody>
  ),
  tr: ({ children }) => (
    <tr className="border-b border-border/50">{children}</tr>
  ),
  th: ({ children }) => (
    <th className="px-2 py-1 text-left font-medium">{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-2 py-1">{children}</td>
  ),

  // Horizontal rule
  hr: () => (
    <hr className={`
      my-3 border-0 h-px
      ${isUser ? 'bg-white/20' : 'bg-border'}
    `} />
  ),

  // Strong and emphasis
  strong: ({ children }) => (
    <strong className="font-semibold">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic">{children}</em>
  ),
});

export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({
  content,
  className = "",
  isUser = false,
}) => {
  const components = React.useMemo(() => createMarkdownComponents(isUser), [isUser]);

  return (
    <div className={`
      prose prose-sm max-w-none
      ${isUser
        ? 'prose-invert [&>*]:text-white'
        : 'dark:prose-invert'
      }
      ${className}
    `}>
      <ReactMarkdown
        components={components}
        remarkPlugins={[remarkGfm]}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownMessage;
