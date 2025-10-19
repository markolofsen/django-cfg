/**
 * Components Configuration Index
 * Aggregates all component configs from separate files
 */

export type { ComponentConfig } from './types';
export { FORM_COMPONENTS } from './forms.config';
export { LAYOUT_COMPONENTS } from './layout.config';
export { NAVIGATION_COMPONENTS } from './navigation.config';
export { OVERLAY_COMPONENTS } from './overlay.config';
export { FEEDBACK_COMPONENTS } from './feedback.config';
export { DATA_COMPONENTS } from './data.config';
export { SPECIALIZED_COMPONENTS } from './specialized.config';
export { BLOCKS } from './blocks.config';
export { HOOKS } from './hooks.config';

import { FORM_COMPONENTS } from './forms.config';
import { LAYOUT_COMPONENTS } from './layout.config';
import { NAVIGATION_COMPONENTS } from './navigation.config';
import { OVERLAY_COMPONENTS } from './overlay.config';
import { FEEDBACK_COMPONENTS } from './feedback.config';
import { DATA_COMPONENTS } from './data.config';
import { SPECIALIZED_COMPONENTS } from './specialized.config';
import { BLOCKS } from './blocks.config';
import { HOOKS } from './hooks.config';
import type { ComponentConfig } from './types';

/**
 * All components aggregated from category configs
 */
export const COMPONENTS_CONFIG: ComponentConfig[] = [
  ...FORM_COMPONENTS,
  ...LAYOUT_COMPONENTS,
  ...NAVIGATION_COMPONENTS,
  ...OVERLAY_COMPONENTS,
  ...FEEDBACK_COMPONENTS,
  ...DATA_COMPONENTS,
  ...SPECIALIZED_COMPONENTS,
  ...BLOCKS,
  ...HOOKS,
];

/**
 * Get components by category
 */
export function getComponentsByCategory(category: string): ComponentConfig[] {
  return COMPONENTS_CONFIG.filter(comp => comp.category === category);
}

/**
 * Get component by name
 */
export function getComponentByName(name: string): ComponentConfig | undefined {
  return COMPONENTS_CONFIG.find(comp => comp.name === name);
}

/**
 * Get all categories
 */
export function getAllCategories(): string[] {
  return [...new Set(COMPONENTS_CONFIG.map(comp => comp.category))];
}

/**
 * Get component count by category
 */
export function getComponentCount(category: string): number {
  return COMPONENTS_CONFIG.filter(comp => comp.category === category).length;
}
