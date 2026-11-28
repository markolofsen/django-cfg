/**
 * Hook for validating Mermaid code completeness.
 *
 * Purpose: while a diagram is being *streamed* (token by token from an
 * LLM, or typed) the source is briefly invalid. Rendering it would throw
 * a parse error and flash an error panel on every keystroke. This
 * heuristic detects "obviously still-being-written" source so the
 * renderer can wait instead. It is intentionally conservative — false
 * "complete" is fine (the real parser catches it), false "incomplete"
 * just delays a render.
 */

import { useCallback } from 'react';

/** Diagram keywords that, alone, are a valid first line. */
const DIAGRAM_KEYWORDS = [
    'graph',
    'flowchart',
    'sequenceDiagram',
    'classDiagram',
    'stateDiagram',
    'stateDiagram-v2',
    'erDiagram',
    'journey',
    'gantt',
    'pie',
    'mindmap',
    'timeline',
    'gitGraph',
    'quadrantChart',
    'requirementDiagram',
    'C4Context',
    'sankey-beta',
    'xychart-beta',
    'block-beta',
];

/** Count occurrences of a character that are not inside a quoted string. */
function countUnquoted(text: string, open: string, close: string): number {
    let depth = 0;
    let inQuote = false;
    for (let i = 0; i < text.length; i++) {
        const ch = text[i];
        if (ch === '"') {
            inQuote = !inQuote;
            continue;
        }
        if (inQuote) continue;
        if (ch === open) depth++;
        else if (ch === close) depth--;
    }
    return depth;
}

export function useMermaidValidation() {
    const isMermaidCodeComplete = useCallback((code: string): boolean => {
        if (!code || code.trim().length === 0) return false;

        const trimmed = code.trim();

        // Must start with a recognised diagram keyword. During streaming
        // the very first tokens may be a partial keyword — wait for it.
        const firstToken = trimmed.split(/[\s\n;]/)[0] ?? '';
        const hasKnownType = DIAGRAM_KEYWORDS.some(
            (kw) => firstToken === kw || trimmed.startsWith(kw),
        );
        if (!hasKnownType) return false;

        const lines = trimmed.split('\n');
        const lastLine = (lines[lines.length - 1] ?? '').trim();

        // Trailing edge with no destination: `A -->` / `A --` / `A -.->`.
        if (/(-{1,3}>?|={1,3}>?|-\.->?|\.\.>?|--[ox])\s*$/.test(lastLine)) {
            return false;
        }
        // Trailing edge label still open: `A -->|label` (no closing `|`).
        if (/-{1,3}>?\s*\|[^|]*$/.test(lastLine)) return false;

        // Unbalanced shape brackets across the whole source (open > close).
        if (countUnquoted(trimmed, '[', ']') > 0) return false;
        if (countUnquoted(trimmed, '(', ')') > 0) return false;
        // ER diagrams use `{` / `}` for crow's-foot cardinality
        // (`||--o{`, `}|--||`) — those braces are deliberately unbalanced
        // and must not be counted, or the diagram never renders.
        if (!trimmed.startsWith('erDiagram') && countUnquoted(trimmed, '{', '}') > 0) {
            return false;
        }

        // Odd number of double quotes — an unterminated string literal.
        const quoteCount = (trimmed.match(/"/g) ?? []).length;
        if (quoteCount % 2 !== 0) return false;

        return true;
    }, []);

    return { isMermaidCodeComplete };
}
