/**
 * Hook for managing Mermaid fullscreen modal
 */

import { useEffect, useRef, useState } from 'react';

export function useMermaidFullscreen() {
    const [isFullscreen, setIsFullscreen] = useState(false);
    const fullscreenRef = useRef<HTMLDivElement>(null);

    const openFullscreen = () => setIsFullscreen(true);
    const closeFullscreen = () => setIsFullscreen(false);

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            closeFullscreen();
        }
    };

    // Handle ESC key
    useEffect(() => {
        const handleEscKey = (event: KeyboardEvent) => {
            if (event.key === 'Escape' && isFullscreen) {
                closeFullscreen();
            }
        };

        if (isFullscreen) {
            document.addEventListener('keydown', handleEscKey);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscKey);
            document.body.style.overflow = 'unset';
        };
    }, [isFullscreen]);

    return {
        isFullscreen,
        fullscreenRef,
        openFullscreen,
        closeFullscreen,
        handleBackdropClick,
    };
}
