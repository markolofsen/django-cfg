"use client"

import * as React from 'react';
import StickyBox from 'react-sticky-box';

import { useIsMobile } from '../hooks/useMobile';

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
      zIndex: 10,
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
  return (
    <StickyBox
      bottom={bottom}
      offsetTop={offsetTop}
      offsetBottom={offsetBottom}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </StickyBox>
  );
};

Sticky.displayName = "Sticky";

export { Sticky };
