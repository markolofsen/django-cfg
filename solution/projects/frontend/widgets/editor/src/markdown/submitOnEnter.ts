// SubmitOnEnter — Tiptap extension that hooks ProseMirror's keymap
// before StarterKit's HardBreak so Enter and Cmd/Ctrl+Enter both submit
// while Shift+Enter inserts a newline (ChatGPT / Telegram behaviour).
//
// Why an extension and not a wrapper `onKeyDown` handler:
//
//   Tiptap registers its keymaps inside the ProseMirror keymap
//   plugin, which runs in the ProseMirror dispatch pipeline. A React
//   `onKeyDown` / `onKeyDownCapture` on a wrapper div fires AFTER
//   ProseMirror has already committed the HardBreak transaction in
//   the same event tick — so calling `preventDefault()` there is too
//   late: the user sees a hard-break flash in, the React handler
//   then runs its preventDefault, and the next Enter submits.
//
//   Registering the keybinding via `addKeyboardShortcuts` puts us in
//   the same keymap pipeline at a higher priority than StarterKit's
//   default Enter binding, so we intercept before HardBreak runs.
//
// The handler also respects IME composition and the mention popover
// (Tiptap's suggestion plugin captures Enter when its popover is
// open — we mirror that by checking `.markdown-mention-list` in the
// DOM; same predicate the wrapper used).

import { Extension } from '@tiptap/core';

export interface SubmitOnEnterOptions {
  /** Fired when Enter is pressed without Shift, no IME composition,
   *  and no mention popover open. Return `true` to consume the key
   *  (default behaviour), `false` to let ProseMirror handle it (i.e.
   *  fall back to HardBreak). */
  onSubmit: () => boolean | void;
}

export const SubmitOnEnter = Extension.create<SubmitOnEnterOptions>({
  name: 'submitOnEnter',

  addOptions() {
    return {
      // Default no-op — explicit consumer must override. We never
      // intercept Enter unless an onSubmit is wired, so leaving the
      // extension installed with no handler is safe.
      onSubmit: () => false,
    };
  },

  addKeyboardShortcuts() {
    // Shared by `Enter` and `Mod-Enter` so the two can never drift into
    // different submit rules.
    const submit = () => {
      // Mention suggestion popover owns Enter while open.
      // The suggestion plugin renders the list with this class
      // (see createMentionSuggestion.ts).
      if (typeof document !== 'undefined' && document.querySelector('.markdown-mention-list')) {
        return false;
      }
      const result = this.options.onSubmit();
      // Default: consume the key (true). Only let it fall through
      // to HardBreak if onSubmit explicitly returned false.
      return result !== false;
    };

    return {
      Enter: submit,
      // Cmd/Ctrl+Enter submits too. ProseMirror matches a chord EXACTLY, so the
      // `Enter` binding above does NOT fire while a modifier is held — without
      // this line Cmd+Enter fell through to the default and did nothing, in a
      // rich composer only. The plain `<textarea>` path has always sent on it
      // (`useChatComposer`: `!e.shiftKey` is true with Meta down), so the two
      // hosts disagreed about the same keystroke depending on which one the
      // surface happened to mount.
      //
      // Both keys are ONE intent — "send this" — so they share `submit` and go
      // through the composer's single `submit()`, which is what routes to a
      // queued follow-up mid-turn instead of a second send path.
      'Mod-Enter': submit,
      // Shift+Enter — always insert a newline. Tiptap's StarterKit
      // already binds this to HardBreak; we re-bind to `false` (not
      // handled) so the chain falls through cleanly even if other
      // extensions try to grab Shift+Enter.
      'Shift-Enter': () => false,
    };
  },
});
