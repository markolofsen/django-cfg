'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';

/**
 * Creates a debounced version of a callback function.
 *
 * @param callback The function to debounce.
 * @param delay The debounce delay in milliseconds.
 * @returns A debounced callback function.
 */
/** The debounced function, plus the `cancel` handle this hook attaches to it. */
export type DebouncedCallback<T extends (...args: never[]) => unknown> = ((
    ...args: Parameters<T>
) => void) & { cancel: () => void };

export function useDebouncedCallback<T extends (...args: never[]) => unknown>(
    callback: T,
    delay: number
): DebouncedCallback<T> {
    const callbackRef = useRef(callback);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    // Update ref when callback changes, but don't trigger effect
    useEffect(() => {
        callbackRef.current = callback;
    }, [callback]);

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []);

    const cancel = useCallback(() => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }
    }, []);

    // `cancel` is part of the returned type, so it is assembled with the
    // function rather than bolted on afterwards.
    return useMemo(() => {
        const debounced: DebouncedCallback<T> = Object.assign(
            (...args: Parameters<T>) => {
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }

                timeoutRef.current = setTimeout(() => {
                    callbackRef.current(...args);
                }, delay);
            },
            { cancel }
        );
        return debounced;
    }, [delay, cancel]);
}

export default useDebouncedCallback; 