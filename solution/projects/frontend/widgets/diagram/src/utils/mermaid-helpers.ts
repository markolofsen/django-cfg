/**
 * Helper utilities for Mermaid diagram rendering
 */

/**
 * Read a semantic color token from CSS custom properties.
 *
 * Theme tokens (`light.css` / `dark.css`) ship fully-wrapped CSS colors
 * (`hsl(0 0% 94%)`) — see `ui-core/src/styles/theme/tokens.css`. Older
 * tokens stored bare HSL components (`0 0% 94%`), so this helper handles
 * both: complete colors pass through untouched, bare components get
 * wrapped once. Never double-wrap an already-complete color.
 *
 * @param variable CSS custom property name, e.g. `--foreground`.
 * @param fallback Returned when the variable is empty / unavailable.
 */
export const getThemeColor = (variable: string, fallback = ''): string => {
    if (typeof document === 'undefined') return fallback;
    const value = getComputedStyle(document.documentElement)
        .getPropertyValue(variable)
        .trim();
    if (!value) return fallback;
    // Already a complete color (hex / rgb / hsl / oklch / named).
    if (
        value.startsWith('#') ||
        value.startsWith('rgb') ||
        value.startsWith('hsl(') ||
        value.startsWith('oklch') ||
        value.startsWith('oklab') ||
        value.startsWith('color(') ||
        value.startsWith('var(')
    ) {
        return value;
    }
    // Bare HSL components — wrap once.
    return `hsl(${value})`;
};

/** Resolve the diagram text color for the given theme. */
export const getTextColor = (theme: string): string =>
    theme === 'dark'
        ? getThemeColor('--foreground', 'hsl(0 0% 98%)')
        : getThemeColor('--foreground', 'hsl(222.2 84% 4.9%)');

/**
 * Diagram types whose labels sit on per-section colored backgrounds
 * (timeline sections, journey tasks, pie slices, mindmap nodes, gitgraph
 * commits). For these, Mermaid already picks a contrasting label color
 * from the `cScaleLabel*` / `pie*` theme variables — re-asserting a single
 * `--foreground` would put dark text on dark boxes (and vice versa).
 *
 * We detect them via the wrapper class Mermaid puts on the root `<g>` /
 * `<svg>` and skip the blanket text override for those SVGs.
 */
const SECTION_COLORED_SELECTORS = [
    '.timeline',
    '.mindmap',
    '[id^="mermaid"][aria-roledescription="timeline"]',
    '[id^="mermaid"][aria-roledescription="journey"]',
    '[id^="mermaid"][aria-roledescription="mindmap"]',
    '[id^="mermaid"][aria-roledescription="pie"]',
];

/** True when the SVG renders a diagram type that colors its own labels. */
const usesSectionColors = (svg: SVGSVGElement): boolean => {
    const role = svg.getAttribute('aria-roledescription') ?? '';
    if (['timeline', 'journey', 'mindmap', 'pie'].includes(role)) return true;
    return SECTION_COLORED_SELECTORS.some((sel) => svg.querySelector(sel) !== null);
};

/**
 * Apply theme text colors to a rendered Mermaid SVG.
 *
 * Mermaid's `base` theme bakes `themeVariables` at render time, but text
 * fill on `<text>` nodes and `color` on foreignObject labels can drift
 * from our tokens — this re-asserts them after render.
 *
 * Diagrams that color their own labels per section (timeline, journey,
 * mindmap, pie) are skipped: their `themeVariables` already encode
 * contrasting label colors, so a blanket override would re-introduce the
 * dark-text-on-dark-box problem.
 */
export const applyMermaidTextColors = (container: HTMLElement, textColor: string): void => {
    const svgElement = container.querySelector('svg');
    if (!svgElement) return;
    if (usesSectionColors(svgElement)) return;
    // SVG text elements use 'fill'.
    svgElement.querySelectorAll('text').forEach((el) => {
        (el as SVGElement).style.fill = textColor;
    });
    // HTML elements inside foreignObject use 'color'.
    svgElement.querySelectorAll('.nodeLabel, .edgeLabel').forEach((el) => {
        (el as HTMLElement).style.color = textColor;
    });
};

/**
 * Re-color ER diagram attribute-row backgrounds.
 *
 * Mermaid derives the zebra-stripe fills for `.row-rect-odd` /
 * `.row-rect-even` by lightening `mainBkg` — in dark mode the odd stripe
 * lands on a light gray (`hsl(0 0% 83%)`) while the attribute text stays
 * white, so it vanishes. `themeVariables` has no hook for these, so we
 * re-assert themed fills after render.
 *
 * @param container Host element holding the rendered SVG.
 * @param oddFill   Background for odd attribute rows.
 * @param evenFill  Background for even attribute rows.
 */
export const applyMermaidErRowColors = (
    container: HTMLElement,
    oddFill: string,
    evenFill: string,
): void => {
    const svgElement = container.querySelector('svg');
    if (!svgElement) return;
    svgElement.querySelectorAll('.row-rect-odd path').forEach((el) => {
        const fill = (el as SVGElement).getAttribute('fill');
        if (fill && fill !== 'none') (el as SVGElement).setAttribute('fill', oddFill);
    });
    svgElement.querySelectorAll('.row-rect-even path').forEach((el) => {
        const fill = (el as SVGElement).getAttribute('fill');
        if (fill && fill !== 'none') (el as SVGElement).setAttribute('fill', evenFill);
    });
};

/**
 * Detect whether a diagram is vertical (tall and narrow).
 *
 * Used to pick a sensible fullscreen fit. Prefers the `viewBox` (stable,
 * available immediately) and falls back to `getBBox()` only when needed.
 */
export const isVerticalDiagram = (svgElement: SVGSVGElement): boolean => {
    const viewBox = svgElement.getAttribute('viewBox');
    if (viewBox) {
        const [, , width, height] = viewBox.split(/\s+/).map(Number);
        if (
            width === undefined ||
            height === undefined ||
            !Number.isFinite(width) ||
            !Number.isFinite(height) ||
            width <= 0
        ) {
            return false;
        }
        return height > width * 1.5;
    }
    try {
        const bbox = svgElement.getBBox?.();
        if (bbox && bbox.width > 0) {
            return bbox.height > bbox.width * 1.5;
        }
    } catch {
        // getBBox throws if the SVG is not attached / not rendered.
    }
    return false;
};
