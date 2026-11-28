"use client"

/*
 * Sticky Component - react-sticky-box wrapper
 *
 * COMMON ISSUES & SOLUTIONS:
 *
 * 1. STICKY NOT WORKING
 *    Required structure:
 *    - Outer div: h-full overflow-y-auto (scrollable container)
 *    - Inner div: flex items-start min-h-full (flex container)
 *    - Main content: flex-1
 *    - Sticky: direct child of flex container
 *
 * 2. PAGE DOESN'T SCROLL
 *    Add "h-full overflow-y-auto" to outer container.
 *    Scrollable container must have defined height.
 *
 * 3. INSIDE ResizablePanel
 *    ResizablePanel has overflow-hidden. Add scrollable wrapper inside:
 *    <ResizablePanel>
 *      <div className="h-full overflow-y-auto">...</div>
 *    </ResizablePanel>
 *
 * 4. FLEX CONTAINER REQUIREMENTS
 *    - Use items-start (NOT items-stretch)
 *    - Sticky must be direct child of flex container
 *    - Main content should be flex-1
 *
 * 5. useNativeSticky vs react-sticky-box
 *    - useNativeSticky: CSS position:sticky, simpler but limited
 *    - Default: react-sticky-box, better for sidebars, handles tall content
 */

import * as React from 'react';
import StickyBox from 'react-sticky-box';

import { useIsMobile } from '../../../hooks';

export interface StickyProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Stick to bottom instead of top */
  bottom?: boolean;
  /** Top offset in pixels */
  offsetTop?: number;
  /** Bottom offset in pixels */
  offsetBottom?: number;
  /** Disable sticking */
  disabled?: boolean;
  /** Disable sticky on mobile devices (default: true) */
  disableOnMobile?: boolean;
  /** Use native CSS sticky instead of react-sticky-box */
  useNativeSticky?: boolean;
  /** Enable debug logging (default: false) */
  debug?: boolean;
  /** Z-index value (default: 10) */
  zIndex?: number;
}

const Sticky: React.FC<StickyProps> = ({
  className,
  bottom = false,
  offsetTop = 0,
  offsetBottom = 0,
  disabled = false,
  disableOnMobile = true,
  useNativeSticky = false,
  debug = false,
  zIndex = 10,
  children,
  style,
  ...props
}) => {
  const isMobile = useIsMobile();
  
  // Automatically disable sticky on mobile if disableOnMobile is true
  const isDisabled = disabled || (disableOnMobile && isMobile);
  
  // Debug logging (only when debug is enabled)
  React.useEffect(() => {
    if (debug) {
      console.log('Sticky Debug:', {
        isMobile,
        disabled,
        disableOnMobile,
        isDisabled,
        offsetTop,
        offsetBottom,
        useNativeSticky
      });
      
      if (!useNativeSticky) {
        console.warn('⚠️ Make sure the parent container has position: relative for react-sticky-box to work properly');
      }
    }
  }, [debug, isMobile, disabled, disableOnMobile, isDisabled, offsetTop, offsetBottom, useNativeSticky]);
  
  // If disabled, render as regular div
  if (isDisabled) {
    return (
      <div className={className} style={style} {...props}>
        {children}
      </div>
    );
  }

  // Use native CSS sticky
  if (useNativeSticky) {
    const nativeStickyStyle: React.CSSProperties = {
      position: 'sticky',
      top: bottom ? 'auto' : `${offsetTop}px`,
      bottom: bottom ? `${offsetBottom}px` : 'auto',
      zIndex,
      ...style,
    };

    return (
      <div
        className={className}
        style={nativeStickyStyle}
        {...props}
      >
        {children}
      </div>
    );
  }

  // Use react-sticky-box
  const stickyBoxStyle: React.CSSProperties = {
    zIndex,
    ...style,
  };

  return (
    <StickyBox
      bottom={bottom}
      offsetTop={offsetTop}
      offsetBottom={offsetBottom}
      className={className}
      style={stickyBoxStyle}
      {...props}
    >
      {children}
    </StickyBox>
  );
};

Sticky.displayName = "Sticky";

export { Sticky };
