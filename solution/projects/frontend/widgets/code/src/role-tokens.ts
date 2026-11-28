/**
 * Role-aware inline styling for markdown rendered on a two-role surface
 * (a chat bubble being the only one today).
 *
 * These live in `common/` rather than in the chat package because their
 * consumer is `MarkdownMessage`, which is NOT chat-only — OpenapiViewer,
 * PrettyCode and UrlChip render it too. The chat widget re-exports them from
 * its own `styles/bubbleTokens`, so chat code keeps one import site and the
 * dependency runs one way: chat → code, never back.
 */

/** The two surfaces markdown can be painted on. */
export type MarkdownSurfaceRole = 'user' | 'assistant';

/**
 * Anchor (link) classes for markdown content rendered inside a bubble.
 *
 * The two roles CANNOT share a link color, because the user bubble is an
 * INVERTED surface. `--primary` is tuned for contrast against the page, so on a
 * bubble painted with `--foreground` it is ink-on-ink: in the light theme a
 * deep cyan (`192 90% 35%`) on near-black, which all but disappears.
 *
 * So the user bubble draws its link from `--background` — the token that IS the
 * readable counterpart of the surface it sits on, in every theme by definition —
 * and marks the link with an underline rather than a hue shift. The assistant
 * sits on the plain transcript, so brand-primary works there as usual.
 */
export const ANCHOR = {
  user:
    'text-background underline decoration-background/50 underline-offset-2 ' +
    'hover:decoration-background transition-colors break-all',
  assistant: 'text-primary underline hover:text-primary/80 transition-colors break-all',
} as const;

/** Inline secondary action (e.g. "Show more / less"). Same logic as anchors. */
export const TOGGLE = {
  user: 'text-background/80 hover:text-background',
  assistant: 'text-primary hover:text-primary/80',
} as const;
