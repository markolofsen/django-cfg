/**
 * Enhanced Image with Fallback Component
 * 
 * Advanced image component with loading states, error handling, and customizable fallbacks
 */

import React, { forwardRef } from 'react';
import { Car, ImageIcon, User, Package, MapPin } from 'lucide-react';
import { cn } from '../lib/utils';
import { useImageLoader } from '../hooks/useImageLoader';

export interface ImageWithFallbackProps extends Omit<React.ImgHTMLAttributes<HTMLImageElement>, 'onLoad' | 'onError'> {
  src?: string;
  alt?: string;
  className?: string;
  
  // Fallback options
  fallbackIcon?: 'car' | 'image' | 'user' | 'package' | 'location';
  fallbackContent?: React.ReactNode;
  showLoadingState?: boolean;
  
  // Loading placeholder
  placeholder?: string;
  blurDataURL?: string;
  
  // Callbacks
  onLoad?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
  onError?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
  onLoadStart?: () => void;
  
  // Performance
  priority?: boolean;
  unoptimized?: boolean;
}

export const ImageWithFallback = forwardRef<HTMLImageElement, ImageWithFallbackProps>(({
  src,
  alt = '',
  className,
  
  // Fallback options
  fallbackIcon = 'car',
  fallbackContent,
  showLoadingState = true,
  
  // Loading placeholder
  placeholder,
  blurDataURL,
  
  // Callbacks
  onLoad,
  onError,
  onLoadStart,
  
  // Performance
  priority = false,
  unoptimized = false,
  
  // Standard img attributes
  width,
  height,
  sizes,
  loading = priority ? 'eager' : 'lazy',
  decoding = 'async',
  ...imgProps
}, ref) => {
  const { isLoading, isLoaded, hasError } = useImageLoader(src, {
    onLoadStart,
    onLoad,
    onError,
  });

  // Get fallback icon
  const getFallbackIcon = () => {
    switch (fallbackIcon) {
      case 'car': return Car;
      case 'user': return User;
      case 'package': return Package;
      case 'location': return MapPin;
      case 'image':
      default: return ImageIcon;
    }
  };

  const FallbackIcon = getFallbackIcon();

  // Custom fallback content
  if (hasError || !src) {
    if (fallbackContent) {
      return (
        <div className={cn('flex items-center justify-center', className)}>
          {fallbackContent}
        </div>
      );
    }

    return (
      <div
        className={cn(
          'flex items-center justify-center bg-muted/30 text-muted-foreground/50',
          'transition-colors duration-200',
          className
        )}
      >
        <FallbackIcon className="h-8 w-8" />
      </div>
    );
  }

  // Loading state
  if (isLoading && showLoadingState) {
    return (
      <div className={cn('relative overflow-hidden', className)}>
        {/* Blur placeholder if available */}
        {(placeholder || blurDataURL) && (
          <img
            src={placeholder || blurDataURL}
            alt=""
            className="absolute inset-0 w-full h-full object-cover blur-sm scale-110"
            aria-hidden="true"
          />
        )}
        
        {/* Loading overlay */}
        <div className={cn(
          'absolute inset-0 flex items-center justify-center',
          'bg-muted/20 text-muted-foreground/30 animate-pulse',
          'backdrop-blur-sm'
        )}>
          <FallbackIcon className="h-6 w-6" />
        </div>
      </div>
    );
  }

  // Successfully loaded image
  if (isLoaded) {
    return (
      <img
        ref={ref}
        src={src}
        alt={alt}
        width={width}
        height={height}
        sizes={sizes}
        loading={loading}
        decoding={decoding}
        className={cn('object-cover transition-opacity duration-300', className)}
        onLoad={onLoad}
        onError={onError}
        {...imgProps}
      />
    );
  }

  // Initial render fallback
  return (
    <div
      className={cn(
        'flex items-center justify-center bg-muted/20 text-muted-foreground/30',
        'transition-colors duration-200',
        className
      )}
    >
      <FallbackIcon className="h-6 w-6" />
    </div>
  );
});

ImageWithFallback.displayName = 'ImageWithFallback';
