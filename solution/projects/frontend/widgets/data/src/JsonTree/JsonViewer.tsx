'use client';

/**
 * JsonViewer — collapsible, syntax-coloured JSON tree.
 *
 * Ported from jalco/ui's JsonViewer (MIT, Justin Levine —
 * https://ui.justinlevine.me). Modifications:
 *   - Removed Shiki theme module + the 65-theme palette table; we only
 *     use Tailwind tokens so the viewer follows the host theme via
 *     normal CSS-var cascade. No `colorTheme` prop.
 *   - Replaced jalco's `<button>` toolbar with ui-core <Button tooltip>
 *     primitives so it picks up shared focus/hover styling.
 *   - New `toolbar` prop: `'auto' | 'always' | 'never'`. `'auto'` fades
 *     the toolbar in on hover / keyboard focus inside the container
 *     (ChatGPT-style). `'always'` keeps it visible — debug-panel mode.
 *   - New `actions` prop: list of buttons to mount (`'search' | 'expand'
 *     | 'copy' | 'download'`). Default omits download — file viewers
 *     don't need to "download" something that already lives on disk.
 *   - `bordered={false}` strips the card chrome for host panes that own
 *     it already (avoids the historic double-border bug).
 *
 * The recursive tree code (collapsedPaths Set keyed by string path,
 * buildPath helper, hasSearchMatch recursion, HighlightMatch span) is
 * jalco's original — see `_legacy/` for the pre-refactor JsonContent
 * wrapper around `react-json-tree`.
 */

import {
  Check,
  ChevronRight,
  Copy,
  CopyPlus,
  Download,
  FoldHorizontal,
  Search,
  UnfoldHorizontal,
  X,
} from 'lucide-react';
import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from 'react';
import { Button, Input } from '@djangocfg/ui-core';
import { cn } from '@djangocfg/ui-core/lib';
import type { JsonAction, JsonTreeProps, JsonValue } from './types';

// ─── helpers ────────────────────────────────────────────────────────────

function typeOf(value: JsonValue): string {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  return typeof value;
}

function countEntries(value: JsonValue): number {
  if (Array.isArray(value)) return value.length;
  if (value !== null && typeof value === 'object') return Object.keys(value).length;
  return 0;
}

/** Build a JS access path: `root.users[0].name`. Falls back to bracket
 *  syntax for keys that aren't valid identifiers. */
function buildPath(parent: string, key: string | number): string {
  if (parent === '') return String(key);
  if (typeof key === 'number') return `${parent}[${key}]`;
  if (/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(key)) return `${parent}.${key}`;
  return `${parent}["${key}"]`;
}

function matchesSearch(key: string | number, value: JsonValue, query: string): boolean {
  const q = query.toLowerCase();
  if (String(key).toLowerCase().includes(q)) return true;
  if (value === null) return 'null'.includes(q);
  if (typeof value !== 'object') return String(value).toLowerCase().includes(q);
  return false;
}

function hasSearchMatch(value: JsonValue, key: string | number, query: string): boolean {
  if (!query) return false;
  if (matchesSearch(key, value, query)) return true;
  if (value !== null && typeof value === 'object') {
    const entries = Array.isArray(value)
      ? (value.map((v, i) => [i, v] as const))
      : (Object.entries(value) as readonly (readonly [string, JsonValue])[]);
    return entries.some(([k, v]) => hasSearchMatch(v, k, query));
  }
  return false;
}

/**
 * Token palette per theme.
 *
 * Light is hand-tuned after VSCode Light+ / Xcode (deep blue keys,
 * brick-red strings, forest-green numbers) — pastels read as washed-out
 * on a white background. Dark mirrors the One Dark family.
 */
// Syntax-highlighting hues, not status colours: `violet` names "this is a key",
// not "info", and `emerald` names "this is a string", not "success". A semantic
// token here would assert a meaning the value does not have, and re-theming
// would silently recolour the grammar.
const TOKEN_CLASS: Record<string, string> = {
  /* eslint-disable no-restricted-syntax */
  key: 'text-[#001080] dark:text-violet-400',
  string: 'text-[#a31515] dark:text-emerald-400',
  number: 'text-[#098658] dark:text-sky-400',
  boolean: 'text-[#0550ae] dark:text-amber-400',
  /* eslint-enable no-restricted-syntax */
  null: 'text-muted-foreground/70 dark:text-muted-foreground/60',
  punctuation: 'text-muted-foreground dark:text-muted-foreground',
};

function TokenSpan({
  token,
  children,
  className,
  italic,
}: {
  token: keyof typeof TOKEN_CLASS;
  children: React.ReactNode;
  className?: string;
  italic?: boolean;
}) {
  return (
    <span className={cn(TOKEN_CLASS[token], italic && 'italic', className)}>{children}</span>
  );
}

function HighlightMatch({ text, query }: { text: string; query: string }) {
  if (!query) return <>{text}</>;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return <>{text}</>;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="rounded-sm bg-warning/30 px-0.5 text-inherit">
        {text.slice(idx, idx + query.length)}
      </mark>
      {text.slice(idx + query.length)}
    </>
  );
}

// ─── recursive node ─────────────────────────────────────────────────────

interface JsonNodeProps {
  keyName: string | number;
  value: JsonValue;
  path: string;
  depth: number;
  searchQuery: string;
  collapsedPaths: Set<string>;
  onToggle: (path: string) => void;
  isLast: boolean;
}

function JsonNode({
  keyName,
  value,
  path,
  depth,
  searchQuery,
  collapsedPaths,
  onToggle,
  isLast,
}: JsonNodeProps) {
  const type = typeOf(value);
  const isExpandable = type === 'object' || type === 'array';
  const count = isExpandable ? countEntries(value) : 0;

  const isCollapsed = collapsedPaths.has(path);
  const isExpanded = isExpandable && !isCollapsed;

  const openBracket = type === 'array' ? '[' : '{';
  const closeBracket = type === 'array' ? ']' : '}';
  const comma = isLast ? '' : ',';

  const nodeMatches = searchQuery && matchesSearch(keyName, value, searchQuery);

  const handleToggle = useCallback(() => {
    if (isExpandable) onToggle(path);
  }, [isExpandable, onToggle, path]);

  const [pathCopied, setPathCopied] = useState(false);
  const handleCopyPath = useCallback(() => {
    void navigator.clipboard?.writeText(path).then(() => {
      setPathCopied(true);
      setTimeout(() => setPathCopied(false), 1500);
    });
  }, [path]);

  const rowClass = cn(
    'group flex items-center gap-0 py-px hover:bg-muted/40 rounded-sm',
    nodeMatches && 'bg-warning/15',
  );

  const rowStyle: CSSProperties = { paddingLeft: `${depth * 20 + 8}px` };

  const copyIconClass =
    'ml-1 inline-flex items-center justify-center rounded p-0.5 text-muted-foreground/0 transition-colors group-hover:text-muted-foreground hover:!text-foreground focus-visible:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring';

  function renderKey() {
    return (
      <TokenSpan token="key">
        {typeof keyName === 'string' ? (
          <>
            &quot;
            <HighlightMatch text={keyName} query={searchQuery} />
            &quot;
          </>
        ) : (
          keyName
        )}
      </TokenSpan>
    );
  }

  function renderValue() {
    if (typeof value === 'string') {
      return (
        <TokenSpan token="string">
          &quot;
          <HighlightMatch text={value} query={searchQuery} />
          &quot;
        </TokenSpan>
      );
    }
    if (value === null) {
      return (
        <TokenSpan token="null" italic>
          {searchQuery ? <HighlightMatch text="null" query={searchQuery} /> : 'null'}
        </TokenSpan>
      );
    }
    if (typeof value === 'number') {
      return (
        <TokenSpan token="number">
          <HighlightMatch text={String(value)} query={searchQuery} />
        </TokenSpan>
      );
    }
    if (typeof value === 'boolean') {
      return (
        <TokenSpan token="boolean">
          <HighlightMatch text={String(value)} query={searchQuery} />
        </TokenSpan>
      );
    }
    return <span>{String(value)}</span>;
  }

  if (!isExpandable) {
    return (
      <div className={rowClass} style={rowStyle}>
        <span className="w-4 shrink-0" />
        <span className="font-mono">
          {renderKey()}
          <TokenSpan token="punctuation">: </TokenSpan>
          {renderValue()}
          <TokenSpan token="punctuation">{comma}</TokenSpan>
        </span>
        <button
          type="button"
          onClick={handleCopyPath}
          aria-label={`Copy path: ${path}`}
          className={copyIconClass}
        >
          {pathCopied ? (
            <CopyPlus className="size-3 text-success" />
          ) : (
            <CopyPlus className="size-3" />
          )}
        </button>
      </div>
    );
  }

  const entries = Array.isArray(value)
    ? value.map((v, i) => [i, v] as [number, JsonValue])
    : (Object.entries(value as Record<string, JsonValue>) as [string, JsonValue][]);

  const displayEntries = searchQuery
    ? entries.filter(([k, v]) => hasSearchMatch(v, k, searchQuery))
    : entries;

  return (
    <div>
      <div className={rowClass} style={rowStyle}>
        <button
          type="button"
          onClick={handleToggle}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
          className="flex size-4 shrink-0 items-center justify-center transition-transform text-muted-foreground"
        >
          <ChevronRight
            className={cn('size-3 transition-transform', isExpanded && 'rotate-90')}
          />
        </button>
        <span className="font-mono">
          {renderKey()}
          <TokenSpan token="punctuation">: </TokenSpan>
          <TokenSpan token="punctuation">{openBracket}</TokenSpan>
          {!isExpanded && (
            <>
              <span className="mx-1 text-[10px] text-muted-foreground/60">
                {count} {count === 1 ? 'item' : 'items'}
              </span>
              <TokenSpan token="punctuation">
                {closeBracket}
                {comma}
              </TokenSpan>
            </>
          )}
        </span>
        <button
          type="button"
          onClick={handleCopyPath}
          aria-label={`Copy path: ${path}`}
          className={copyIconClass}
        >
          {pathCopied ? (
            <CopyPlus className="size-3 text-success" />
          ) : (
            <CopyPlus className="size-3" />
          )}
        </button>
      </div>

      {isExpanded && (
        <>
          {displayEntries.map(([k, v], i) => (
            <JsonNode
              key={`${k}-${i}`}
              keyName={k}
              value={v}
              path={buildPath(path, k)}
              depth={depth + 1}
              searchQuery={searchQuery}
              collapsedPaths={collapsedPaths}
              onToggle={onToggle}
              isLast={i === displayEntries.length - 1}
            />
          ))}
          <div
            className="font-mono text-muted-foreground"
            style={{ paddingLeft: `${depth * 20 + 8 + 16}px` }}
          >
            {closeBracket}
            {comma}
          </div>
        </>
      )}
    </div>
  );
}

// ─── path collectors for expand/collapse-all ────────────────────────────

function collectInitialCollapsed(
  value: JsonValue,
  path: string,
  maxDepth: number | true,
  depth: number,
  result: Set<string>,
): void {
  if (value === null || typeof value !== 'object') return;
  if (maxDepth !== true && depth >= maxDepth) result.add(path);
  const entries = Array.isArray(value)
    ? value.map((v, i) => [i, v] as const)
    : Object.entries(value);
  for (const [k, v] of entries) {
    collectInitialCollapsed(v, buildPath(path, k), maxDepth, depth + 1, result);
  }
}

function collectAllExpandable(value: JsonValue, path: string, result: Set<string>): void {
  if (value === null || typeof value !== 'object') return;
  result.add(path);
  const entries = Array.isArray(value)
    ? value.map((v, i) => [i, v] as const)
    : Object.entries(value);
  for (const [k, v] of entries) {
    collectAllExpandable(v, buildPath(path, k), result);
  }
}

// ─── toolbar ────────────────────────────────────────────────────────────

interface ToolbarProps {
  title?: string;
  badge?: string;
  actions: readonly JsonAction[];
  searchOpen: boolean;
  copiedAll: boolean;
  compact?: boolean;
  onToggleSearch: () => void;
  onExpandAll: () => void;
  onCollapseAll: () => void;
  onCopy: () => void;
  onDownload: () => void;
}

function Toolbar({
  title,
  badge,
  actions,
  searchOpen,
  copiedAll,
  compact = false,
  onToggleSearch,
  onExpandAll,
  onCollapseAll,
  onCopy,
  onDownload,
}: ToolbarProps) {
  // Compact density: smaller hit area, smaller icons, no key/items badge.
  // Used by embedded contexts (e.g. RequestViewer body for 2-key error
  // responses) where the default toolbar visually outweighs the JSON.
  const btnSize = compact ? 'size-6' : 'size-7';
  const iconSize = compact ? 'size-3' : 'size-3.5';
  const rowPadding = compact ? 'px-2 py-1' : 'px-3 py-1.5';
  // Each action button carries its label as a `tooltip` (hover devices only).
  const renderBtn = (
    key: string,
    label: string,
    icon: React.ReactNode,
    onClick: () => void,
    active?: boolean,
  ) => (
    <Button
      key={key}
      type="button"
      variant="ghost"
      size="icon"
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      tooltip={label}
      className={cn(btnSize, 'text-muted-foreground hover:text-foreground', active && 'bg-muted text-foreground')}
    >
      {icon}
    </Button>
  );

  const iconCls = iconSize;
  return (
    <div className={cn('flex items-center justify-between gap-2 border-b border-border/40', rowPadding)}>
      <div className="flex min-w-0 items-center gap-2">
        {title ? (
          <h3 className="truncate text-xs font-medium text-foreground">{title}</h3>
        ) : null}
        {badge && !compact ? (
          <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
            {badge}
          </span>
        ) : null}
      </div>
      <div className="flex shrink-0 items-center gap-0.5">
        {actions.includes('search')
          ? renderBtn(
              'search',
              searchOpen ? 'Close search' : 'Search',
              <Search className={iconCls} />,
              onToggleSearch,
              searchOpen,
            )
          : null}
        {actions.includes('expand') ? (
          <>
            {renderBtn(
              'expand',
              'Expand all',
              <UnfoldHorizontal className={iconCls} />,
              onExpandAll,
            )}
            {renderBtn(
              'collapse',
              'Collapse all',
              <FoldHorizontal className={iconCls} />,
              onCollapseAll,
            )}
          </>
        ) : null}
        {actions.includes('copy')
          ? renderBtn(
              'copy',
              copiedAll ? 'Copied!' : 'Copy JSON',
              copiedAll ? (
                <Check className={cn(iconCls, 'text-success')} />
              ) : (
                <Copy className={iconCls} />
              ),
              onCopy,
            )
          : null}
        {actions.includes('download')
          ? renderBtn(
              'download',
              'Download JSON',
              <Download className={iconCls} />,
              onDownload,
            )
          : null}
      </div>
    </div>
  );
}

// ─── component ──────────────────────────────────────────────────────────

const DEFAULT_ACTIONS: readonly JsonAction[] = ['search', 'expand', 'copy'];

/**
 * JsonTree — interactive viewer for arbitrary JSON.
 *
 * Default view: card with a hover-revealed toolbar (search / expand /
 * copy) and the tree expanded two levels deep. Toolbar fades in when
 * the container is hovered or keyboard-focused.
 *
 * For debug surfaces that benefit from the toolbar being always
 * visible, pass `toolbar="always"`. For host panes that own the
 * surrounding chrome (cmdop file preview, OpenAPI response panel),
 * pass `bordered={false}`.
 */
/** Map `size` → Tailwind text-size class for the tree body. */
const SIZE_CLASS: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
};

export const JsonTree = memo(function JsonTree({
  data,
  title,
  rootName = 'root',
  toolbar = 'auto',
  actions = DEFAULT_ACTIONS,
  defaultExpandedDepth = 2,
  bordered = true,
  size = 'sm',
  className,
  downloadFilename = 'data.json',
  compactHeader = false,
}: JsonTreeProps) {
  // Treat the data uniformly as `JsonValue` for the recursion. We only
  // need this cast at the boundary; everything inside is typed.
  const root = data as JsonValue;

  const [collapsedPaths, setCollapsedPaths] = useState<Set<string>>(() => {
    if (defaultExpandedDepth === true) return new Set();
    const collapsed = new Set<string>();
    collectInitialCollapsed(root, rootName, defaultExpandedDepth, 0, collapsed);
    return collapsed;
  });
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedAll, setCopiedAll] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  const togglePath = useCallback((path: string) => {
    setCollapsedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  }, []);

  const expandAll = useCallback(() => setCollapsedPaths(new Set()), []);
  const collapseAll = useCallback(() => {
    const all = new Set<string>();
    collectAllExpandable(root, rootName, all);
    setCollapsedPaths(all);
  }, [root, rootName]);

  const jsonString = useMemo(() => JSON.stringify(data, null, 2), [data]);

  const copyJson = useCallback(() => {
    void navigator.clipboard?.writeText(jsonString).then(() => {
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 1500);
    });
  }, [jsonString]);

  const downloadJson = useCallback(() => {
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = downloadFilename;
    // Appended, and revoked a tick later: the click is queued, so revoking in
    // the next statement can pull the blob out from under a download that has
    // not started reading it yet — a silent zero-byte file.
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }, [jsonString, downloadFilename]);

  const toggleSearch = useCallback(() => {
    setSearchOpen((prev) => {
      const next = !prev;
      if (next) {
        requestAnimationFrame(() => searchRef.current?.focus());
      } else {
        setSearchQuery('');
      }
      return next;
    });
  }, []);

  // Any non-empty query expands the whole tree so matches inside
  // collapsed nodes become visible — restoring the user's previous
  // collapse state would be friendlier; for now match jalco's behaviour.
  useEffect(() => {
    if (searchQuery) setCollapsedPaths(new Set());
  }, [searchQuery]);

  const isExpandable = root !== null && typeof root === 'object';
  const type = typeOf(root);
  const badge = isExpandable
    ? `${countEntries(root)} ${type === 'array' ? 'items' : 'keys'}`
    : undefined;

  const showToolbar = toolbar !== 'never';
  const toolbarHover = toolbar === 'auto';

  return (
    <div
      data-slot="json-tree"
      // `group/jsontree` powers the hover-reveal toolbar in `auto` mode:
      // the toolbar listens to `group-hover/jsontree:` + focus-within
      // and fades in. Keyboard users still see it when focus lands
      // inside the container.
      className={cn(
        'group/jsontree relative w-full',
        SIZE_CLASS[size],
        bordered && 'overflow-hidden rounded-md border border-border/60 bg-card',
        className,
      )}
    >
      {showToolbar ? (
        <div
          className={cn(
            'transition-opacity duration-150',
            toolbarHover &&
              'opacity-0 group-hover/jsontree:opacity-100 group-focus-within/jsontree:opacity-100',
          )}
        >
          <Toolbar
            title={title}
            badge={badge}
            actions={actions}
            searchOpen={searchOpen}
            copiedAll={copiedAll}
            compact={compactHeader}
            onToggleSearch={toggleSearch}
            onExpandAll={expandAll}
            onCollapseAll={collapseAll}
            onCopy={copyJson}
            onDownload={downloadJson}
          />
        </div>
      ) : null}

      {showToolbar && searchOpen ? (
        <div className="flex items-center gap-2 border-b border-border/40 px-3 py-1.5">
          <Search className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
          <Input
            ref={searchRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter keys and values…"
            className="h-7 border-0 bg-transparent px-0 font-mono shadow-none focus-visible:ring-0"
          />
          {searchQuery ? (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              aria-label="Clear search"
              className="inline-flex items-center justify-center rounded p-0.5 text-muted-foreground transition-colors hover:text-foreground"
            >
              <X className="size-3" />
            </button>
          ) : null}
        </div>
      ) : null}

      <div className="overflow-auto py-1">
        {isExpandable ? (
          <JsonNode
            keyName={rootName}
            value={root}
            path={rootName}
            depth={0}
            searchQuery={searchQuery}
            collapsedPaths={collapsedPaths}
            onToggle={togglePath}
            isLast
          />
        ) : (
          <div className="px-4 py-2 font-mono">
            <TokenSpan token="key">{rootName}</TokenSpan>
            <TokenSpan token="punctuation">: </TokenSpan>
            {typeof root === 'string' ? (
              <TokenSpan token="string">&quot;{root}&quot;</TokenSpan>
            ) : typeof root === 'number' ? (
              <TokenSpan token="number">{String(root)}</TokenSpan>
            ) : typeof root === 'boolean' ? (
              <TokenSpan token="boolean">{String(root)}</TokenSpan>
            ) : (
              <TokenSpan token="null" italic>
                null
              </TokenSpan>
            )}
          </div>
        )}
      </div>
    </div>
  );
});
