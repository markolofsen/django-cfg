import { ReactRenderer } from '@tiptap/react';
import type { SuggestionOptions } from '@tiptap/suggestion';
import { autoUpdate, computePosition, flip, offset, shift } from '@floating-ui/dom';
import { MentionList, type MentionListRef } from './MentionList';
import type { MentionItem, MentionConfig } from './types';

export function createMentionSuggestion(
  config: MentionConfig,
): Omit<SuggestionOptions<MentionItem>, 'editor'> {
  const { maxItems = 5, trigger = '@' } = config;

  return {
    char: trigger,

    items: ({ query }) => {
      const q = query.toLowerCase();
      return config.items
        .filter((item) => item.label.toLowerCase().includes(q))
        .slice(0, maxItems);
    },

    render: () => {
      let component: ReactRenderer<MentionListRef> | null = null;
      let popup: HTMLDivElement | null = null;
      let cleanupAutoUpdate: (() => void) | null = null;
      let getReferenceRect: (() => DOMRect | null) | null = null;

      // Floating-UI virtual element backed by Tiptap's clientRect.
      // We re-read it on every reposition so caret movement is tracked.
      const buildVirtualElement = () => ({
        getBoundingClientRect: () => {
          const rect = getReferenceRect?.();
          // Fallback to a zero-sized rect at origin if the editor is detached
          // (e.g. mid-teardown). Floating-UI tolerates this.
          return rect ?? new DOMRect(0, 0, 0, 0);
        },
      });

      // The popup wrapper is mounted in onStart and removed in onExit.
      // While mounted it must stay hidden whenever MentionList renders
      // nothing (empty query / no matches), otherwise an empty positioned
      // div lingers next to the caret as a ghost block.
      const setPopupVisible = (visible: boolean) => {
        if (popup) popup.style.display = visible ? '' : 'none';
      };

      const updatePosition = () => {
        if (!popup) return;
        const virtualEl = buildVirtualElement();
        void computePosition(virtualEl, popup, {
          placement: 'bottom-start',
          middleware: [
            offset(4),
            flip({ fallbackPlacements: ['top-start'] }),
            shift({ padding: 8 }),
          ],
        }).then(({ x, y }) => {
          if (!popup) return;
          // transform is more performant than top/left and avoids
          // sub-pixel layout thrash during scroll/resize.
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
          component = new ReactRenderer(MentionList, {
            props: {
              items: props.items,
              command: (item: MentionItem) => {
                props.command({ id: item.id, label: item.label });
              },
            },
            editor: props.editor,
          });

          popup = document.createElement('div');
          // top/left at 0; actual position is applied via transform by computePosition.
          popup.style.cssText = 'position: absolute; top: 0; left: 0; z-index: 99999;';
          popup.appendChild(component.element);
          document.body.appendChild(popup);
          setPopupVisible(props.items.length > 0);

          getReferenceRect = () => props.clientRect?.() ?? null;

          // autoUpdate handles scroll, resize, ancestor scroll/resize, layout shifts.
          // It calls updatePosition synchronously on registration too — no manual first call needed.
          const virtualEl = buildVirtualElement();
          cleanupAutoUpdate = autoUpdate(virtualEl, popup, updatePosition);
        },

        onUpdate: (props) => {
          component?.updateProps({
            items: props.items,
            command: (item: MentionItem) => {
              props.command({ id: item.id, label: item.label });
            },
          });

          setPopupVisible(props.items.length > 0);

          // Refresh reference accessor so autoUpdate sees the new caret rect.
          getReferenceRect = () => props.clientRect?.() ?? null;
          updatePosition();
        },

        onKeyDown: (props) => {
          if (props.event.key === 'Escape') {
            teardown();
            return true;
          }
          return component?.ref?.onKeyDown(props.event as unknown as React.KeyboardEvent) ?? false;
        },

        onExit: () => {
          teardown();
        },
      };
    },
  };
}
