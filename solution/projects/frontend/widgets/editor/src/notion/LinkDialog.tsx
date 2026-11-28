'use client';

/**
 * Cmd/Ctrl+K link prompt. Modeless dialog with a single URL input and
 * Save/Remove/Cancel actions. Mounted as a side-channel above the editor
 * so it survives selection collapse — without this, focusing the input
 * would unset the selection and TipTap couldn't apply the mark.
 *
 * We snapshot `from`/`to` of the selection on open and re-apply it
 * before running the link command. ProseMirror tolerates this because
 * the dialog is rendered in a portal (Radix's `DialogPortal`) and the
 * editor's view does not lose its `state` — only its DOM focus.
 */

import { useEffect, useRef, useState } from 'react';
import {
  Button,
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Input,
} from '@djangocfg/ui-core';
import type { Editor } from '@tiptap/react';

/** Reject `javascript:`, `data:`, `vbscript:` schemes. Plain anchors,
 *  http(s), mailto, tel, and relative paths pass. Same allow-list TipTap
 *  uses internally when `validate` is omitted, made explicit here. */
function isSafeHref(value: string): boolean {
  const trimmed = value.trim();
  const colon = trimmed.indexOf(':');
  if (colon === -1) return true; // relative or hash link
  const scheme = trimmed.slice(0, colon).toLowerCase();
  return ['http', 'https', 'mailto', 'tel', 'sms', 'ftp'].includes(scheme);
}

interface LinkDialogProps {
  editor: Editor;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LinkDialog({ editor, open, onOpenChange }: LinkDialogProps) {
  const [href, setHref] = useState('');
  const inputRef = useRef<HTMLInputElement | null>(null);
  // Remember the selection range when the dialog opened — focusing the
  // input collapses selection in the editor; we re-apply the snapshot
  // before running the link command.
  const rangeRef = useRef<{ from: number; to: number } | null>(null);

  useEffect(() => {
    if (!open) return;
    const { from, to } = editor.state.selection;
    rangeRef.current = { from, to };
    const existing = editor.getAttributes('link').href as string | undefined;
    setHref(existing ?? '');
    // Focus is handled by Radix's `onOpenAutoFocus` below — that fires
    // after the dialog DOM is in the document and avoids racing the
    // built-in focus trap.
  }, [open, editor]);

  const applyLink = (value: string) => {
    const range = rangeRef.current;
    if (range) {
      editor.chain().focus().setTextSelection(range).run();
    }
    const trimmed = value.trim();
    if (!trimmed) {
      editor.chain().focus().unsetLink().run();
    } else if (isSafeHref(trimmed)) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: trimmed }).run();
    }
    onOpenChange(false);
  };

  const removeLink = () => {
    const range = rangeRef.current;
    if (range) {
      editor.chain().focus().setTextSelection(range).run();
    }
    editor.chain().focus().unsetLink().run();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="sm:max-w-md"
        // Override Radix's default auto-focus (first focusable). We want
        // the URL input focused + selected — combining `preventDefault`
        // here with a direct `focus()` call sequences cleanly with the
        // dialog mount; the earlier queueMicrotask version raced Radix.
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          inputRef.current?.focus();
          inputRef.current?.select();
        }}
      >
        <DialogHeader>
          <DialogTitle>Link</DialogTitle>
        </DialogHeader>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            applyLink(href);
          }}
        >
          <Input
            ref={inputRef}
            type="url"
            placeholder="https://example.com"
            value={href}
            onChange={(e) => setHref(e.target.value)}
            autoComplete="off"
            spellCheck={false}
          />
          <DialogFooter className="mt-4 gap-2 sm:gap-2">
            {editor.isActive('link') ? (
              <Button type="button" variant="outline" onClick={removeLink}>
                Remove
              </Button>
            ) : null}
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">Save</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
