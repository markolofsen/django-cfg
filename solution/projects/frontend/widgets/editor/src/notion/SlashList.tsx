'use client';

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from 'react';
import type { SlashItem } from './slashItems';

export interface SlashListRef {
  /** Forwarded from `@tiptap/suggestion.render().onKeyDown`, which fires
   *  the underlying native `KeyboardEvent` — typing this as React's
   *  synthetic event would be a lie. */
  onKeyDown: (event: KeyboardEvent) => boolean;
}

interface SlashListProps {
  items: SlashItem[];
  command: (item: SlashItem) => void;
}

const LISTBOX_ID = 'notion-slash-menu';

/**
 * Slash-command popover content. Mirrors the MentionList pattern —
 * Arrow keys / Enter / Tab keyboard navigation, mouse hover preview,
 * auto-scroll active item into view.
 */
export const SlashList = forwardRef<SlashListRef, SlashListProps>(
  ({ items, command }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);

    useEffect(() => setSelectedIndex(0), [items]);

    useEffect(() => {
      itemRefs.current[selectedIndex]?.scrollIntoView({ block: 'nearest' });
    }, [selectedIndex]);

    const select = useCallback(
      (index: number) => {
        const item = items[index];
        if (item) command(item);
      },
      [items, command],
    );

    useImperativeHandle(ref, () => ({
      onKeyDown: (event: KeyboardEvent) => {
        if (items.length === 0) return false;
        if (event.key === 'ArrowUp') {
          setSelectedIndex((i) => (i + items.length - 1) % items.length);
          return true;
        }
        if (event.key === 'ArrowDown') {
          setSelectedIndex((i) => (i + 1) % items.length);
          return true;
        }
        if (event.key === 'Enter' || event.key === 'Tab') {
          select(selectedIndex);
          return true;
        }
        return false;
      },
    }));

    // Empty state — render a "no matches" pill instead of vanishing so
    // the user gets feedback that the popover is alive (not a bug).
    if (items.length === 0) {
      return (
        <div
          id={LISTBOX_ID}
          role="listbox"
          aria-label="Slash commands"
          className="notion-slash-list"
        >
          <div className="notion-slash-empty">No matching blocks</div>
        </div>
      );
    }

    const activeId = `${LISTBOX_ID}-${selectedIndex}`;

    return (
      <div
        id={LISTBOX_ID}
        role="listbox"
        aria-label="Slash commands"
        aria-activedescendant={activeId}
        className="notion-slash-list"
      >
        {items.map((item, i) => {
          const Icon = item.icon;
          const isActive = i === selectedIndex;
          return (
            <button
              key={item.title}
              id={`${LISTBOX_ID}-${i}`}
              ref={(el) => {
                itemRefs.current[i] = el;
              }}
              type="button"
              role="option"
              aria-selected={isActive}
              onMouseEnter={() => setSelectedIndex(i)}
              onClick={() => select(i)}
              // Prevent the click from blurring the editor — without this,
              // ProseMirror loses its selection before the slash command
              // can resolve the range.
              onMouseDown={(e) => e.preventDefault()}
              className={`notion-slash-item${isActive ? ' notion-slash-item--active' : ''}`}
            >
              <span className="notion-slash-icon">
                <Icon style={{ width: 16, height: 16 }} aria-hidden />
              </span>
              <span className="notion-slash-meta">
                <span className="notion-slash-title">{item.title}</span>
                <span className="notion-slash-desc">{item.description}</span>
              </span>
              {item.hint ? (
                <span className="notion-slash-hint" aria-hidden>
                  {item.hint}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    );
  },
);

SlashList.displayName = 'SlashList';
