'use client';

/**
 * Chat bridge — how the AI drives the user's live page.
 *
 * Two layers:
 *
 * - `bridge/` proper — the command registry, the built-in commands, and
 *   the directive transport (SSE → singleton bus). This is the AI's
 *   control surface over the browser.
 * - `overlay/` — how a `point` directive is drawn: ref resolution,
 *   geometry tracking, and the SVG-mask spotlight.
 *
 * Read-only by default. Commands that would change the user's data
 * (`fill`, `click`) are deliberately stubbed.
 */

// Overlay — how a highlight is drawn.
export {
  HighlightOverlay,
  type HighlightOverlayProps,
  SpotlightCanvas,
  type SpotlightCanvasProps,
  useHighlightTargets,
  resolveRefs,
  type RefResolver,
  type PointDirective,
  type HighlightTarget,
  type SpotlightRect,
  type CSTRefId,
} from './overlay';

// Directive transport — SSE `directive` event → singleton bus.
export {
  useChatDirectives,
  pushDirectives,
  clearDirectives,
  parseDirectives,
} from './directive-bus';

// Command registry + the ref resolver the commands read.
export {
  registerBridgeCommand,
  getBridgeCommand,
  type BridgeCommand,
} from './registry';
export {
  setBridgeResolver,
  setBridgeSender,
  type BridgeSender,
} from './set-bridge-resolver';

// `window.__chatBridge` install (dev-gated). Importing this transitively
// pulls in `./commands`, whose modules register the built-in commands
// into the registry as a side effect.
export { installChatBridge, type ChatBridge } from './window';

/**
 * Running an approved action. The gate that approves it lives in
 * `copilot`; the doing lives here, with the DOM.
 */
export {
  performAction,
  VISIBLE_TIMEOUT_MS,
  type ActionOutcome,
  type ProposedAction,
} from './perform';
