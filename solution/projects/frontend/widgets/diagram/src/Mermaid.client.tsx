'use client';

import React, { useRef } from 'react';

import { useResolvedTheme } from '@djangocfg/ui-core/hooks';
import { FloatingToolbar } from './FloatingToolbar';
import { CopyAction, FullscreenAction } from './FloatingToolbar/actions';
import { MermaidErrorPanel } from './components/MermaidErrorPanel';
import { MermaidFullscreenModal } from './components/MermaidFullscreenModal';
import { useMermaidFullscreen } from './hooks/useMermaidFullscreen';
import { useMermaidRenderer } from './hooks/useMermaidRenderer';
import type { MermaidProps } from './types';


const Mermaid: React.FC<MermaidProps> = ({
    chart,
    className = '',
    isCompact = false,
    fullscreen = true,
    scrollIsolation = false,
    debounceMs = 300,
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const theme = useResolvedTheme();

    // Rendering logic
    const { mermaidRef, svgContent, isVertical, isRendering, error } = useMermaidRenderer({
        chart,
        theme,
        isCompact,
        debounceMs,
    });

    // Fullscreen modal logic (only used if fullscreen prop is true)
    const {
        isFullscreen,
        fullscreenRef,
        openFullscreen,
        closeFullscreen,
        handleBackdropClick,
    } = useMermaidFullscreen();

    // Hoist derived UI state out of JSX (data-before-JSX).
    const hasError = error !== null;
    // The spinner needs a box to sit in while the first diagram renders
    // (empty SVG host has no intrinsic height).
    const showPlaceholderHeight = isRendering && !svgContent && !hasError;
    const showToolbar = !!svgContent && !isRendering && !hasError;

    return (
        <>
            <div ref={containerRef} className={`relative ${className}`}>
                {hasError && <MermaidErrorPanel message={error} />}

                <div
                    ref={mermaidRef}
                    className="flex justify-center items-center"
                    style={{
                        isolation: 'isolate',
                        minHeight: showPlaceholderHeight ? 100 : undefined,
                        display: hasError ? 'none' : undefined,
                    }}
                />

                {isRendering && !hasError && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
                    </div>
                )}

                {showToolbar && (
                    <FloatingToolbar containerRef={containerRef} scrollIsolation={scrollIsolation}>
                        <CopyAction value={chart} title="Copy source" />
                        {fullscreen && (
                            <FullscreenAction onToggle={openFullscreen} title="Fullscreen" />
                        )}
                    </FloatingToolbar>
                )}
            </div>

            {fullscreen && (
                <MermaidFullscreenModal
                    isOpen={isFullscreen}
                    svgContent={svgContent}
                    isVertical={isVertical}
                    theme={theme}
                    chart={chart}
                    fullscreenRef={fullscreenRef}
                    onClose={closeFullscreen}
                    onBackdropClick={handleBackdropClick}
                />
            )}
        </>
    );
};

export default Mermaid;
