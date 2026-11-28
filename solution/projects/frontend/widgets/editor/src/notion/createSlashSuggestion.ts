import { ReactRenderer } from '@tiptap/react';
import type { SuggestionOptions } from '@tiptap/suggestion';
import { autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom';
import { SlashList, type SlashListRef } from './SlashList';
import { filterSlashItems, type SlashItem } from './slashItems';

/**
 * `@tiptap/suggestion` config for the slash menu. Mirrors the mention
 * suggestion pattern in `MarkdownEditor/createMentionSuggestion.ts`:
 * floating-ui positioning, virtual element backed by the caret rect,
 * keyboard nav delegated to `SlashList` via an imperative ref.
 *
 * Editor never imports this directly — `notionExtensions()` consumes it.
 */
export function createSlashSuggestion(): Omit<SuggestionOptions<SlashItem>, 'editor'> {
  return {
    char: '/',
    // Block the menu inside code blocks — `/` is valid syntax there
    // (regex literals, paths) and a floating popover would be noise.
    // Use `editor.isActive('codeBlock')` rather than `state.doc.resolve()`
    // so nested cases (code block in a table cell, in a list item) all
    // resolve correctly — `parent.type.name` only sees the immediate
    // ancestor, which can be the cell/li instead of the code block.
    allow: ({ editor }) => !editor.isActive('codeBlock'),
    items: ({ query }) => filterSlashItems(query),
    command: ({ editor, range, props }) => {
      props.command({ editor, range });
    },

    render: () => {
      let component: ReactRenderer<SlashListRef> | null = null;
      let popup: HTMLDivElement | null = null;
      let cleanupAutoUpdate: (() => void) | null = null;
      let getReferenceRect: (() => DOMRect | null) | null = null;

      const buildVirtualElement = () => ({
        getBoundingClientRect: () => getReferenceRect?.() ?? new DOMRect(0, 0, 0, 0),
      });

      const setPopupVisible = (visible: boolean) => {
        if (popup) popup.style.display = visible ? '' : 'none';
      };

      const updatePosition = () => {
        if (!popup) return;
        const virtualEl = buildVirtualElement();
        void computePosition(virtualEl, popup, {
          placement: 'bottom-start',
          middleware: [
            offset(6),
            flip({ fallbackPlacements: ['top-start'] }),
            shift({ padding: 8 }),
          ],
        }).then(({ x, y }) => {
          if (!popup) return;
          popup.style.transform = `translate3d(${Math.round(x)}px, ${Math.round(y)}px, 0)`;
        });
      };

      const teardown = () => {
        cleanupAutoUpdate?.();
        cleanupAutoUpdate = null;
        popup?.remove();
        popup = null;
        component?.destroy();
        component = null;
        getReferenceRect = null;
      };

      return {
        onStart: (props) => {
          component = new ReactRenderer(SlashList, {
            props: {
              items: props.items,
              command: (item: SlashItem) => {
                props.command(item);
              },
            },
            editor: props.editor,
          });

          popup = document.createElement('div');
          popup.style.cssText = 'position: absolute; top: 0; left: 0; z-index: 99999;';
          popup.appendChild(component.element);
          document.body.appendChild(popup);
          setPopupVisible(props.items.length > 0);

          getReferenceRect = () => props.clientRect?.() ?? null;
          const virtualEl = buildVirtualElement();
          cleanupAutoUpdate = autoUpdate(virtualEl, popup, updatePosition);
        },

        onUpdate: (props) => {
          component?.updateProps({
            items: props.items,
            command: (item: SlashItem) => {
              props.command(item);
            },
          });
          setPopupVisible(props.items.length > 0);
          getReferenceRect = () => props.clientRect?.() ?? null;
          updatePosition();
        },

        onKeyDown: (props) => {
          if (props.event.key === 'Escape') {
            teardown();
            return true;
          }
          // `props.event` is a native KeyboardEvent — SlashListRef types
          // it as such, no cast needed.
          return component?.ref?.onKeyDown(props.event) ?? false;
        },

        onExit: () => {
          teardown();
        },
      };
    },
  };
}
