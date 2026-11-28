// Markdown for a reader, outside any conversation: a news post, a file preview.
//
// Sibling to `chat`'s `Response`, which renders the user's own agent and
// relaxes link safety accordingly. This one does not — see `markdown.tsx`.

export { Markdown, type MarkdownProps, type MarkdownSize } from './markdown';
