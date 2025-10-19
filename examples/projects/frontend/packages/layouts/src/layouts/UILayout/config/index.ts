/**
 * Configuration Module Exports
 * Single source of truth for all UI documentation
 */

// Components configuration
export {
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
  getComponentsByCategory,
  getComponentByName,
  getAllCategories,
  getComponentCount,
} from './components';
export type { ComponentConfig } from './components';

// Categories configuration
export {
  CATEGORIES,
  getCategoryById,
  getTotalComponentCount,
} from './categories.config';
export type { ComponentCategory } from './categories.config';

// Tailwind configuration
export { TAILWIND_GUIDE } from './tailwind.config';
export type { TailwindGuide } from './tailwind.config';

// AI Export configuration
export {
  UI_LIBRARY_CONFIG,
  generateAIContext,
} from './ai-export.config';
export type { UILibraryConfig } from './ai-export.config';
