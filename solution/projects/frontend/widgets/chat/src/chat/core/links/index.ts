// Links, both directions: the ones this package WRITES into a message, and the
// ones it READS back out of one.
//
// Together because they are one round trip. A picked tool is written as a
// markdown link and parsed back on render, and `scheme.ts` owns both halves so
// the shape can never disagree with itself. `prose.ts` handles the other kind —
// ordinary web links the model or the user wrote — which are only ever read.
//
// Pure functions of a string, no React and no DOM: the chip decision and the
// label are testable without rendering anything, which is what keeps them
// honest while the renderer changes.

export {
  configureMentionScheme,
  mentionScheme,
  toolURL,
  parse,
  type ParsedMention,
  type ParseResult,
} from "./scheme";

// Reading half only. A picked tool needs no preprocess step — the composer
// writes the link itself, so the id is never recovered from prose.
export { extractToolId } from "./tool-id";

export {
  isBareUrlLink,
  isExternalHref,
  linkChipLabel,
  normalizeHref,
  splitUrl,
  type SplitUrl,
} from "./prose";

// Links inside plain text: find, sanitise, shorten.
export {
  findLinks,
  linkLabel,
  opensInNewTab,
  safeHref,
  type FoundLink,
  type TextRange,
} from "./linkify";

// A title and icon for a link, resolved by the host.
export {
  linkHost,
  previewable,
  safeIcon,
  usableTitle,
  type LinkPreview,
  type LinksCapability,
  type ResolveLinkPreview,
} from "./preview";
