/**
 * Shared types for all select-based components
 */

import type { ReactNode } from 'react';

/**
 * Base option interface for all select components
 */
export interface BaseSelectOption {
  /** Unique value */
  value: string;
  /** Display label */
  label: string;
  /** Optional description/subtitle */
  description?: string;
  /** Optional icon component */
  icon?: React.ComponentType<{ className?: string }>;
  /** Optional badge text */
  badge?: string | ReactNode;
  /** Whether this option is disabled */
  disabled?: boolean;
  /** Custom styling for badge/icon */
  style?: {
    badgeColor?: string;
    iconColor?: string;
    gradient?: string;
  };
}

/**
 * Group of options with heading
 */
export interface SelectOptionGroup {
  heading: string;
  options: BaseSelectOption[];
}

/**
 * Style configuration for badge
 */
export interface BadgeStyle {
  badgeColor?: string;
  iconColor?: string;
  gradient?: string;
}

/**
 * Animation configuration for select components
 */
export interface SelectAnimationConfig {
  badgeAnimation?: 'bounce' | 'pulse' | 'wiggle' | 'fade' | 'slide' | 'none';
  popoverAnimation?: 'scale' | 'slide' | 'fade' | 'flip' | 'none';
  optionHoverAnimation?: 'highlight' | 'scale' | 'glow' | 'none';
  duration?: number;
  delay?: number;
}
