'use client';

import { Highlight, themes, type Language } from 'prism-react-renderer';
import { memo, useMemo } from 'react';

import { useAppT } from '@djangocfg/i18n';
import { useResolvedTheme } from '@djangocfg/ui-core/hooks';

import { CodePanelHeader } from './code-panel-header';
import { languageLabel, normalizePrismLanguage } from './languages';
import { useEnsurePrismLanguages } from './prism-languages';

// Surface palette — driven by the ui-core `--code*` semantic tokens so the
// code panel matches the rest of the theme system (neutral, preset-aware)
// instead of a hard-coded GitHub blue. The tokens are tuned per theme
// (`light.css` / `dark.css`): a near-white gray in light, a near-black gray in
// dark. Syntax colours still come from Prism's vsDark / github palettes.
const SURFACE = { backgroundColor: 'var(--code)', borderRadius: 'var(--radius-popover)' };
const INLINE_SURFACE = { backgroundColor: 'var(--code-inline)' };

// The panel is BORDERLESS: `--code` already separates it from the page in both
// themes, so a border only added a second boundary around a shape the fill had
// already drawn. `--code-border` stays defined for hosts that need an outline.

export interface PrettyCodeLabels {
  /** a11y label of the copy button. */
  readonly copyCode: string;
  /** Shown instead of an empty listing. */
  readonly noContent: string;
  /** a11y label of the expand button. */
  readonly expand: string;
}

export interface PrettyCodeProps {
  /** The source. An object is `JSON.stringify`d. */
  data: string | object;
  /** A fence language (`ts`, `bash`, …). Aliases are resolved; unknown names render as plain text. */
  language: Language;
  className?: string;
  /**
   * Pin a palette. **Defaults to the resolved host theme** (light -> light
   * surface + GitHub palette, dark -> dark surface + vsDark palette). Pin only
   * to ignore the theme, e.g. printing a PDF on a light page.
   */
  mode?: 'dark' | 'light';
  /** An inline `<code>` chip instead of a block. */
  inline?: boolean;
  /** A class that replaces the `--code` surface. */
  customBg?: string;
  /** 12px type and tighter padding, for a block inside prose (a chat message). */
  isCompact?: boolean;
  /**
   * Line count at which the block scrolls instead of growing. `undefined`
   * (default) grows to fit.
   */
  maxLines?: number;
  /**
   * An expand button appears in the header, but ONLY while the code is
   * height-capped (exceeds `maxLines`).
   */
  onExpand?: () => void;
  /**
   * `card` (default): surface, header with the language and a copy button.
   * `plain`: chrome-less, for embedding inside another scroll container.
   */
  variant?: 'card' | 'plain';
  /**
   * The source is still arriving (a half-written fence). An empty body is then
   * a block that has not started yet, not an empty listing, so no "no content"
   * line flashes before the first token.
   */
  pending?: boolean;
  /** Overrides the words. Default: the `@djangocfg/i18n` dictionary for the active language. */
  labels?: Partial<PrettyCodeLabels>;
}

/** A listing's text. An object that cannot be stringified (a cycle) is shown as its `String()` rather than throwing in render. */
function sourceOf(data: string | object): string {
  if (typeof data === 'string') return data;
  try {
    return JSON.stringify(data ?? {}, null, 2) ?? '';
  } catch {
    return String(data);
  }
}

function PrettyCodeImpl({
  data,
  language,
  className,
  mode,
  inline = false,
  customBg,
  isCompact = false,
  maxLines,
  onExpand,
  variant = 'card',
  pending = false,
  labels: labelOverrides,
}: PrettyCodeProps) {
  const t = useAppT();
  const resolvedTheme = useResolvedTheme();
  const isDark = (mode ?? (resolvedTheme === 'light' ? 'light' : 'dark')) !== 'light';

  // Re-render once `bash` / `ruby` / `java` / `php` finish loading, so a block
  // painted before the grammars arrived is highlighted afterwards.
  useEnsurePrismLanguages();

  const labels = useMemo<PrettyCodeLabels>(
    () => ({
      copyCode: labelOverrides?.copyCode ?? t('tools.code.copyCode'),
      noContent: labelOverrides?.noContent ?? t('tools.code.noContent'),
      expand: labelOverrides?.expand ?? t('ui.actions.expand'),
    }),
    [t, labelOverrides?.copyCode, labelOverrides?.noContent, labelOverrides?.expand],
  );

  const source = sourceOf(data);
  const prismTheme = isDark ? themes.vsDark : themes.github;
  const prismLanguage = normalizePrismLanguage(language);
  const displayLanguage = languageLabel(language);

  const fontSizePx = isCompact ? 12 : 14;
  const lineHeight = isCompact ? 1.4 : 1.5;
  const surfaceStyle = customBg ? undefined : SURFACE;

  // Scroll only past `maxLines`; otherwise the block grows to fit.
  const lineCount = source ? source.split('\n').length : 0;
  const shouldScroll = maxLines !== undefined && lineCount > maxLines;
  // The <pre>'s vertical padding (top + bottom), kept in step with the padding below.
  const maxHeightPx = maxLines === undefined ? undefined : maxLines * fontSizePx * lineHeight + 28;

  if (source.trim() === '') {
    // A block still arriving keeps its header (the surface exists from the
    // first token); a finished empty one says so.
    if (pending && variant === 'card' && !inline) {
      return (
        <div
          data-slot="pretty-code"
          className={`group relative overflow-hidden rounded-[var(--radius-popover)] ${customBg ?? ''} ${className ?? ''}`}
          style={surfaceStyle}
        >
          <CodePanelHeader language={displayLanguage} dark={isDark} />
          <div style={{ height: `${lineHeight * fontSizePx + 28}px` }} aria-hidden />
        </div>
      );
    }
    return (
      <div
        // Same borderless token-rounded surface as the populated panel, so it
        // does not change shape when content arrives.
        className={`relative h-full rounded-[var(--radius-popover)] ${customBg ?? ''} ${className ?? ''}`}
        style={surfaceStyle}
      >
        <div className="h-full overflow-auto p-4">
          <p className="text-sm italic text-muted-foreground" role="status">
            {labels.noContent}
          </p>
        </div>
      </div>
    );
  }

  if (inline) {
    return (
      <Highlight theme={prismTheme} code={source} language={prismLanguage}>
        {({ className: prismClassName, style, tokens, getTokenProps }) => (
          <code
            // `--radius-sm`, not the panel's container radius: a chip inside a
            // line of prose rounds like a small control, not like a card.
            className={`${prismClassName} ${customBg ?? ''} px-2 py-1 rounded-[var(--radius-sm)] ${isCompact ? 'text-xs' : 'text-sm'} font-mono inline-block ${className ?? ''}`}
            style={{
              ...style,
              ...(customBg ? undefined : INLINE_SURFACE),
              fontSize: `${fontSizePx}px`,
              fontFamily: 'monospace',
            }}
          >
            {tokens.map((line, i) => line.map((token, key) => <span key={`${i}-${key}`} {...getTokenProps({ token })} />))}
          </code>
        )}
      </Highlight>
    );
  }

  const listing = (
    <Highlight theme={prismTheme} code={source} language={prismLanguage}>
      {({ className: prismClassName, style, tokens, getLineProps, getTokenProps }) => {
        // The surface owns the ground; drop Prism theme's own background.
        const { backgroundColor: _bg, ...rest } = style;
        const plain = variant === 'plain';
        return (
          <pre
            className={plain ? `${prismClassName} ${className ?? ''}` : prismClassName}
            style={{
              ...rest,
              ...(plain ? { background: 'transparent' } : undefined),
              margin: 0,
              padding: plain ? (isCompact ? '0.75rem 1rem' : '1rem') : '0.875rem 1rem',
              fontSize: `${fontSizePx}px`,
              lineHeight,
              fontFamily: 'monospace',
              // Long unbroken strings (escaped JSON bodies in generated samples)
              // wrap at any character rather than overflowing the container.
              whiteSpace: 'pre-wrap',
              wordBreak: plain ? 'break-all' : 'break-word',
              overflowWrap: plain ? 'anywhere' : 'break-word',
              ...(plain ? { maxWidth: '100%' } : undefined),
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
        );
      }}
    </Highlight>
  );

  // The caller's ScrollArea / panel owns the chrome and the scroll.
  if (variant === 'plain') return listing;

  return (
    <div
      data-slot="pretty-code"
      // Radius lives in the CLASS, not in `surfaceStyle`: a host passing
      // `customBg` drops the inline style, and the panel stays rounded anyway.
      className={`group relative overflow-hidden rounded-[var(--radius-popover)] ${customBg ?? ''} ${className ?? ''}`}
      style={surfaceStyle}
    >
      {/* Persistent header (GitHub / ChatGPT style): language left, copy right, in flow, never floating over the code. */}
      <CodePanelHeader
        language={displayLanguage}
        copyValue={source}
        copyLabel={labels.copyCode}
        expandLabel={labels.expand}
        dark={isDark}
        onExpand={onExpand && shouldScroll ? onExpand : undefined}
      />
      <div
        className={shouldScroll ? 'h-full overflow-auto' : ''}
        style={shouldScroll ? { maxHeight: maxHeightPx } : undefined}
        // An internally scrolling region must be keyboard-reachable.
        {...(shouldScroll ? { tabIndex: 0, role: 'region', 'aria-label': displayLanguage } : {})}
      >
        {listing}
      </div>
    </div>
  );
}

/** Memoised: a block re-renders when its source, language or flags change, not when the surrounding transcript does. */
export const PrettyCode = memo(PrettyCodeImpl);
PrettyCode.displayName = 'PrettyCode';
