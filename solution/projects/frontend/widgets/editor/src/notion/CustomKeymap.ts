import { Extension } from '@tiptap/core';
import { TextSelection } from '@tiptap/pm/state';

/**
 * Notion-style smart Cmd/Ctrl+A:
 *   1st press → select the current text block
 *   2nd press → select the whole document
 *
 * Default editor behaviour selects everything on first press, which is
 * jarring in long documents where the user almost always wants "select
 * paragraph" first. Ported from Novel (`extensions/custom-keymap.ts`).
 */
export const CustomKeymap = Extension.create({
  name: 'notion-custom-keymap',

  addKeyboardShortcuts() {
    return {
      'Mod-a': ({ editor }) => {
        const { selection, doc } = editor.state;
        const { $from, $to, from, to } = selection;

        // Resolve the boundaries of the current text block. `start`/`end`
        // on $from/$to give the inclusive content range of the parent
        // textblock (a paragraph, heading, code block, list item body).
        const blockStart = $from.start();
        const blockEnd = $to.end();

        const isWholeBlockSelected = from === blockStart && to === blockEnd;
        // If the block is already fully selected → escalate to whole doc.
        if (isWholeBlockSelected) {
          editor
            .chain()
            .setTextSelection({ from: 0, to: doc.content.size })
            .run();
          return true;
        }

        editor
          .chain()
          .setTextSelection(
            TextSelection.create(editor.state.doc, blockStart, blockEnd),
          )
          .run();
        return true;
      },
    };
  },
});
