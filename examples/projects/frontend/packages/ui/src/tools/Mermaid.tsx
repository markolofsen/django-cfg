import mermaid from 'mermaid';
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useTheme } from '../hooks/useTheme';

interface MermaidProps {
    chart: string;
    className?: string;
}

// Utility function to apply text colors to Mermaid SVG
const applyMermaidTextColors = (container: HTMLElement, textColor: string) => {
    const svgElement = container.querySelector('svg');
    if (svgElement) {
        // SVG text elements use 'fill'
        svgElement.querySelectorAll('text').forEach((el) => {
            (el as SVGElement).style.fill = textColor;
        });

        // HTML elements inside foreignObject use 'color'
        svgElement.querySelectorAll('.nodeLabel, .edgeLabel').forEach((el) => {
            (el as HTMLElement).style.color = textColor;
        });
    }
};

const Mermaid: React.FC<MermaidProps> = ({ chart, className = '' }) => {
    const mermaidRef = useRef<HTMLDivElement>(null);
    const fullscreenRef = useRef<HTMLDivElement>(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [svgContent, setSvgContent] = useState<string>('');
    const theme = useTheme();

    useEffect(() => {
        // Get CSS variables for semantic colors
        const getCSSVariable = (variable: string) => {
            if (typeof document === 'undefined') return '';
            const value = getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
            return value ? `hsl(${value})` : '';
        };

        // Force re-initialization by clearing mermaid state
        // @ts-ignore - accessing internal mermaid state
        if (mermaid.mermaidAPI) {
            // @ts-ignore
            mermaid.mermaidAPI.reset();
        }

        const themeVariables = theme === 'dark' ? {
                // Dark theme - vibrant and clear
                primaryColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',
                primaryTextColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',
                primaryBorderColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',

                secondaryColor: getCSSVariable('--muted') || 'hsl(217.2 32.6% 17.5%)',
                secondaryTextColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',
                secondaryBorderColor: getCSSVariable('--border') || 'hsl(217.2 32.6% 27.5%)',

                tertiaryColor: getCSSVariable('--accent') || 'hsl(217.2 32.6% 20%)',
                tertiaryTextColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',
                tertiaryBorderColor: getCSSVariable('--border') || 'hsl(217.2 32.6% 27.5%)',

                // Main elements - darker with good contrast
                mainBkg: getCSSVariable('--card') || 'hsl(222.2 84% 8%)',
                textColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',
                nodeBorder: getCSSVariable('--border') || 'hsl(217.2 32.6% 27.5%)',
                nodeTextColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',

                // Alternative backgrounds
                secondBkg: getCSSVariable('--muted') || 'hsl(217.2 32.6% 17.5%)',

                // Lines and edges - lighter for visibility
                lineColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',
                edgeLabelBackground: getCSSVariable('--card') || 'hsl(222.2 84% 8%)',

                // Clusters
                clusterBkg: getCSSVariable('--muted') || 'hsl(217.2 32.6% 12%)',
                clusterBorder: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',

                // Background
                background: getCSSVariable('--background') || 'hsl(222.2 84% 4.9%)',

                // Labels
                labelBackground: getCSSVariable('--card') || 'hsl(222.2 84% 8%)',
                labelTextColor: getCSSVariable('--foreground') || 'hsl(210 40% 98%)',

                // Special states
                errorBkgColor: getCSSVariable('--destructive') || 'hsl(0 62.8% 30.6%)',
                errorTextColor: 'hsl(210 40% 98%)',

                fontSize: '14px',
                fontFamily: 'Inter, system-ui, sans-serif',
            } : {
                // Light theme - clean and professional
                primaryColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',
                primaryTextColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',
                primaryBorderColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',

                secondaryColor: getCSSVariable('--secondary') || 'hsl(210 40% 96.1%)',
                secondaryTextColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',
                secondaryBorderColor: getCSSVariable('--border') || 'hsl(214.3 31.8% 91.4%)',

                tertiaryColor: getCSSVariable('--muted') || 'hsl(210 40% 96.1%)',
                tertiaryTextColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',
                tertiaryBorderColor: getCSSVariable('--border') || 'hsl(214.3 31.8% 91.4%)',

                // Main elements - white with good contrast
                mainBkg: getCSSVariable('--card') || 'hsl(0 0% 100%)',
                textColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',
                nodeBorder: getCSSVariable('--border') || 'hsl(214.3 31.8% 91.4%)',
                nodeTextColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',

                // Alternative backgrounds
                secondBkg: getCSSVariable('--muted') || 'hsl(210 40% 96.1%)',

                // Lines and edges - vibrant primary color
                lineColor: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',
                edgeLabelBackground: getCSSVariable('--card') || 'hsl(0 0% 100%)',

                // Clusters - subtle background
                clusterBkg: getCSSVariable('--accent') || 'hsl(210 40% 98%)',
                clusterBorder: getCSSVariable('--primary') || 'hsl(221.2 83.2% 53.3%)',

                // Background
                background: getCSSVariable('--background') || 'hsl(0 0% 100%)',

                // Labels
                labelBackground: getCSSVariable('--card') || 'hsl(0 0% 100%)',
                labelTextColor: getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)',

                // Special states
                errorBkgColor: getCSSVariable('--destructive') || 'hsl(0 84.2% 60.2%)',
                errorTextColor: 'hsl(210 40% 98%)',

                fontSize: '14px',
                fontFamily: 'Inter, system-ui, sans-serif',
            };

        console.log('[Mermaid] Theme:', theme, 'Variables:', themeVariables);

        // Initialize mermaid with dynamic theme configuration
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base', // Use 'base' theme for better custom variable support
            securityLevel: 'loose',
            fontFamily: 'Inter, system-ui, sans-serif',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
            },
            themeVariables,
        });

        // Render the chart
        if (mermaidRef.current && chart) {
            mermaid.render(`mermaid-${Date.now()}`, chart).then(({ svg }) => {
                if (mermaidRef.current) {
                    // Post-process SVG to force correct text colors
                    const textColor = theme === 'dark'
                        ? getCSSVariable('--foreground') || 'hsl(0 0% 90%)'
                        : getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)';

                    // Add inline style to override any conflicting styles
                    const processedSvg = svg.replace(
                        /<svg /,
                        `<svg style="--mermaid-text-color: ${textColor};" `
                    );

                    mermaidRef.current.innerHTML = processedSvg;
                    setSvgContent(processedSvg);

                    // Apply text colors and responsive styles using utility function
                    applyMermaidTextColors(mermaidRef.current, textColor);

                    // Make inline SVG responsive
                    const svgElement = mermaidRef.current.querySelector('svg');
                    if (svgElement) {
                        svgElement.style.maxWidth = '100%';
                        svgElement.style.height = 'auto';
                        svgElement.style.display = 'block';
                    }
                }
            }).catch((error) => {
                console.error('Mermaid rendering error:', error);
                if (mermaidRef.current) {
                    mermaidRef.current.innerHTML = `
            <div class="p-4 text-destructive bg-destructive/10 border border-destructive/20 rounded-sm">
              <p class="font-semibold">Mermaid Diagram Error</p>
              <p class="text-sm">${error.message}</p>
            </div>
          `;
                }
            });
        }
    }, [chart, theme]);

    const handleClick = () => {
        if (svgContent) {
            setIsFullscreen(true);
        }
    };

    const handleClose = () => {
        setIsFullscreen(false);
    };

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            handleClose();
        }
    };

    // Handle ESC key
    useEffect(() => {
        const handleEscKey = (event: KeyboardEvent) => {
            if (event.key === 'Escape' && isFullscreen) {
                handleClose();
            }
        };

        if (isFullscreen) {
            document.addEventListener('keydown', handleEscKey);
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        }

        return () => {
            document.removeEventListener('keydown', handleEscKey);
            document.body.style.overflow = 'unset';
        };
    }, [isFullscreen]);

    // Apply text colors and responsive styles to fullscreen modal after render
    useEffect(() => {
        if (isFullscreen && fullscreenRef.current) {
            const getCSSVariable = (variable: string) => {
                if (typeof document === 'undefined') return '';
                const value = getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
                return value ? `hsl(${value})` : '';
            };

            const textColor = theme === 'dark'
                ? getCSSVariable('--foreground') || 'hsl(0 0% 90%)'
                : getCSSVariable('--foreground') || 'hsl(222.2 84% 4.9%)';

            applyMermaidTextColors(fullscreenRef.current, textColor);

            // Make SVG responsive
            const svgElement = fullscreenRef.current.querySelector('svg');
            if (svgElement) {
                svgElement.style.maxWidth = '100%';
                svgElement.style.height = 'auto';
                svgElement.style.display = 'block';
            }
        }
    }, [isFullscreen, theme]);

    return (
        <>
            <div
                className={`relative bg-card rounded-sm border border-border overflow-hidden cursor-pointer hover:shadow-sm transition-shadow ${className}`}
                onClick={handleClick}
            >
                <div className="p-4 border-b border-border bg-muted/50">
                    <h6 className="text-sm font-semibold text-foreground">Diagram</h6>
                    <p className="text-xs text-muted-foreground mt-1">Click to view fullscreen</p>
                </div>
                <div className="p-4">
                    <div
                        ref={mermaidRef}
                        className="flex justify-center items-center min-h-[200px]"
                    />
                </div>
            </div>

            {/* Fullscreen Modal - rendered in portal */}
            {isFullscreen && typeof document !== 'undefined' && createPortal(
                <div
                    className="fixed inset-0 z-[9999] bg-black/75 flex items-center justify-center p-4"
                    onClick={handleBackdropClick}
                >
                    <div className="relative bg-card rounded-sm shadow-xl max-w-[95vw] max-h-[95vh] w-full h-full flex flex-col border border-border">
                        {/* Header */}
                        <div className="flex items-center justify-between py-4 px-6 border-b border-border">
                            <h3 className="text-sm font-medium text-foreground py-0 my-0">Diagram</h3>
                            <button
                                onClick={handleClose}
                                className="text-muted-foreground hover:text-foreground transition-colors"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        {/* Content with scroll */}
                        <div className="flex-1 overflow-auto p-6">
                            <div
                                ref={fullscreenRef}
                                className="w-full min-h-full flex items-start justify-center"
                                dangerouslySetInnerHTML={{ __html: svgContent }}
                            />
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </>
    );
};

export default Mermaid; 