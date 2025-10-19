/**
 * UILayout Module Exports
 * Config-driven UI documentation layout
 */

// Main Layout Component
export { UILayout, ComponentShowcaseLayout } from './UILayout';
export type { UILayoutProps, ComponentShowcaseLayoutProps } from './UILayout';

// Context for navigation management
export { ShowcaseProvider, useShowcase } from './context';

// UI Guide View (specific implementation for Django CFG UI)
export { default as UIGuideView } from './UIGuideView';
export { UIGuideLanding } from './UIGuideLanding';
export { UIGuideApp } from './UIGuideApp';

// Components
export { AutoComponentDemo, CategorySection } from './components/AutoComponentDemo';
export { CategoryRenderer } from './components/CategoryRenderer';
export { TailwindGuideRenderer } from './components/TailwindGuideRenderer';
export { Sidebar } from './components/Sidebar';
export { Header } from './components/Header';
export { MobileOverlay } from './components/MobileOverlay';

// Configuration (Single Source of Truth)
export {
  // All components
  COMPONENTS_CONFIG,
  FORM_COMPONENTS,
  LAYOUT_COMPONENTS,
  NAVIGATION_COMPONENTS,
  OVERLAY_COMPONENTS,
  FEEDBACK_COMPONENTS,
  DATA_COMPONENTS,
  SPECIALIZED_COMPONENTS,
  BLOCKS,
  HOOKS,
  // Utility functions
  getComponentsByCategory,
  getComponentByName,
  getAllCategories,
  getComponentCount,
  // Categories
  CATEGORIES,
  getCategoryById,
  getTotalComponentCount,
  // Tailwind
  TAILWIND_GUIDE,
  // AI Export
  UI_LIBRARY_CONFIG,
  generateAIContext,
} from './config';

// Types
export type {
  ComponentConfig,
  ComponentCategory,
  TailwindGuide,
  UILibraryConfig,
} from './config';

// Constants
export * from './constants';
