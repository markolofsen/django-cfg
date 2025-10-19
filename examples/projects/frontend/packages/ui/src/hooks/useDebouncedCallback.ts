import { useCallback, useEffect, useRef } from 'react';

/**
 * Creates a debounced version of a callback function.
 *
 * @param callback The function to debounce.
 * @param delay The debounce delay in milliseconds.
 * @returns A debounced callback function.
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
    callback: T,
    delay: number
): (...args: Parameters<T>) => void {
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

    const debouncedCallback = useCallback(
        (...args: Parameters<T>) => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            timeoutRef.current = setTimeout(() => {
                callbackRef.current(...args);
            }, delay);
        },
        [delay]
    );

    // Add a cancel method to the debounced function
    // We attach it directly to the function object
    (debouncedCallback as any).cancel = useCallback(() => {
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }
    }, []);

    return debouncedCallback;
}

export default useDebouncedCallback; 