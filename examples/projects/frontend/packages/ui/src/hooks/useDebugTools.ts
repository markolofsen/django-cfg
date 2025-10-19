import { useDebugValue } from 'react';

type DebugValue = Record<string, unknown> | unknown[] | null | undefined;

export function useDebugTools(values: DebugValue, prefix = '') {
    if (values === null || values === undefined) {
        useDebugValue(values, () => `${prefix}: ${values === null ? 'null' : 'undefined'}`);
        return;
    }

    if (Array.isArray(values)) {
        values.forEach((value, index) => {
            useDebugValue(value, (v) => {
                const label = prefix ? `${prefix}[${index}]` : `[${index}]`;
                return `${label}: ${formatValue(v)}`;
            });
        });
        return;
    }

    if (typeof values === 'object') {
        for (const [key, value] of Object.entries(values)) {
            useDebugValue(value, (v) => {
                const label = prefix ? `${prefix}.${key}` : key;
                return `${label}: ${formatValue(v)}`;
            });
        }
        return;
    }

    // Handle primitive values
    useDebugValue(values, (v) => `${prefix}: ${formatValue(v)}`);
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
