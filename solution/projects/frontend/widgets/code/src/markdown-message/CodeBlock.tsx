import React, { memo } from 'react';
import { CopyButton } from '@djangocfg/ui-core/components';
import { LazyPrettyCode as PrettyCode } from '@djangocfg/widget-kit/pretty-code/lazy';

interface CodeBlockProps {
  code: string;
  language: string;
  isUser: boolean;
  isCompact?: boolean;
  /**
   * Code surface palette. Default `'auto'` — follow the host theme.
   * `'dark'` / `'light'` pin the palette regardless of theme.
   */
  codeTheme?: 'dark' | 'light' | 'auto';
}

/**
 * Markdown code block. Renders the kit's <PrettyCode> directly — its header
 * already carries the language tag and the Copy action.
 *
 * Earlier versions stacked an extra <CopyButton> here too, which
 * surfaced as two copy buttons on every code fence. The fallback
 * branch below still ships its own button because the plain <pre>
 * has no toolbar of its own.
 *
 * Memoised: re-renders only when `code`, `language`, `isUser` or
 * `isCompact` change. `code` is the main trigger — long code blocks
 * should not re-render when parent chat scrolls.
 */
function CodeBlockRaw({ code, language, codeTheme = 'auto' }: CodeBlockProps) {
  // Chat fences are always rendered in PrettyCode's compact mode:
  // 12px font, tighter padding, line-height 1.4. A fenced block in
  // a chat bubble shouldn't outweigh two paragraphs of body text —
  // the standalone PrettyCode story keeps the larger default for
  // docs/diff viewers.
  //
  // `mode` must be UNDEFINED to follow the theme: PrettyCode resolves it as
  // `mode ?? resolvedTheme`, so passing a concrete value — as this did with
  // its old `'dark'` default — pins the palette and defeats that fallback.
  // The pin also propagated to `CodePanelHeader` (`dark={isDarkMode}`), which
  // is why the language label and copy icon stayed `text-white/40` on a light
  // panel. `'auto'` is the default now; a host can still pin deliberately.
  const pinnedMode = codeTheme === 'auto' ? undefined : codeTheme;
  return (
    <div className="my-2">
      <PrettyCode
        data={code}
        language={language}
        className="text-xs"
        mode={pinnedMode}
        // No `customBg` — let PrettyCode paint the surface via its inline
        // `var(--code)` style (see surfaceStyle there). We used to pass
        // `customBg="bg-code"`, but that Tailwind utility only exists in the
        // generated CSS if the CONSUMER scans ui-core/widget source in its
        // Tailwind `content` globs — and most (e.g. cmdop) do not. The class
        // then landed in the DOM with no rule behind it, so the panel rendered
        // with a transparent surface in light mode (in dark mode the ambient
        // dark page hid it). The inline var()-based surface needs no content
        // scan, so it renders correctly in every consumer and both themes.
        isCompact
      />
    </div>
  );
}

export const CodeBlock = memo(CodeBlockRaw);

/** Simple `<pre>` fallback used when CodeBlock throws (lazy module
 *  failure, missing PrettyCode peer, etc).
 *
 *  Memoised: re-renders only when `code`, `language`, `isUser` or
 *  `isCompact` change.
 */
function CodeBlockFallbackRaw({ code, codeTheme = 'auto' }: CodeBlockProps) {
  // Only an explicit `'dark'` pin takes the hard-coded dark surface. `'auto'`
  // uses the token branch, which is already theme-aware (`--code*` is defined
  // in both light.css and dark.css) — so it renders correctly in EITHER theme.
  // Testing `=== 'dark'` and letting everything else fall through to a fixed
  // LIGHT surface would have been the same class of bug this fixes, inverted.
  const isDark = codeTheme === 'dark';
  // On the dark surface the copy button is always light; on a light
  // surface it follows the semantic muted token.
  const copyButtonClass =
    `absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 ` +
    (isDark
      ? 'text-white/70 hover:text-white hover:bg-white/15'
      : 'text-muted-foreground hover:text-foreground hover:bg-muted');

  return (
    <div className="relative group my-3">
      <CopyButton
        value={code}
        variant="ghost"
        className={copyButtonClass}
        title="Copy code"
      />
      {isDark ? (
        // Fixed dark surface to match PrettyCode's default.
        <pre
          className="p-3 rounded text-xs font-mono overflow-x-auto border"
          style={{
            backgroundColor: '#0d1117',
            color: '#e5e7eb',
            borderColor: '#1f2937',
          }}
        >
          <code>{code}</code>
        </pre>
      ) : (
        <pre
          className="p-3 rounded text-xs font-mono overflow-x-auto border"
          // Inline `var(--code*)` rather than `bg-code`/`text-code-foreground`/
          // `border-code-border` classes: those utilities only exist when the
          // consumer scans this widget's source in its Tailwind content globs, which
          // many don't — see the note in CodeBlockRaw. The vars are defined in
          // both light.css and dark.css, so this stays theme-aware everywhere.
          style={{
            backgroundColor: 'var(--code)',
            color: 'var(--code-foreground)',
            borderColor: 'var(--code-border)',
          }}
        >
          <code>{code}</code>
        </pre>
      )}
    </div>
  );
}

export const CodeBlockFallback = memo(CodeBlockFallbackRaw);
