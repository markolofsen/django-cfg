/**
 * Shared types for the universal Nextra-4 docs SEO toolkit (scripts/seo).
 * Brand-agnostic — project specifics come from the project's seo.config.
 */

export interface NextraSeoConfig {
  /**
   * Project display name — CLI banner, outbound user-agent, **and the `# `
   * heading of the generated `public/llms.txt`**. That last one makes it a
   * PUBLIC string: a slug-style value ships to readers verbatim. Set a name a
   * human would accept on a published page, not an internal id.
   */
  name: string;
  /**
   * One-line product summary for the `> blockquote` at the top of llms.txt.
   * Brand-agnostic: each project sets its own in seo.config. Optional.
   */
  description?: string;
  /**
   * Whether `sitemap` should (re)generate `public/llms.txt` from the route tree.
   * Defaults to `true` (the route-dump index). Set `false` when a project hand-
   * maintains a curated `llms.txt` (and/or `llms-full.txt`) that the generator
   * must not clobber. Optional.
   */
  llms?: boolean;
  /** Content directory (Nextra 4 `content/`), relative to cwd. */
  contentDir: string;
  /** Base URL for the sitemap, no trailing slash. */
  baseUrl: string;
  /** Output directory for sitemap.xml / robots.txt, relative to cwd. */
  outputDir: string;
  /** Public assets directory (Next.js `public/`), relative to cwd. */
  publicDir: string;
  /** Glob patterns (relative to contentDir) to exclude from routes & link scan. */
  ignore: string[];
  /**
   * Next.js `basePath` (e.g. '/docs'), or '' when the app is served at root.
   * When set, raw `<a href>` internal links (in `.tsx`/`.jsx` components and
   * literal JSX `<a>` in `.mdx`) MUST start with this prefix — Next does NOT
   * auto-prefix raw anchors. Internal raw `<a>` hrefs missing the prefix are
   * flagged `missing-basepath`. When '', the rule is skipped. Brand-agnostic.
   */
  basePath: string;
  /**
   * Globs (relative to cwd) for component/app code to scan for raw `<a href>`
   * internal links. Only used when `basePath` is set. Defaults to app sources.
   */
  appGlobs: string[];
}

export interface RouteInfo {
  /** Route path, root-based, no trailing slash (e.g. "/intro/how-it-works", "/" for home). */
  path: string;
  /** Absolute source file that produced the route. */
  file: string;
  /** SEO priority (0.0 - 1.0). */
  priority: number;
  /** Change frequency hint. */
  changefreq: string;
  /** Last modified ISO date (from file mtime). */
  lastmod: string;
}

/** Why a link is considered broken. */
export type BrokenReason =
  | 'old-prefix' // /docs/... — legacy prefix that should be stripped
  | 'absolute-wrong' // /slug exists elsewhere in the tree (unique relocation candidate)
  | 'missing-page' // does not resolve and no candidate found
  | 'bad-anchor' // page resolves but #anchor (heading slug) not found
  | 'missing-asset' // image/asset path does not exist under public/
  | 'jsx-relative-href' // relative href in a JSX/HTML attr — Nextra does NOT rewrite these, so the
                        // browser resolves them against the current URL (no trailing slash) → 404
  | 'missing-basepath'; // raw <a> internal absolute href missing the configured basePath (e.g. /docs).
                        // Next does NOT auto-prefix raw <a>, so it 404s in the browser.

/** What kind of reference this is — affects how it's validated. */
export type LinkKind = 'link' | 'image';

export interface LinkRef {
  /** Absolute path of the file containing the link. */
  file: string;
  /** 1-based line number. */
  line: number;
  /** 1-based column. */
  column: number;
  /** Raw href as authored (e.g. "/how-it-works", "./quickstart", "/docs/cli#run"). */
  raw: string;
  /** Path portion without anchor/query. */
  pathname: string;
  /** Anchor portion including leading '#', or '' if none. */
  anchor: string;
  /** 'link' (page/anchor) or 'image' (asset under public/). */
  kind: LinkKind;
  /**
   * True when this href came from a JSX/HTML attribute (`<Card href>`, `<a href>`, `<img src>`),
   * NOT a markdown `[..](..)` / `![..](..)`. Matters because Nextra rewrites RELATIVE markdown
   * links to absolute at build time, but leaves JSX/HTML attributes untouched — so a relative
   * JSX href ships verbatim and the browser mis-resolves it. Markdown relatives are safe.
   */
  inJsx: boolean;
  /**
   * JSX/HTML element name the href came from, lowercased (e.g. 'a', 'img',
   * 'card'). Undefined for markdown links. Used to distinguish a genuine raw
   * `<a>`/`<img>` (ships verbatim — basePath rule applies) from a component
   * like `<Card>` that maps to a prefix-adding component (basePath added at
   * runtime, so its source href is correctly authored WITHOUT the prefix).
   */
  jsxTag?: string;
}

export interface BrokenLink extends LinkRef {
  reason: BrokenReason;
  /** Suggested replacement raw href, if a safe fix exists. */
  suggestion?: string;
  /** Whether `fix --write` would apply the suggestion automatically. */
  autoFixable: boolean;
}

export interface CheckResult {
  scanned: number; // files scanned
  links: number; // internal links examined
  broken: BrokenLink[];
}

/** One external (http/https) URL reference and where it was authored. */
export interface ExternalRef {
  url: string;
  file: string;
  line: number;
}

/** Result of probing one external URL. */
export interface ExternalCheck extends ExternalRef {
  /** HTTP status, or 0 for a network/DNS/timeout error. */
  status: number;
  /** True when the URL is considered dead (4xx/5xx/network error). */
  dead: boolean;
  /** Short note (e.g. "timeout", "ENOTFOUND", "301 -> …"). */
  note?: string;
}

export interface ExternalResult {
  total: number; // distinct URLs probed
  refs: number; // total references (with dupes)
  dead: ExternalCheck[];
}
