// The input subsystem — its own layer, not a leaf inside primitives/.
//
// Measured: the archived chat's composer is 3 200 lines across 21 files and the
// editor it wraps another 3 191. Seven thousand lines is a subsystem.
//
// EDITOR POLICY: textarea first, a richer editor only on a named trigger.
// Formatting while typing is out of scope; the one structural weakness is that
// a textarea cannot host a POPUP well, and a mention menu is a popup — so the
// switch criteria are things a textarea cannot do, never a taste argument.
//
// What keeps that swap cheap: mention DETECTION is a pure function of
// (text, caret) and lives in core/, so it survives the swap untouched. Only the
// rendering surface is replaced.
//
// LAYOUT, grouped by job rather than by artifact kind:
//   field/     the textarea and everything positioned against its caret
//   controls/  the row's buttons, which agree on shape through `button.tsx`
//   tray/      what sits around the draft rather than in it
//   stories/   the workbench; no product code may import it
// At the root: the shell, the context all three groups read, and this barrel.
// A context inside a group would make the other three reach sideways into it.
//
// May import: primitives, store, core, utils, content.
// May NOT import: ui, widgets.

export { Composer } from "./composer";
export type { ComposerProps } from "./composer";
export { ComposerButton } from "./controls/button";
export type { ComposerButtonProps, ComposerButtonTone } from "./controls/button";
export { ComposerInput } from "./field/input";
export type { ComposerInputProps } from "./field/input";
export { ComposerField } from "./field/field";
export { MentionMenu, mentionTextareaAria, optionId } from "./field/mention-menu";
export type { MentionMenuProps, MenuRow } from "./field/mention-menu";
export { useMentionMenu } from "./field/use-mention-menu";
export type { MentionMenuState } from "./field/use-mention-menu";
export type { ComposerFieldProps } from "./field/field";
export { ComposerPickedTools, PickedToolChip } from "./tray/picked-tools";
export type { ComposerPickedToolsProps, PickedToolChipProps } from "./tray/picked-tools";
export { ComposerModel } from "./controls/model";
export { ComposerAttach } from "./controls/attach";
export type { ComposerAttachProps } from "./controls/attach";
export { ComposerAttachments, ComposerAttachmentsView } from "./tray/attachments";
export type { ComposerAttachmentsProps, ComposerAttachmentsViewProps } from "./tray/attachments";
export type { StagedAttachment, StagedStatus } from "../store/composing/use-attachments";
export { ComposerSend } from "./controls/send";
export type { ComposerSendProps } from "./controls/send";
export { ComposerQueue } from "./tray/queue";
export type { ComposerQueueProps } from "./tray/queue";

// The notice block ABOVE the composer box — composed parts, so a host adds a
// line or a link in its own JSX rather than asking for a prop.
export {
  ComposerBanner,
  ComposerBannerAction,
  ComposerBannerActions,
  ComposerBannerBody,
  ComposerBannerDescription,
  ComposerBannerDismiss,
  ComposerBannerIcon,
  ComposerBannerTitle,
} from "./tray/banner";
export type {
  ComposerBannerActionProps,
  ComposerBannerDismissProps,
  ComposerBannerIconProps,
  ComposerBannerProps,
  ComposerBannerTone,
} from "./tray/banner";
// A session-control verb in flight. Beside the banner because it renders as
// one, and above the composer for the same reason.
export { CommandProgress } from "./tray/command-progress";
export type { CommandProgressProps } from "./tray/command-progress";
export { ComposerVoice } from "./controls/voice";
export type { ComposerVoiceProps } from "./controls/voice";
export { ComposerThink } from "./controls/think";
export type { ComposerThinkProps } from "./controls/think";
// The `+` arsenal. Its sheet is a DIRECTORY beside `controls/` — a filter, a
// grouped list and their matching rule do not fit one 300-line file, and
// splitting after the fact is how a file ends up owning three jobs.
export { ComposerTools } from "./controls/tools";
export type { ComposerToolsProps } from "./controls/tools";
export { ToolMenu } from "./tools/menu";
export type { ToolMenuProps } from "./tools/menu";
export { ToolRows } from "./tools/rows";
export type { ToolRowsProps } from "./tools/rows";
export { LanguageMenu, languageLabel } from "./controls/language-menu";
export type { LanguageMenuProps } from "./controls/language-menu";
export { useComposer } from "./context";
export { useDraftPersistence } from "./use-draft-persistence";
export { useReplaceText } from "./tray/use-replace-text";
export type { AskReplace } from "./tray/use-replace-text";
