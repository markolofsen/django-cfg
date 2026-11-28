'use client';

import {
  forwardRef,
  useImperativeHandle,
  useState,
  useCallback,
  useEffect,
  useRef,
  type KeyboardEvent,
} from 'react';
import type { MentionItem } from './types';

export interface MentionListRef {
  onKeyDown: (event: KeyboardEvent) => boolean;
}

interface MentionListProps {
  items: MentionItem[];
  command: (item: MentionItem) => void;
}

export const MentionList = forwardRef<MentionListRef, MentionListProps>(
  ({ items, command }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0);
    // One ref per rendered option so keyboard nav can scroll the active
    // item into view inside the (scrollable, max-height) dropdown.
    const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);

    useEffect(() => setSelectedIndex(0), [items]);

    // Keep the highlighted item visible when ArrowUp/Down moves the
    // selection past the visible window of the dropdown.
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
        // Tab commits the highlighted item too — matches GitHub / Slack /
        // ChatGPT mention pickers. Returning true keeps focus in the editor.
        if (event.key === 'Enter' || event.key === 'Tab') {
          select(selectedIndex);
          return true;
        }
        return false;
      },
    }));

    if (items.length === 0) return null;

    return (
      <div className="markdown-mention-list" role="listbox" aria-label="Mention suggestions">
        {items.map((item, i) => {
          const isSelected = i === selectedIndex;
          const cls = `markdown-mention-item ${isSelected ? 'selected' : ''}`;
          return (
            <button
              key={item.id}
              type="button"
              role="option"
              aria-selected={isSelected}
              ref={(el) => {
                itemRefs.current[i] = el;
              }}
              className={cls}
              // Pointer-driven selection mirrors the keyboard highlight so
              // hovering then clicking never picks a different item.
              onMouseEnter={() => setSelectedIndex(i)}
              onClick={() => select(i)}
            >
              {item.thumbnail && (
                <img src={item.thumbnail} alt="" className="markdown-mention-avatar" />
              )}
              <div className="markdown-mention-info">
                <span className="markdown-mention-name">{item.label}</span>
                {item.description && (
                  <span className="markdown-mention-desc">{item.description}</span>
                )}
              </div>
            </button>
          );
        })}
      </div>
    );
  },
);

MentionList.displayName = 'MentionList';
