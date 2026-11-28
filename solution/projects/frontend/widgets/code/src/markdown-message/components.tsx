import React from 'react';
import type { Components } from 'react-markdown';
import { ANCHOR } from '../role-tokens';
import { CodeBlock, CodeBlockFallback } from './CodeBlock';
import { extractTextFromChildren } from './plainText';

/* Mermaid is loaded only when a ```mermaid fence is actually rendered.
 *
 * It was a static import, so the diagram engine entered the bundle of every
 * consumer of this renderer. Measured on the MLS Caribbean property pages
 * 2026-10-17: mermaid and the editor chips accounted for roughly 1.1 MB on a
 * page whose markdown is prose — six sampled listings contained no code fence,
 * no table and no diagram at all.
 *
 * `React.lazy` keeps the call site unchanged; the Suspense fallback is the
 * code block the fence would otherwise have shown, so a diagram that is still
 * loading reads as its own source rather than as empty space.
 */
const Mermaid = React.lazy(() => import('@djangocfg/widget-diagram'));

/** Body / heading size classes per `size` level. */
const SIZE_CLASSES: Record<'xs' | 'sm' | 'base', {
  text: string;
  headingBase: string;
  headingSm: string;
}> = {
  xs: { text: 'text-xs', headingBase: 'text-sm', headingSm: 'text-xs' },
  sm: { text: 'text-sm', headingBase: 'text-base', headingSm: 'text-sm' },
  base: { text: 'text-base', headingBase: 'text-lg', headingSm: 'text-base' },
};

/**
 * Build the chat-tuned markdown component map.
 *
 * Body text size follows `size` (xs/sm/base → 12/14/16px). Heading
 * sizes are scaled a notch above the body so inline-in-chat headings
 * stand out without dominating.
 */
export function createMarkdownComponents(
  isUser: boolean = false,
  size: 'xs' | 'sm' | 'base' = 'sm',
  codeTheme: 'dark' | 'light' | 'auto' = 'auto',
): Components {
  const { text: textSize, headingBase, headingSm } = SIZE_CLASSES[size];
  // Code blocks / diagrams only have a binary compact mode — treat the
  // smallest text level as compact, larger ones as roomy.
  const isCompact = size === 'xs';

  return {
    h1: ({ children }) => (
      <h1 className={`${headingBase} font-semibold mb-2 mt-3 first:mt-0`}>{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className={`${headingSm} font-semibold mb-2 mt-3 first:mt-0`}>{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className={`${headingSm} font-semibold mb-1 mt-2 first:mt-0`}>{children}</h3>
    ),
    h4: ({ children }) => (
      <h4 className={`${headingSm} font-semibold mb-1 mt-2 first:mt-0`}>{children}</h4>
    ),
    h5: ({ children }) => (
      <h5 className={`${headingSm} font-medium mb-1 mt-2 first:mt-0`}>{children}</h5>
    ),
    h6: ({ children }) => (
      <h6 className={`${headingSm} font-medium mb-1 mt-2 first:mt-0`}>{children}</h6>
    ),

    p: ({ children }) => (
      <p className={`${textSize} mb-4 last:mb-0 leading-relaxed break-words`}>{children}</p>
    ),

    ul: ({ children }) => (
      <ul className={`list-disc list-inside mb-2 space-y-1 ${textSize}`}>{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className={`list-decimal list-inside mb-2 space-y-1 ${textSize}`}>{children}</ol>
    ),
    li: ({ children }) => <li className="break-words">{children}</li>,

    // `target` / `rel` for external links are NOT set here — the
    // rehype-external-links plugin tags them on the rehype side, so
    // every `<a>` that sanitize let through gets the same security
    // treatment regardless of which renderer (default vs linkRules
    // override) emitted it. Doing it twice here would just duplicate
    // attributes; doing it only here would miss the linkRules path.
    a: ({ href, children, ...rest }) => (
      <a
        {...rest}
        href={href}
        className={`${textSize} ${isUser ? ANCHOR.user : ANCHOR.assistant}`}
      >
        {children}
      </a>
    ),

    pre: ({ children }) => {
      let codeContent = '';
      let language = 'plaintext';

      if (React.isValidElement(children)) {
        const child = children;
        if (
          child.type === 'code'
          || (typeof child.type === 'function' && child.type.name === 'code')
        ) {
          const codeProps = child.props as {
            className?: string;
            children?: React.ReactNode;
          };
          const rawClassName = codeProps.className;
          language = rawClassName?.replace(/language-/, '').trim() || 'plaintext';
          codeContent = extractTextFromChildren(codeProps.children).trim();
        } else {
          codeContent = extractTextFromChildren(children).trim();
        }
      } else {
        codeContent = extractTextFromChildren(children).trim();
      }

      if (!codeContent) {
        return (
          <div className="my-3 p-3 bg-muted rounded text-sm text-muted-foreground">
            No content available
          </div>
        );
      }

      if (language === 'mermaid') {
        // Inline render fits the bubble width; the Mermaid component
        // owns its own click-to-fullscreen modal which sizes against
        // the viewport, so we don't cap it here. A previous version
        // hardcoded `max-w-[600px]` and that constraint leaked into
        // the fullscreen modal too — diagram rendered at 600px in the
        // middle of an empty viewport.
        return (
          <div className="my-3 w-full">
            <React.Suspense
              fallback={
                <CodeBlockFallback
                  code={codeContent}
                  language="mermaid"
                  isUser={isUser}
                  isCompact={isCompact}
                  codeTheme={codeTheme}
                />
              }
            >
              <Mermaid chart={codeContent} isCompact={isCompact} />
            </React.Suspense>
          </div>
        );
      }

      try {
        return <CodeBlock code={codeContent} language={language} isUser={isUser} isCompact={isCompact} codeTheme={codeTheme} />;
      } catch (error) {
        console.warn('CodeBlock failed, using fallback:', error);
        return <CodeBlockFallback code={codeContent} language={language} isUser={isUser} isCompact={isCompact} codeTheme={codeTheme} />;
      }
    },

    code: ({ children, className }) => {
      // Inside <pre>: let pre handle styling.
      if (className?.includes('language-')) {
        return <code className={className}>{children}</code>;
      }
      // Inline `<code>` uses the design system's `--code-inline`
      // token. One semantic chip surface across both themes; on a
      // user bubble we still palette-switch with `text-primary-
      // foreground` because the inline chip blends INTO the bubble
      // — there's no panel boundary like a fence has. We trade a
      // perfect "code surface" tone here for legible body inheritance,
      // matching ChatGPT's behaviour in coloured user bubbles.
      const inlineCodeClass = isUser
        ? 'bg-primary-foreground/15 text-primary-foreground'
        : 'bg-code-inline text-code-inline-foreground';
      return (
        <code className={`px-1 py-0.5 rounded font-mono text-[0.875em] ${inlineCodeClass} break-all`}>
          {extractTextFromChildren(children)}
        </code>
      );
    },

    // Modern chat convention drops italic on blockquotes — italic +
    // tight bubble = hard to read. Border-left at 2px (4px reads
    // heavy in a 320–480px bubble). On the saturated user bubble we
    // use a primary-foreground tint; on the assistant bubble we use
    // the muted-foreground role for de-emphasis.
    blockquote: ({ children }) => {
      const cls = isUser
        ? 'border-primary-foreground/40 text-primary-foreground/80'
        : 'border-border text-muted-foreground';
      return (
        <blockquote className={`${textSize} border-l-2 pl-3 my-3 break-words ${cls}`}>
          {children}
        </blockquote>
      );
    },

    // Tables: outer wrapper handles overflow, inner `<table>`
    // inherits the chat-density text size. Borders / header use
    // semantic tokens — `border-code-border` for the assistant
    // (matches the code-fence panel for visual cohesion when both
    // appear in the same reply); primary-foreground/N for the user
    // bubble so lines read against the saturated `bg-primary`.
    table: ({ children }) => (
      <div className="overflow-x-auto my-3">
        <table className={`min-w-full ${textSize} border-collapse`}>{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className={isUser ? 'bg-primary-foreground/10' : 'bg-muted/40'}>
        {children}
      </thead>
    ),
    tbody: ({ children }) => <tbody>{children}</tbody>,
    tr: ({ children }) => (
      <tr className={isUser ? 'border-b border-primary-foreground/15' : 'border-b border-border'}>
        {children}
      </tr>
    ),
    th: ({ children }) => {
      const borderCls = isUser ? 'border-primary-foreground/25' : 'border-border';
      return (
        <th className={`px-2 py-1.5 text-left font-semibold border-b ${borderCls} break-words`}>
          {children}
        </th>
      );
    },
    td: ({ children }) => <td className="px-2 py-1.5 break-words">{children}</td>,

    // Soft separator. ChatGPT / Slack / Linear strip the visible
    // line, Claude.ai keeps a hairline. We follow Claude — present
    // but quiet. Palette switches by role so the hairline reads on
    // both surfaces.
    hr: () => (
      <hr
        className={`my-4 border-0 h-px ${
          isUser ? 'bg-primary-foreground/20' : 'bg-border'
        }`}
      />
    ),

    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
  };
}
