/**
 * Hook for cleaning up orphaned Mermaid DOM nodes
 */

import { useCallback, useEffect } from 'react';

export function useMermaidCleanup() {
    const cleanupMermaidErrors = useCallback(() => {
        if (typeof document === 'undefined') return;

        // Remove all orphaned mermaid elements from body
        // Mermaid can append: SVGs, divs with errors, text nodes

        // 1. Remove elements with mermaid-* IDs directly in body
        document.querySelectorAll('[id^="mermaid-"]').forEach((node) => {
            if (node.parentNode === document.body) {
                node.remove();
            }
        });

        // 2. Remove elements with d prefix (mermaid diagram IDs) directly in body
        document.querySelectorAll('[id^="d"]').forEach((node) => {
            if (node.parentNode === document.body && node.id.match(/^d\d+$/)) {
                node.remove();
            }
        });

        // 3. Remove orphaned SVG elements that mermaid creates in body
        document.querySelectorAll('body > svg').forEach((node) => {
            // Check if it's a mermaid SVG (has mermaid classes or aria-roledescription)
            if (node.getAttribute('aria-roledescription') ||
                node.classList.contains('mermaid') ||
                node.querySelector('.mermaid') ||
                node.id?.includes('mermaid')) {
                node.remove();
            }
        });

        // 4. Remove any orphaned error divs with "Syntax error" text
        document.querySelectorAll('body > div').forEach((node) => {
            const text = node.textContent || '';
            if (text.includes('Syntax error in text') ||
                text.includes('mermaid version') ||
                node.id?.startsWith('mermaid-') ||
                node.id?.startsWith('d') && node.id.match(/^d\d+$/)) {
                node.remove();
            }
        });

        // 5. Remove orphaned pre elements with error info
        document.querySelectorAll('body > pre').forEach((node) => {
            const text = node.textContent || '';
            if (text.includes('Syntax error') || text.includes('mermaid')) {
                node.remove();
            }
        });
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            cleanupMermaidErrors();
        };
    }, [cleanupMermaidErrors]);

    // Removed periodic cleanup - it causes unnecessary re-renders
    // Cleanup only happens on unmount now

    return { cleanupMermaidErrors };
}
