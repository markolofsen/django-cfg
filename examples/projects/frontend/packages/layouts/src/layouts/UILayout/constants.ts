/**
 * Constants for UILayout
 */

export const MOBILE_BREAKPOINT = 768; // px
export const SIDEBAR_WIDTH = 256; // px (w-64)
export const HEADER_HEIGHT = 56; // px (h-14)

export const ANIMATION_DURATION = {
  fast: 150,
  normal: 300,
  slow: 500,
} as const;

export const Z_INDEX = {
  sidebar: 30,
  overlay: 20,
  header: 40,
  dropdown: 50,
} as const;

export const DEFAULT_PROJECT_NAME = 'Django CFG UI';
export const DEFAULT_DESCRIPTION = 'Explore our comprehensive collection of 56+ React components built with Radix UI and Tailwind CSS';
