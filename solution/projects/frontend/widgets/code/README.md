# @djangocfg/widget-code

Code surfaces: an editor, a diff, a highlighted listing, a JSON editor, and the
markdown renderer that embeds them.

## Install

```bash
pnpm add @djangocfg/widget-code @djangocfg/ui-core @djangocfg/i18n
```

| Subpath | What | Weight |
|---|---|---|
| `./editor` | Monaco, single file or diff | ~550 KB, lazy |
| `./json-editor` | an editable JSON tree | `json-edit-react` |
| `./diff-viewer` | unified or split diff, virtualised | Prism + virtuoso |
| `./diff-viewer/full` | the same, eagerly | |
| `./markdown-message` | markdown with embedded code, diagrams and chips | |
| `./role-tokens` | the `ANCHOR` / `TOGGLE` class contracts | |

## No root barrel worth importing

Monaco alone is ~550 KB, and Prism and `json-edit-react` sit behind their own
subpaths. The root exports the role tokens and nothing else, on purpose.

## Read-only code elsewhere

`PrettyCode` (a read-only listing with a panel header, Prism) lives in
`@djangocfg/widget-kit/pretty-code`, with `/pretty-code/lazy` for the deferred
form; `DiffViewer` and `MarkdownMessage` here use it from there, and so does the
chat's `Response`. `@djangocfg/widget-media/code` is a second, shiki listing with
no consumer in this repo.

## Verify

```bash
pnpm --filter @djangocfg/widget-code check-types test
```
