/**
 * Hook for rendering Mermaid diagrams with debounced, race-safe rendering.
 *
 * Mermaid (~800KB) is imported eagerly here because the whole component
 * tree is already lazy-loaded behind `Mermaid.client` — splitting again
 * would just add a second waterfall for no win.
 */

import mermaid from 'mermaid';
import { useEffect, useRef, useState } from 'react';

import {
    applyMermaidErRowColors,
    applyMermaidTextColors,
    getThemeColor,
    getTextColor,
    isVerticalDiagram,
} from '../utils/mermaid-helpers';
import { useMermaidCleanup } from './useMermaidCleanup';
import { useMermaidValidation } from './useMermaidValidation';

interface UseMermaidRendererProps {
    chart: string;
    theme: string;
    isCompact?: boolean;
    /** Debounce window in ms before (re)rendering. Default 300. */
    debounceMs?: number;
}

interface MermaidRenderResult {
    mermaidRef: React.RefObject<HTMLDivElement | null>;
    svgContent: string;
    isVertical: boolean;
    isRendering: boolean;
    /** Set when the last render failed with a syntax / parse error. */
    error: string | null;
}

/**
 * Section color scales for timeline / journey / mindmap / pie diagrams.
 *
 * These diagram types do NOT use `mainBkg` for their boxes — they cycle
 * through `cScale0..N` (and `pie1..N`) instead. Mermaid's `base` theme
 * derives those scales from `primaryColor`, which lands far too dark in
 * light mode (dark box) while the section label still inherits the
 * default dark `textColor` — i.e. dark text on a dark box.
 *
 * We pin an explicit, theme-aware palette: mid-saturation backgrounds
 * that read on either page background, each paired with an explicit
 * contrasting label color via `cScaleLabel*`. `cScalePeer*` colors the
 * sub-task boxes that sit under a section.
 */
const SECTION_SCALES = {
    light: [
        { bg: '#1f6f8b', label: '#ffffff', peer: '#3a8ba6' },
        { bg: '#7b5ea7', label: '#ffffff', peer: '#977dc0' },
        { bg: '#2e8b57', label: '#ffffff', peer: '#4caf7d' },
        { bg: '#c25a3a', label: '#ffffff', peer: '#d6805f' },
        { bg: '#3a6ea5', label: '#ffffff', peer: '#5d8cc0' },
        { bg: '#a8456b', label: '#ffffff', peer: '#c06b8b' },
        { bg: '#5f8f3a', label: '#ffffff', peer: '#80aa5d' },
        { bg: '#9a7d2e', label: '#ffffff', peer: '#b89c50' },
    ],
    dark: [
        { bg: '#3aa6c9', label: '#0b1620', peer: '#2b7d99' },
        { bg: '#b39ddb', label: '#1a142b', peer: '#8a72b5' },
        { bg: '#66c990', label: '#0c1f15', peer: '#479a6b' },
        { bg: '#e8956f', label: '#2a1409', peer: '#bd6f4c' },
        { bg: '#79a8d9', label: '#0d1726', peer: '#577fad' },
        { bg: '#d987a8', label: '#2a0f1b', peer: '#ad6082' },
        { bg: '#a4cf7a', label: '#142008', peer: '#7da352' },
        { bg: '#d4bb6e', label: '#241c08', peer: '#a8924c' },
    ],
} as const;

/**
 * Build Mermaid `themeVariables` from our semantic tokens.
 *
 * Tokens are read live from the DOM so the diagram tracks light/dark
 * without a hard-coded palette. Fallbacks only fire during SSR or before
 * stylesheets load.
 */
function buildThemeVariables(theme: string, fontSize: string) {
    const isDark = theme === 'dark';
    const fg = getThemeColor('--foreground', isDark ? 'hsl(0 0% 98%)' : 'hsl(0 0% 9%)');
    const card = getThemeColor('--card', isDark ? 'hsl(0 0% 8%)' : 'hsl(0 0% 100%)');
    const muted = getThemeColor('--muted', isDark ? 'hsl(0 0% 15%)' : 'hsl(0 0% 96%)');
    const border = getThemeColor('--border', isDark ? 'hsl(0 0% 15%)' : 'hsl(0 0% 90%)');
    const primary = getThemeColor('--primary', isDark ? 'hsl(189 100% 50%)' : 'hsl(192 90% 35%)');
    const accent = getThemeColor('--accent', muted);
    const secondary = getThemeColor('--secondary', muted);
    const background = getThemeColor('--background', isDark ? 'hsl(0 0% 4%)' : 'hsl(0 0% 94%)');
    const destructive = getThemeColor('--destructive', 'hsl(0 84% 60%)');
    const destructiveFg = getThemeColor('--destructive-foreground', 'hsl(0 0% 98%)');

    const scales = SECTION_SCALES[isDark ? 'dark' : 'light'];
    // `cScale*` / `pie*` / `fillType*` are flat keys (cScale0, pie1, ...).
    //
    // `fillType*` is what the **journey** diagram actually paints its
    // section / task rects with. Left unset, Mermaid derives it by
    // rotating the hue of `cScale*` and forcing odd indexes to
    // `hsl(H, 0%, 9%)` — a near-black box. Pinning `fillType*` to our
    // explicit palette kills the dark-on-dark sections.
    const sectionVars: Record<string, string> = {};
    scales.forEach((s, i) => {
        sectionVars[`cScale${i}`] = s.bg;
        sectionVars[`cScaleLabel${i}`] = s.label;
        sectionVars[`cScaleInv${i}`] = s.label;
        sectionVars[`cScalePeer${i}`] = s.peer;
        sectionVars[`fillType${i}`] = s.bg;
        sectionVars[`surface${i}`] = s.bg;
        // Pie slices are 1-indexed and have no separate label var — the
        // slice text color is global (`pieSectionTextColor`).
        sectionVars[`pie${i + 1}`] = s.bg;
    });

    return {
        primaryColor: primary,
        primaryTextColor: fg,
        primaryBorderColor: primary,
        secondaryColor: secondary,
        secondaryTextColor: fg,
        secondaryBorderColor: border,
        tertiaryColor: accent,
        tertiaryTextColor: fg,
        tertiaryBorderColor: border,
        mainBkg: card,
        textColor: fg,
        nodeBorder: border,
        nodeTextColor: fg,
        secondBkg: muted,
        lineColor: primary,
        edgeLabelBackground: card,
        clusterBkg: muted,
        clusterBorder: primary,
        background,
        labelBackground: card,
        labelTextColor: fg,
        errorBkgColor: destructive,
        errorTextColor: destructiveFg,

        // --- ER diagram ---
        // ER attribute-row zebra fills are derived from `mainBkg` by
        // Mermaid and ignore `themeVariables` — they are re-asserted
        // post-render via `applyMermaidErRowColors`.

        // --- Section-colored diagrams (timeline / journey / mindmap) ---
        ...sectionVars,
        // Timeline / journey section title bars + the global label fallback.
        cScaleLabel0: scales[0]?.label ?? fg,
        // Journey actor faces / labels in the legend.
        actorBkg: card,
        actorBorder: border,
        actorTextColor: fg,
        actorLineColor: border,
        // Mindmap nodes inherit `cScale*`; their text uses `nodeTextColor`
        // on the outer ring — keep it readable on the page background.

        // --- Pie chart ---
        pieTitleTextColor: fg,
        pieSectionTextColor: isDark ? '#0b1620' : '#ffffff',
        pieSectionTextSize: '13px',
        pieLegendTextColor: fg,
        pieLegendTextSize: '13px',
        pieStrokeColor: background,
        pieStrokeWidth: '2px',
        pieOuterStrokeColor: border,
        pieOuterStrokeWidth: '1px',
        pieOpacity: '1',

        // --- Git graph ---
        git0: scales[0]?.bg ?? primary,
        git1: scales[1]?.bg ?? secondary,
        git2: scales[2]?.bg ?? accent,
        git3: scales[3]?.bg ?? primary,
        git4: scales[4]?.bg ?? secondary,
        git5: scales[5]?.bg ?? accent,
        git6: scales[6]?.bg ?? primary,
        git7: scales[7]?.bg ?? secondary,
        gitBranchLabel0: scales[0]?.label ?? fg,
        gitBranchLabel1: scales[1]?.label ?? fg,
        gitBranchLabel2: scales[2]?.label ?? fg,
        gitBranchLabel3: scales[3]?.label ?? fg,
        gitBranchLabel4: scales[4]?.label ?? fg,
        gitBranchLabel5: scales[5]?.label ?? fg,
        gitBranchLabel6: scales[6]?.label ?? fg,
        gitBranchLabel7: scales[7]?.label ?? fg,
        gitInv0: scales[0]?.label ?? fg,
        commitLabelColor: fg,
        commitLabelBackground: card,
        tagLabelColor: fg,
        tagLabelBackground: muted,
        tagLabelBorder: border,

        fontSize,
        fontFamily: 'Inter, system-ui, sans-serif',
    };
}

export function useMermaidRenderer({
    chart,
    theme,
    isCompact = false,
    debounceMs = 300,
}: UseMermaidRendererProps): MermaidRenderResult {
    const mermaidRef = useRef<HTMLDivElement>(null);
    const renderTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    // Monotonic token: every effect run bumps it, and an in-flight async
    // render checks it before touching the DOM. Guards against a stale
    // chart's `mermaid.render` resolving after a newer one started.
    const renderSeqRef = useRef(0);

    const [svgContent, setSvgContent] = useState<string>('');
    const [isVertical, setIsVertical] = useState(false);
    const [isRendering, setIsRendering] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { isMermaidCodeComplete } = useMermaidValidation();
    const { cleanupMermaidErrors } = useMermaidCleanup();

    useEffect(() => {
        const seq = ++renderSeqRef.current;
        const isStale = () => seq !== renderSeqRef.current;

        const fontSize = isCompact ? '12px' : '14px';

        const renderChart = async () => {
            const host = mermaidRef.current;
            if (!host || !chart) {
                setIsRendering(false);
                return;
            }

            // Streaming guard: an incomplete diagram (still being typed /
            // streamed) would throw a parse error. Keep the previous SVG
            // visible and just show the spinner — don't flash an error.
            if (!isMermaidCodeComplete(chart)) {
                setIsRendering(true);
                return;
            }

            setIsRendering(true);
            setError(null);

            // `mermaid.initialize` is global + idempotent; re-running it
            // per render keeps `themeVariables` in sync with the live
            // light/dark tokens (cheap, no library reload).
            mermaid.initialize({
                startOnLoad: false,
                theme: 'base',
                securityLevel: 'loose',
                suppressErrorRendering: true,
                fontFamily: 'Inter, system-ui, sans-serif',
                flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
                themeVariables: buildThemeVariables(theme, fontSize),
            });

            const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;

            try {
                // `mermaid.parse` validates without mutating the DOM —
                // catches syntax errors before `render` appends anything.
                await mermaid.parse(chart);
                const { svg } = await mermaid.render(id, chart);

                if (isStale() || !mermaidRef.current) return;

                const textColor = getTextColor(theme);
                const processedSvg = svg.replace(
                    /<svg /,
                    `<svg style="--mermaid-text-color: ${textColor};" `,
                );

                mermaidRef.current.innerHTML = processedSvg;
                applyMermaidTextColors(mermaidRef.current, textColor);
                // ER attribute rows zebra-stripe off `mainBkg` and ignore
                // `themeVariables` — re-assert themed, contrasting fills.
                applyMermaidErRowColors(
                    mermaidRef.current,
                    getThemeColor('--card', theme === 'dark' ? 'hsl(0 0% 8%)' : 'hsl(0 0% 100%)'),
                    getThemeColor('--muted', theme === 'dark' ? 'hsl(0 0% 15%)' : 'hsl(0 0% 96%)'),
                );

                const svgElement = mermaidRef.current.querySelector('svg');
                if (svgElement) {
                    svgElement.style.maxWidth = '100%';
                    svgElement.style.height = 'auto';
                    svgElement.style.display = 'block';
                    setIsVertical(isVerticalDiagram(svgElement));
                }

                setSvgContent(processedSvg);
                setError(null);
                setIsRendering(false);
            } catch (err) {
                // `render` may still have appended an orphan node to
                // <body> despite `suppressErrorRendering` — sweep it.
                cleanupMermaidErrors();
                if (isStale()) return;

                const message =
                    err instanceof Error ? err.message : 'Failed to render diagram';
                setError(message);
                setSvgContent('');
                setIsVertical(false);
                setIsRendering(false);
                if (mermaidRef.current) {
                    mermaidRef.current.innerHTML = '';
                }
            }
        };

        if (renderTimerRef.current) {
            clearTimeout(renderTimerRef.current);
        }
        renderTimerRef.current = setTimeout(renderChart, debounceMs);

        return () => {
            // Invalidate any in-flight async render from this effect run.
            // The counter must be bumped on the LIVE ref, not on a copy taken
            // when the effect ran — a copy would leave the stale render free to
            // overwrite the current diagram when it resolves.
            // eslint-disable-next-line react-hooks/exhaustive-deps
            renderSeqRef.current++;
            if (renderTimerRef.current) {
                clearTimeout(renderTimerRef.current);
                renderTimerRef.current = null;
            }
        };
    }, [chart, theme, isCompact, debounceMs, isMermaidCodeComplete, cleanupMermaidErrors]);

    return { mermaidRef, svgContent, isVertical, isRendering, error };
}
