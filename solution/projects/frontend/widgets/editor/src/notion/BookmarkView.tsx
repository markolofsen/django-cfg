'use client';

/**
 * React NodeView for the NotionEditor `bookmark` node. Renders the shared
 * `LinkPreviewCard` (`appearance="full"`) inside a `NodeViewWrapper`, reading
 * the host resolver injected via the node's `extension.options`
 * (`resolveLinkPreview`). Mirrors `TaskItemView` — we only render the UI; the
 * node owns the `url` attribute + markdown serialisation.
 */

import type { ReactNode } from 'react';
import { NodeViewWrapper, type NodeViewProps } from '@tiptap/react';
import { LinkPreviewCard } from '../link-preview';
import { BlockError, LinkPreviewDataSchema, safeParseBlock } from '../blocks';
import type { BookmarkNodeOptions } from './BookmarkNode';

export function BookmarkView({ node, extension }: NodeViewProps) {
  const url = (node.attrs.url as string) || '';
  const resolver = (extension.options as BookmarkNodeOptions).resolveLinkPreview;

  // An empty url is a legitimate "nothing to show yet" state (freshly inserted
  // node) — render nothing. A NON-empty but malformed url fails the schema and
  // shows a safe fallback instead of risking a throw downstream.
  const validated = url ? safeParseBlock(LinkPreviewDataSchema, { url }) : null;

  let content: ReactNode = null;
  if (validated && validated.ok === true) {
    content = <LinkPreviewCard url={validated.data.url} resolver={resolver} appearance="full" />;
  } else if (validated && validated.ok === false) {
    content = <BlockError label="bookmark" reason={validated.error} />;
  }

  return (
    <NodeViewWrapper
      data-type="bookmark"
      className="notion-bookmark"
      // The drag handle reorders the whole block; keep the card from stealing
      // the drag target by marking the wrapper draggable=false (the node is
      // already `draggable: true` at the schema level for the global handle).
      draggable={false}
    >
      {content}
    </NodeViewWrapper>
  );
}
