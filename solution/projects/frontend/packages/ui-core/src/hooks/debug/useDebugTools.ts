'use client';

import { useDebugValue } from 'react';

type DebugValue = Record<string, unknown> | unknown[] | null | undefined;

export function useDebugTools(values: DebugValue, prefix = '') {
    // useDebugValue must be called EXACTLY ONCE and UNCONDITIONALLY. The prior
    // version called it inside branches and per-array-element/object-key loops,
    // so the hook count varied with the shape of `values` between renders —
    // a rules-of-hooks violation (React #310 territory). Instead, call it once
    // with a lazy formatter that builds the full multi-line label; the formatter
    // still only runs when React DevTools inspects the hook, so nothing is
    // eagerly serialized in normal renders.
    useDebugValue(values, (v) => formatDebugValues(v, prefix));
}

function formatDebugValues(values: DebugValue, prefix: string): string {
    if (values === null || values === undefined) {
        return `${prefix}: ${values === null ? 'null' : 'undefined'}`;
    }

    if (Array.isArray(values)) {
        return values
            .map((value, index) => {
                const label = prefix ? `${prefix}[${index}]` : `[${index}]`;
                return `${label}: ${formatValue(value)}`;
            })
            .join('\n');
    }

    if (typeof values === 'object') {
        return Object.entries(values)
            .map(([key, value]) => {
                const label = prefix ? `${prefix}.${key}` : key;
                return `${label}: ${formatValue(value)}`;
            })
            .join('\n');
    }

    // Primitive
    return `${prefix}: ${formatValue(values)}`;
}

function formatValue(value: unknown): string {
    if (value === null) return 'null';
    if (value === undefined) return 'undefined';

    try {
        if (typeof value === 'object') {
            if (Array.isArray(value)) {
                return `Array(${value.length})`;
            }
            return JSON.stringify(value);
        }
        return String(value);
    } catch {
        return '[Unserializable]';
    }
}
