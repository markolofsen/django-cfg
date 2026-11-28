'use client';

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { TransformWrapper, TransformComponent, useControls } from 'react-zoom-pan-pinch';

import { Button } from '@djangocfg/ui-core/components';
import { applyMermaidTextColors, getTextColor } from '../utils/mermaid-helpers';

interface MermaidFullscreenModalProps {
    isOpen: boolean;
    svgContent: string;
    /**
     * Whether the source diagram is vertical. Kept for API compatibility
     * with callers; the modal now auto-fits via measured bbox so it no
     * longer needs an orientation hint.
     */
    isVertical?: boolean;
    theme: string;
    /** Diagram source. Reserved for future modal actions (copy/export). */
    chart?: string;
    fullscreenRef: React.RefObject<HTMLDivElement | null>;
    onClose: () => void;
    onBackdropClick: (e: React.MouseEvent) => void;
}

// Zoom controls component
function ZoomControls() {
    const { zoomIn, zoomOut, resetTransform } = useControls();

    return (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
            <Button variant="secondary" size="icon" onClick={() => zoomOut()}>
                <ZoomOut className="h-4 w-4" />
            </Button>
            <Button variant="secondary" size="icon" onClick={() => resetTransform()}>
                <RotateCcw className="h-4 w-4" />
            </Button>
            <Button variant="secondary" size="icon" onClick={() => zoomIn()}>
                <ZoomIn className="h-4 w-4" />
            </Button>
        </div>
    );
}

export const MermaidFullscreenModal: React.FC<MermaidFullscreenModalProps> = ({
    isOpen,
    svgContent,
    theme,
    fullscreenRef,
    onClose,
    onBackdropClick,
}) => {
    // Auto-fit scale on open. Two failure modes drove this design:
    //
    //   1. Stale state across re-opens. Without a reset, the second
    //      open would still see the previous fit value in state; if
    //      the new SVG had the same dimensions the `key` swap below
    //      wouldn't fire and TransformWrapper would skip re-init.
    //   2. SVG not in DOM yet at first rAF. Mermaid renders into
    //      `fullscreenRef` after the modal portal mounts; on a fast
    //      paint the first `querySelector('svg')` returned null and
    //      the scale stayed at the fallback `1`. Retry across a few
    //      frames until the bbox is real, then commit.
    //
    // `openSeq` increments on every open so the `key` always changes,
    // forcing a fresh TransformWrapper instance even when the fit
    // value happens to repeat.
    const [initialScale, setInitialScale] = useState<number | null>(null);
    const [openSeq, setOpenSeq] = useState(0);
    useEffect(() => {
        if (!isOpen) {
            // Reset so the next open recomputes from scratch.
            setInitialScale(null);
            return;
        }
        setOpenSeq((n) => n + 1);
        let cancelled = false;
        let attempts = 0;
        const tick = () => {
            if (cancelled) return;
            attempts += 1;
            const svg = fullscreenRef.current?.querySelector('svg');
            const bbox = svg?.getBoundingClientRect();
            if (svg && bbox && bbox.width > 1 && bbox.height > 1) {
                const targetW = window.innerWidth * 0.9;
                const targetH = window.innerHeight * 0.9;
                const fit = Math.min(targetW / bbox.width, targetH / bbox.height);
                setInitialScale(Math.max(1, Math.min(fit, 6)));
                return;
            }
            // Give Mermaid up to ~30 frames (~0.5s @ 60fps) to paint
            // before settling for the unscaled fallback.
            if (attempts < 30) {
                requestAnimationFrame(tick);
            } else {
                setInitialScale(1);
            }
        };
        requestAnimationFrame(tick);
        return () => {
            cancelled = true;
        };
    }, [isOpen, svgContent, fullscreenRef]);

    // Re-assert theme text colors on the fullscreen SVG. The shared
    // `getTextColor` reads the (already fully-wrapped) `--foreground`
    // token — it never double-wraps `hsl(...)`.
    useEffect(() => {
        if (isOpen && fullscreenRef.current) {
            applyMermaidTextColors(fullscreenRef.current, getTextColor(theme));
        }
    }, [isOpen, theme, fullscreenRef, svgContent]);

    // Handle escape key
    useEffect(() => {
        if (!isOpen) return;

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    if (!isOpen || typeof document === 'undefined') return null;

    // Hoist derived values out of JSX (COMPONENTS.md "Data Preparation
    // Before Render"). Keeps the returned tree pure markup, makes it
    // obvious at the top of the function which inputs feed which
    // node, and surfaces every dependency to a reader at a glance.
    const transformInitialScale = initialScale ?? 1;
    const transformKey = `${openSeq}-${initialScale ?? 'pending'}`;

    return createPortal(
        <div
            className="fixed inset-0 z-9999 bg-background/95 backdrop-blur-sm"
            onClick={onBackdropClick}
        >
            {/* Close button */}
            <Button
                variant="ghost"
                size="icon"
                className="absolute top-4 right-4 z-10"
                onClick={onClose}
            >
                <X className="h-5 w-5" />
            </Button>

            {/* Zoomable diagram. `key={openSeq}-${initialScale ?? 'pending'}`
                forces a fresh TransformWrapper:
                  - on every modal open (openSeq increments) so the
                    re-opened modal never inherits the prior session's
                    transform;
                  - whenever the auto-fit value lands (null → number)
                    so the wrapper, which only reads `initialScale`
                    at mount time, picks up the freshly measured fit.
                We can't gate the whole subtree on `initialScale != null`
                because the SVG host (`fullscreenRef` div) lives inside
                TransformComponent — without it in the DOM, the rAF
                measure loop has nothing to read and we'd deadlock at
                null forever. Mounting with placeholder `1` first and
                re-mounting once we know the fit is the cheap fix. */}
            <TransformWrapper
                key={transformKey}
                initialScale={transformInitialScale}
                minScale={0.1}
                maxScale={10}
                centerOnInit
                wheel={{ step: 0.1 }}
                pinch={{ step: 5 }}
                doubleClick={{ mode: 'reset' }}
            >
                <ZoomControls />
                <TransformComponent
                    wrapperStyle={{
                        width: '100%',
                        height: '100%',
                    }}
                    contentStyle={{
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <div
                        ref={fullscreenRef}
                        className="p-8"
                        dangerouslySetInnerHTML={{ __html: svgContent }}
                        onClick={(e) => e.stopPropagation()}
                    />
                </TransformComponent>
            </TransformWrapper>
        </div>,
        document.body
    );
};
