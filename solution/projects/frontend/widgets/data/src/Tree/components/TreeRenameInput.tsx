'use client';

import { useEffect, useRef, useState } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { autoSelectRange } from '../data/renameUtils';

export interface TreeRenameInputProps {
  initialValue: string;
  isFolder: boolean;
  /** Called with the new (trimmed) name when the user presses Enter / blurs. */
  onCommit: (nextName: string) => void | Promise<unknown>;
  /** Called when the user presses Escape. */
  onCancel: () => void;
  className?: string;
}

/**
 * Inline rename input rendered in place of `<TreeLabel>` while a row is
 * being renamed. Mounts focused with the *base* portion of the name
 * pre-selected (Finder behaviour — `foo.txt` selects `foo`).
 *
 * Behaviour:
 *   - Enter         → commit
 *   - Escape        → cancel (no adapter call)
 *   - blur          → commit (matches Finder; intentional even for empty
 *                     names — the host validates and re-opens on error)
 *   - all other keys are stopped from bubbling so Tree's container
 *     hotkeys (↑↓ delete F2 etc.) don't fire while typing.
 */
export function TreeRenameInput({
  initialValue,
  isFolder,
  onCommit,
  onCancel,
  className,
}: TreeRenameInputProps) {
  const [value, setValue] = useState(initialValue);
  const inputRef = useRef<HTMLInputElement>(null);
  // Track whether we already committed/cancelled so the blur handler
  // doesn't fire a second time after Enter/Escape.
  const settledRef = useRef(false);

  useEffect(() => {
    const el = inputRef.current;
    if (!el) return;
    el.focus();
    const [start, end] = autoSelectRange(initialValue, isFolder);
    // setSelectionRange on a freshly focused input — schedule on next
    // tick to dodge browser quirks where focus() resets the selection.
    requestAnimationFrame(() => {
      try {
        el.setSelectionRange(start, end);
      } catch {
        /* Some input types reject setSelectionRange — safe to ignore. */
      }
    });
    // Run only once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const commit = () => {
    if (settledRef.current) return;
    settledRef.current = true;
    void onCommit(value);
  };

  const cancel = () => {
    if (settledRef.current) return;
    settledRef.current = true;
    onCancel();
  };

  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      // Tree's container hotkeys (delete / arrows / F2 …) must not fire
      // while the user is typing the new name.
      onKeyDown={(e) => {
        e.stopPropagation();
        if (e.key === 'Enter') {
          e.preventDefault();
          commit();
        } else if (e.key === 'Escape') {
          e.preventDefault();
          cancel();
        }
      }}
      onChange={(e) => setValue(e.target.value)}
      onBlur={commit}
      // Prevent click/dblclick on the row from re-firing while the input
      // is mounted (otherwise a focused click commits + re-selects).
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => e.stopPropagation()}
      // Right-click inside the input should be the native input menu,
      // not the row's context menu.
      onContextMenu={(e) => e.stopPropagation()}
      className={cn(
        'min-w-0 flex-1 rounded-sm border border-primary/50 bg-background',
        'px-1 py-0 text-foreground outline-none',
        'focus:ring-1 focus:ring-primary/40',
        className,
      )}
      style={{
        // Match the row's font metrics so the input doesn't visibly jolt.
        fontSize: 'var(--tree-font-size)',
        height: 'calc(var(--tree-row-height) - 4px)',
      }}
    />
  );
}
