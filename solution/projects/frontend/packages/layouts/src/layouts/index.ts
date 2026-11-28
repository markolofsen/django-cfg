/**
 * Layouts exports
 *
 * Simple, straightforward layout components
 * Import and use directly with props - no complex configs needed!
 */

'use client';

// Shared types (universal type system)
export * from './types';

// Shared components (used by multiple layouts)
export { LocaleSwitcher, LOCALE_LABELS } from './_components';
export type { LocaleSwitcherProps } from './_components';

// PublicLayout components (re-exported for convenience)
export { UserMenu } from './PublicLayout/components';
export type { UserMenuProps } from './PublicLayout/components';
export { UserAvatar } from './PublicLayout/components';
export type { UserAvatarProps } from './PublicLayout/components';

// Smart layout router
export * from './AppLayout';

// Basic layouts
export * from './PublicLayout';
export * from './PrivateLayout';
export * from './AuthLayout';

// Additional layouts
export * from './SettingsLayout';
