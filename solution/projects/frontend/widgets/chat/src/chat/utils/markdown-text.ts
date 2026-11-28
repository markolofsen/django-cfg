import { toString } from "mdast-util-to-string";
import remarkGfm from "remark-gfm";
import remarkParse from "remark-parse";
import { unified } from "unified";

/**
 * Markdown → one line of plain text.
 *
 * For surfaces that show a message as a LABEL rather than rendering it: the
 * roster preview, a notification body, a search hit, a chip title. The reader
 * there wants to know WHAT arrived, not to read it, and raw `**bold**` or a
 * table's pipes are this product's internal format leaking out.
 *
 * Built on the parser this package already renders with — `unified` +
 * `remark-parse` + `remark-gfm`, the same stack `streamdown` runs. Not a regex
 * pipeline: those do not merely miss constructs, they EDIT the text, and
 * `file_name_here.txt` losing its underscores is worse than an asterisk
 * surviving.
 */

/** A node's children are separate BLOCKS, so their text must not run together. */
const BLOCK_CONTAINERS = new Set([
  "root",
  "blockquote",
  "list",
  "listItem",
  "table",
  "tableRow",
  "footnoteDefinition",
]);

interface MdNode {
  type: string;
  children?: MdNode[];
  checked?: boolean | null;
  lang?: string | null;
  alt?: string | null;
  url?: string;
}

/**
 * What a block becomes when its CONTENT is not worth reading in one line.
 *
 * A fenced block flattened to text reads as if the agent said it in prose:
 * "const x = 1 const y = 2" is not something anyone wrote. A table is worse —
 * headers and cells collapse into one stream and the structure that made it a
 * table is gone. Both are frequent here, because this product is agents writing
 * code.
 *
 * The glyph is a constant and never translated; the word beside it is supplied
 * by the caller, which is what keeps this file free of an i18n dependency.
 */
export type OpaqueBlock = "code" | "table" | "image" | "formula";

export interface MarkdownTextOptions {
  /**
   * Names for the blocks that collapse to a glyph. A key left out means that
   * block flattens to its text as before — so a caller with no catalogue gets
   * the old behaviour rather than a bare glyph with no word.
   */
  readonly blockLabels?: Partial<Record<OpaqueBlock, string>>;
  /**
   * Re-emit GFM task state as a glyph. A task item carries completion in
   * `checked`, not in its text, so a preview that drops it says an unfinished
   * item is done.
   */
  readonly taskMarks?: boolean;
}

const GLYPH: Record<OpaqueBlock, string> = {
  code: "💻",
  table: "📊",
  image: "📷",
  formula: "🔢",
};

/** `html` nodes are raw by design — mdast does not parse their inner markup.
 *  These strings are message text, so a tag is something a human or an agent
 *  typed: drop the tag, keep the words. NOT sanitisation — every consumer
 *  renders the result as a text node. */
const HTML_TAG = /<\/?[a-zA-Z][^>]*>/g;

const collapse = (s: string): string =>
  s.replace(HTML_TAG, "").replace(/\s+/g, " ").trim();

const TO_STRING_OPTS = { includeImageAlt: true, includeHtml: true } as const;

/** The opaque block this node is, or null when its text should be kept. */
function opaqueKind(node: MdNode): OpaqueBlock | null {
  if (node.type === "code") return "code";
  if (node.type === "table") return "table";
  if (node.type === "image") return "image";
  if (node.type === "math" || node.type === "inlineMath") return "formula";
  return null;
}

function flatten(node: MdNode, options: MarkdownTextOptions): string {
  const labels = options.blockLabels ?? {};
  const kind = opaqueKind(node);
  if (kind !== null) {
    const word = labels[kind];
    // No label supplied: fall through to the text. A bare glyph with no word
    // is less informative than the content it replaced.
    if (word !== undefined) return `${GLYPH[kind]} ${word}`;
  }

  if (!BLOCK_CONTAINERS.has(node.type) || !node.children?.length) {
    return toString(node as Parameters<typeof toString>[0], TO_STRING_OPTS);
  }

  const mark =
    options.taskMarks && node.type === "listItem" && typeof node.checked === "boolean"
      ? node.checked
        ? "✓ "
        : "◻ "
      : "";

  const parts: string[] = [];
  for (const child of node.children) {
    const text = flatten(child, options).trim();
    if (text) parts.push(text);
  }
  // `toString` on a container concatenates blocks bare — two paragraphs come
  // back as "donenext" — so the boundary is reintroduced here. One space is all
  // a single line can express of it.
  return mark + parts.join(" ");
}

const processor = unified().use(remarkParse).use(remarkGfm);

function parse(markdown: string): MdNode | null {
  try {
    return processor.parse(markdown) as unknown as MdNode;
  } catch {
    return null;
  }
}

/**
 * All of the markdown's text on one collapsed line.
 *
 * A parser that throws must not blank the label: showing raw markdown is
 * degraded, showing nothing loses the message entirely.
 */
export function markdownToText(
  markdown: string,
  options: MarkdownTextOptions = {},
): string {
  if (!markdown) return "";
  const tree = parse(markdown);
  if (tree === null) return collapse(markdown);
  return collapse(flatten(tree, { taskMarks: true, ...options }));
}

/**
 * The FIRST block that carries words — for a NAME (row title, chip, search hit).
 *
 * Returns '' when nothing is renderable (a lone fence with no label, a rule, a
 * bare marker), so a caller can fall back to its own placeholder rather than
 * printing punctuation as a name.
 */
export function markdownToLine(
  markdown: string,
  options: MarkdownTextOptions = {},
): string {
  if (!markdown) return "";
  const tree = parse(markdown);
  if (tree === null) return collapse(markdown.split("\n")[0] ?? "");
  const opts = { taskMarks: false, ...options };
  for (const block of tree.children ?? []) {
    const line = collapse(flatten(block, opts));
    if (line) return line;
  }
  return "";
}
