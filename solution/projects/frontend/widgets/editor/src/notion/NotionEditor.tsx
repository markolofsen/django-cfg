'use client';

/**
 * NotionEditor — Notion-style WYSIWYG built on TipTap v3.
 *
 * Composition (vs `MarkdownEditor`):
 *   - StarterKit (with H1-H4) + Placeholder + Markdown serialiser
 *   - TaskList + TaskItem (GFM `- [ ]`)
 *   - Table (+ Row/Header/Cell)
 *   - CodeBlockLowlight (syntax highlight via lowlight's `common` pack)
 *   - Highlight (`==text==`)
 *   - GlobalDragHandle (Notion-style block grabbers)
 *   - SlashExtension (own `/` menu — see SlashList.tsx)
 *   - BubbleMenu (floating selection toolbar)
 *
 * Why a separate component instead of a variant on MarkdownEditor:
 *   - Different baseline (no mentions, no slash-as-chip extension that
 *     the chat composer depends on).
 *   - ~30KB more deps (tables, lowlight, drag-handle) — would punish
 *     every chat composer mount if added to the shared editor.
 *   - Lazy chunk boundary stays clean — Skills / chat composer keep
 *     their slim TipTap; document-preview pulls the heavy stack.
 */

import { useEditor, EditorContent, type Editor } from '@tiptap/react';
import { BubbleMenu } from '@tiptap/react/menus';
import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import {
  Bold,
  Italic,
  Strikethrough,
  Code as CodeIcon,
  Highlighter,
  Link as LinkIcon,
  Underline as UnderlineIcon,
  type LucideIcon,
} from 'lucide-react';
import { TooltipHint } from '@djangocfg/ui-core';
import { useHotkey } from '@djangocfg/ui-core/hooks';
import { notionExtensions } from './extensions';
import { LinkDialog } from './LinkDialog';
import type { NotionEditorHandle, NotionEditorProps } from './types';
import './styles.css';

// Same markdown helper as MarkdownEditor — TipTap v3 augments Editor with
// `getMarkdown()` when @tiptap/markdown is registered.
interface MarkdownManager {
  serialize: (json: Record<string, unknown>) => string;
}
function getMarkdown(editor: Editor): string {
  const withMd = editor as Editor & { getMarkdown?: () => string };
  if (typeof withMd.getMarkdown === 'function') return withMd.getMarkdown();
  const storage = editor.storage.markdown as { manager?: MarkdownManager } | undefined;
  if (!storage?.manager) return editor.getText();
  return storage.manager.serialize(editor.getJSON());
}

export const NotionEditor = forwardRef<NotionEditorHandle, NotionEditorProps>(
  function NotionEditor(
    {
      value,
      onChange,
      placeholder = "Type '/' for commands…",
      disabled = false,
      autoFocus = false,
      onSave,
      className = '',
      minHeight = 320,
      resolveLinkPreview,
    },
    ref,
  ) {
    const isExternalUpdate = useRef(false);
    const [linkDialogOpen, setLinkDialogOpen] = useState(false);

    // Build extensions once. Placeholder is captured by closure on first
    // render — same constraint as MarkdownEditor; mentions / slash items
    // don't change at runtime here. The link-preview resolver is likewise
    // captured on first build; pass a stable reference (it's a host method).
    const extensions = useMemo(
      () => notionExtensions({ placeholder, resolveLinkPreview }),
      [placeholder, resolveLinkPreview],
    );

    const editor = useEditor({
      immediatelyRender: false,
      editable: !disabled,
      extensions,
      content: value,
      contentType: 'markdown',
      onUpdate: ({ editor }) => {
        if (isExternalUpdate.current) return;
        onChange(getMarkdown(editor));
      },
      editorProps: {
        attributes: {
          class: 'notion-editor-content focus:outline-none',
          style: `min-height: ${minHeight}px`,
        },
      },
    });

    // Sync external value → editor without looping back into onChange.
    useEffect(() => {
      if (!editor) return;
      const current = getMarkdown(editor);
      if (current === value) return;
      isExternalUpdate.current = true;
      editor.commands.setContent(value, {
        contentType: 'markdown',
        emitUpdate: false,
      });
      isExternalUpdate.current = false;
    }, [value, editor]);

    useEffect(() => {
      editor?.setEditable(!disabled);
    }, [editor, disabled]);

    // Declarative autoFocus.
    useEffect(() => {
      if (!autoFocus || !editor) return;
      editor.commands.focus('end');
    }, [autoFocus, editor]);

    // Cmd/Ctrl+S → save, scoped to the editor DOM via guard.
    const onSaveRef = useRef(onSave);
    onSaveRef.current = onSave;
    useHotkey(
      'mod+s',
      () => {
        const h = onSaveRef.current;
        if (!h || !editor) return;
        const dom = editor.view.dom;
        const active = document.activeElement;
        if (!active || !dom.contains(active)) return;
        h(getMarkdown(editor));
      },
      { enabled: !!editor && !!onSave },
    );

    // Cmd/Ctrl+K → link prompt. Same focus-scope guard so we don't
    // collide with global command palettes higher up the tree.
    useHotkey(
      'mod+k',
      () => {
        if (!editor) return;
        const dom = editor.view.dom;
        const active = document.activeElement;
        if (!active || !dom.contains(active)) return;
        setLinkDialogOpen(true);
      },
      { enabled: !!editor },
    );

    useImperativeHandle(
      ref,
      (): NotionEditorHandle => ({
        focus: () => {
          editor?.commands.focus();
        },
        moveCursorToEnd: () => {
          editor?.commands.focus('end');
        },
        getEditor: () => editor ?? null,
      }),
      [editor],
    );

    return (
      <div className={`notion-editor ${disabled ? 'opacity-60' : ''} ${className}`.trim()}>
        {editor ? (
          <>
            <BubbleSelectionToolbar
              editor={editor}
              onOpenLink={() => setLinkDialogOpen(true)}
            />
            <LinkDialog
              editor={editor}
              open={linkDialogOpen}
              onOpenChange={setLinkDialogOpen}
            />
          </>
        ) : null}
        <EditorContent editor={editor} />
      </div>
    );
  },
);

interface BubbleItem {
  icon: LucideIcon;
  title: string;
  /** Keyboard shortcut to display in the tooltip. `useHotkey` string (mod+b). */
  hotkey: string;
  isActive: () => boolean;
  run: () => void;
}

/**
 * Floating selection toolbar. `@tiptap/extension-bubble-menu` anchors
 * itself to the current selection; it auto-hides when the selection
 * collapses, so we only need to declare the buttons. Tooltips show the
 * keyboard chord — Tiptap installs the shortcuts itself (StarterKit).
 */
function BubbleSelectionToolbar({
  editor,
  onOpenLink,
}: {
  editor: Editor;
  onOpenLink: () => void;
}) {
  const items: BubbleItem[] = [
    {
      icon: Bold,
      title: 'Bold',
      hotkey: 'mod+b',
      isActive: () => editor.isActive('bold'),
      run: () => editor.chain().focus().toggleBold().run(),
    },
    {
      icon: Italic,
      title: 'Italic',
      hotkey: 'mod+i',
      isActive: () => editor.isActive('italic'),
      run: () => editor.chain().focus().toggleItalic().run(),
    },
    {
      icon: UnderlineIcon,
      title: 'Underline',
      hotkey: 'mod+u',
      isActive: () => editor.isActive('underline'),
      run: () => editor.chain().focus().toggleUnderline().run(),
    },
    {
      icon: Strikethrough,
      title: 'Strike',
      hotkey: 'mod+shift+x',
      isActive: () => editor.isActive('strike'),
      run: () => editor.chain().focus().toggleStrike().run(),
    },
    {
      icon: CodeIcon,
      title: 'Inline code',
      hotkey: 'mod+e',
      isActive: () => editor.isActive('code'),
      run: () => editor.chain().focus().toggleCode().run(),
    },
    {
      icon: Highlighter,
      title: 'Highlight',
      hotkey: 'mod+shift+h',
      isActive: () => editor.isActive('highlight'),
      run: () => editor.chain().focus().toggleHighlight().run(),
    },
    {
      icon: LinkIcon,
      title: 'Link',
      hotkey: 'mod+k',
      isActive: () => editor.isActive('link'),
      run: onOpenLink,
    },
  ];

  return (
    <BubbleMenu
      editor={editor}
      className="notion-bubble-menu"
      // Hide inside code blocks (Bold/Italic don't apply there) and when
      // the selection is empty/whitespace-only. Default behaviour shows
      // the menu on any non-empty range, which is too eager.
      shouldShow={({ editor, from, to }) => {
        if (from === to) return false;
        if (editor.isActive('codeBlock')) return false;
        const text = editor.state.doc.textBetween(from, to, ' ').trim();
        return text.length > 0;
      }}
    >
      {items.map((item) => {
        const Icon = item.icon;
        const active = item.isActive();
        return (
          <TooltipHint key={item.title} tooltip={{ content: item.title, hotkey: item.hotkey, side: 'top', sideOffset: 6 }}>
            <button
              type="button"
              aria-label={item.title}
              aria-pressed={active}
              onMouseDown={(e) => e.preventDefault()}
              onClick={item.run}
              className={`notion-bubble-btn${active ? ' notion-bubble-btn--active' : ''}`}
            >
              <Icon style={{ width: 14, height: 14 }} aria-hidden />
            </button>
          </TooltipHint>
        );
      })}
    </BubbleMenu>
  );
}
