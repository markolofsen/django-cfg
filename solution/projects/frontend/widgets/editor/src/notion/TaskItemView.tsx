'use client';

/**
 * React NodeView for `taskItem`. The default Tiptap renderer mints a
 * raw `<input type="checkbox">`; we swap it for our ui-core `<Checkbox>`
 * so task lists pick up the macOS / app token styling (radius, ring,
 * focus state) and stay theme-aware.
 *
 * Wired via `TaskItem.extend({ addNodeView: () => ReactNodeViewRenderer(TaskItemView) })`
 * — TaskItem.attributes already expose `checked` and `editor.commands`
 * persists the change back into ProseMirror state. We only render the UI.
 */

import { NodeViewContent, NodeViewWrapper, type NodeViewProps } from '@tiptap/react';
import { Checkbox } from '@djangocfg/ui-core';

export function TaskItemView({ node, updateAttributes, editor }: NodeViewProps) {
  const checked = node.attrs.checked === true;
  const isEditable = editor.isEditable;

  return (
    <NodeViewWrapper
      as="li"
      data-type="taskList"
      data-checked={checked || undefined}
      className="notion-task-item"
    >
      <Checkbox
        checked={checked}
        disabled={!isEditable}
        onCheckedChange={(value) => updateAttributes({ checked: value === true })}
        // Stop ProseMirror from intercepting the click — without this
        // the editor steals focus mid-toggle and the state flickers.
        onClick={(event) => event.stopPropagation()}
        aria-label={checked ? 'Mark as not done' : 'Mark as done'}
        className="notion-task-checkbox"
      />
      <NodeViewContent as="div" className="notion-task-text" />
    </NodeViewWrapper>
  );
}
