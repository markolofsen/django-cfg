import { Extension } from '@tiptap/core';
import Suggestion, { type SuggestionOptions } from '@tiptap/suggestion';
import type { SlashItem } from './slashItems';

/**
 * Tiptap extension that wires `@tiptap/suggestion` for the slash menu.
 * The actual suggestion config (items / render / floating-ui popup) is
 * passed in via options — keeps this file UI-agnostic and lets the
 * popover live in `createSlashSuggestion.ts`.
 */
export interface SlashExtensionOptions {
  suggestion: Omit<SuggestionOptions<SlashItem>, 'editor'>;
}

export const SlashExtension = Extension.create<SlashExtensionOptions>({
  name: 'notion-slash-command',

  addOptions() {
    return {
      suggestion: { char: '/' } as Omit<SuggestionOptions<SlashItem>, 'editor'>,
    };
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        ...this.options.suggestion,
      }),
    ];
  },
});
