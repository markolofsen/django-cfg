/**
 * Server-only entry point.
 *
 * Separate from the root export because that one reaches `FacePicker`, which
 * imports `@djangocfg/ui-core` and is a client component. A server page pulling
 * the root barrel would drag the whole design system into a static catalogue
 * route to draw one portrait.
 *
 * Both entries share the seed rules and the corpora, so the two products draw
 * the same face — only the rendering strategy differs.
 */
export { ServerAvatar } from "./render/server-avatar";
export type { ServerAvatarProps } from "./render/server-avatar";
export { roleAvatarSeed } from "./seed/role";
export { skillAvatarSeed, mcpAvatarSeed } from "./seed/capability";
export type { AvatarKind } from "./registry/corpora";
