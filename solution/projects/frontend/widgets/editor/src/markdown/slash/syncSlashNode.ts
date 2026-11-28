/**
 * `syncSlashNode` — bridge between the slash hook's string buffer and
 * the TipTap document's node form.
 *
 * The slash hook lives entirely on the editor value string — it has no
 * concept of nodes. When the host wires a TipTap-backed
 * `<ComposerRichTextarea>` with `slashCommands`, the document needs to
 * pick up two things on its own:
 *
 *   1. After `setContent(newValue)` runs (e.g. the user picked `/verb`
 *      from the menu so `composer.value` became `"/verb "`), the
 *      leading `/verb` text must turn into a `SlashCommandNode` atom
 *      so the chip shows up.
 *   2. If the user backspaces past the chip or types non-slash text,
 *      the buffer is no longer a slash command — there's nothing to
 *      do because the atom would have been removed wholesale by the
 *      backspace.
 *
 * This module owns the post-`setContent` "absorb the leading slash"
 * pass. It is the only piece of TipTap-aware code the slash node needs
 * beyond the node definition itself.
 */
import type { Editor } from '@tiptap/react';

import type {
  SlashCommandInfo,
} from './types';

/**
 * Find the leading `/verb` in the document — if and only if it appears
 * as the very first inline text of the first paragraph. Returns
 * `{ verb, from, to }` (`from` / `to` are absolute document positions
 * usable with `insertContentAt`) or `null` when no leading slash is
 * present.
 */
function findLeadingSlashText(
  editor: Editor,
  commands: readonly SlashCommandInfo[],
): { verb: SlashCommandInfo; from: number; to: number } | null {
  const doc = editor.state.doc;
  if (doc.childCount === 0) return null;
  // Walk the document's first inline block. The buffer must START with
  // the slash — verbs in the middle of the message are not slash
  // commands (matches `parseSlashState` semantics).
  const firstBlock = doc.firstChild;
  if (!firstBlock || firstBlock.childCount === 0) return null;
  const firstInline = firstBlock.firstChild;
  if (!firstInline) return null;
  // If the first inline is already a slash atom we're done.
  if (firstInline.type.name === 'slashCommand') return null;
  if (!firstInline.isText) return null;
  const text = firstInline.text ?? '';
  // Mirrors SLASH_RE from ../../../chat/composer/slash/state.ts. Kept
  // inline to avoid pulling the chat package into the editor module.
  const m = /^\/([a-zA-Z][\w-]*)(?:[ \n]|$)/.exec(text);
  if (!m) return null;
  const verb = m[1]?.toLowerCase() ?? '';
  const cmd = commands.find((c) => c.id === verb);
  if (!cmd) return null;
  const slashLen = 1 + (m[1]?.length ?? 0); // `/verb` length, no trailing
  // First text child of the first block starts at position 1 in the
  // document (the block boundary takes position 0).
  const from = 1;
  const to = from + slashLen;
  return { verb: cmd, from, to };
}

/**
 * If the document starts with a `/verb` text node whose verb is in
 * `commands`, replace that text with a `SlashCommandNode` atom. No-op
 * otherwise. Idempotent — calling it on a document that already starts
 * with the atom does nothing.
 *
 * Returns `true` when a replacement happened (so callers can suppress
 * a feedback `onUpdate` if needed).
 */
export function syncLeadingSlashNode(
  editor: Editor,
  commands: readonly SlashCommandInfo[],
): boolean {
  if (!editor || editor.isDestroyed) return false;
  if (commands.length === 0) return false;
  const found = findLeadingSlashText(editor, commands);
  if (!found) return false;
  const { verb, from, to } = found;
  editor
    .chain()
    .insertContentAt(
      { from, to },
      {
        type: 'slashCommand',
        attrs: { id: verb.id, token: verb.token },
      },
    )
    .run();
  return true;
}
