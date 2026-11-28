import { useEffect, useState } from 'react';

/** Debounce a fast-changing value. Used for the sidebar search box so
 *  each keystroke doesn't re-run the filter pipeline (endpoint list
 *  can be hundreds of items long in some specs). 120ms is short
 *  enough to feel instant while still batching rapid typing. */
export function useDebouncedValue<T>(value: T, delayMs = 120): T {
    const [debounced, setDebounced] = useState(value);
    useEffect(() => {
        const id = setTimeout(() => setDebounced(value), delayMs);
        return () => clearTimeout(id);
    }, [value, delayMs]);
    return debounced;
}
