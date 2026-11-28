/**
 * Public types for the new JsonTree.
 *
 * The shape is intentionally narrow — five props cover ~95% of cases.
 * Old shape (`mode`, `config`, `jsonTreeProps`, `showActionButtons`, …)
 * is bridged in `legacyAdapter.ts` so existing consumers compile
 * unchanged. New code should target this surface.
 */

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

/** Which toolbar buttons to expose. Default `['search','expand','copy']`. */
export type JsonAction = 'search' | 'expand' | 'copy' | 'download';

/**
 * Font size for the tree body. Toolbar metrics stay constant.
 *   - `'sm'` (default) — `text-xs`, dense for chat/debug
 *   - `'md'`           — `text-sm`, reads like Monaco at normal zoom
 *   - `'lg'`           — `text-base`, presentation / large screen
 */
export type JsonSize = 'sm' | 'md' | 'lg';

export interface JsonTreeProps {
  /** Any JSON-serializable value. */
  data: unknown;

  /** Optional heading label rendered in the toolbar. */
  title?: string;

  /** Label for the root node in the tree. Default `'root'`. */
  rootName?: string;

  /**
   * How the toolbar behaves:
   *   - `'auto'` — fades in on hover / keyboard focus (ChatGPT-style)
   *   - `'always'` — visible from the start (good for debug panels)
   *   - `'never'` — no toolbar at all
   * Default `'auto'`.
   */
  toolbar?: 'auto' | 'always' | 'never';

  /**
   * Which action buttons to render in the toolbar. Default
   * `['search','expand','copy']`. Add `'download'` for in-memory data
   * that should be exportable; omit for on-disk file viewers.
   */
  actions?: readonly JsonAction[];

  /**
   * Auto-expand depth on mount. `true` = expand everything.
   * Default `2` — root + first level open, deeper stays collapsed.
   */
  defaultExpandedDepth?: number | true;

  /**
   * Font size for the tree body. Default `'sm'`. Use `'md'` for
   * full-pane previews (text-viewer.tsx) so it reads at the same
   * weight as Monaco; `'lg'` for talks / demos.
   */
  size?: JsonSize;

  /**
   * Draw the card frame (border + rounded corners). Default `true`.
   * Pass `false` to render flush inside a host pane that already owns
   * the chrome (cmdop preview, OpenAPI response panel).
   */
  bordered?: boolean;

  /**
   * Render the toolbar with reduced padding, smaller icons, and a hidden
   * "X keys" badge. Use for embedded contexts where the JSON body is
   * tiny (e.g. error responses with 2 keys) and the default toolbar
   * dwarfs the content. Default `false`.
   */
  compactHeader?: boolean;

  /** Extra class on the root container. */
  className?: string;

  /**
   * Filename used for the optional Download action. Default `'data.json'`.
   * Ignored when `actions` doesn't include `'download'`.
   */
  downloadFilename?: string;
}
