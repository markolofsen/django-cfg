# @djangocfg/markdown

Internal Markdown parsing and rendering utilities.

## What's Inside

- Markdown parser with remark/rehype
- Syntax highlighting support
- Type-safe utilities

## Usage

```tsx
import { parseMarkdown, MarkdownRenderer } from '@djangocfg/markdown';

// Parse markdown to HTML
const html = await parseMarkdown('# Hello\n\nWorld');

// Or use component
<MarkdownRenderer content="# Hello" />
```

## Features

- **Syntax Highlighting** - Code blocks with theme support
- **Sanitized Output** - Safe HTML rendering
- **Extensible** - Support for custom remark/rehype plugins

## Dependencies

- `remark` - Markdown processor
- `rehype` - HTML processor
- `unified` - Text processing framework
