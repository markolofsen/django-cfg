/**
 * Type definitions for OG Image Handler
 */

import { ReactElement } from 'react';

/**
 * Font configuration for OG image
 */
export interface OgImageFont {
  /** Font family name */
  name: string;
  /** Font file data as ArrayBuffer */
  data: ArrayBuffer;
  /** Font weight (default: 400) */
  weight?: 400 | 500 | 600 | 700 | 800 | 900;
  /** Font style (default: 'normal') */
  style?: 'normal' | 'italic';
}

/**
 * OG Image dimensions
 */
export interface OgImageSize {
  /** Image width in pixels (default: 1200) */
  width?: number;
  /** Image height in pixels (default: 630) */
  height?: number;
}

/**
 * Template props passed to the OG image template component
 */
export interface OgImageTemplateProps {
  /** Page title */
  title: string;
  /** Page description (optional) */
  description?: string;
  /** Site name (optional) */
  siteName?: string;
  /** Logo URL or data URI (optional) */
  logo?: string;
  /** Additional query params from URL */
  [key: string]: any;
}

/**
 * Template renderer function type
 */
export type OgImageTemplate = (props: OgImageTemplateProps) => ReactElement;

/**
 * Handler configuration options
 */
export interface OgImageHandlerConfig {
  /**
   * Template component or render function
   * Can be a React component or a function that returns JSX
   */
  template: OgImageTemplate;

  /**
   * Fonts to load for the image
   * Can be a function that returns a Promise for dynamic loading
   */
  fonts?: OgImageFont[] | (() => Promise<OgImageFont[]>);

  /**
   * Image dimensions
   */
  size?: OgImageSize;

  /**
   * Debug mode (logs template props)
   */
  debug?: boolean;

  /**
   * Default values for template props
   */
  defaults?: Partial<OgImageTemplateProps>;
}

/**
 * Next.js API Request with query params
 */
export interface OgImageRequest {
  url?: string;
  nextUrl?: {
    searchParams: URLSearchParams;
  };
}
