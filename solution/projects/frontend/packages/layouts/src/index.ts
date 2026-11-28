/**
 * @djangocfg/layouts
 * 
 * Simple, straightforward layout components for Next.js
 * Import and use directly with props - no complex configs needed!
 * 
 * @example
 * ```tsx
 * import { PublicLayout, PublicNavbar, PrivateLayout, AuthLayout } from '@djangocfg/layouts';
 * 
 * // Public page
 * <PublicLayout
 *   navbar={<PublicNavbar config={{ brand: "My App", navigation: navItems, shell: { className: 'mx-auto max-w-7xl' } }} />}
 * >
 *   {children}
 * </PublicLayout>
 * 
 * // Private page
 * <PrivateLayout sidebar={{ items: menuItems }} header={{ title: 'Dashboard' }}>
 *   {children}
 * </PrivateLayout>
 * 
 * // Auth page
 * <AuthLayout logo="/logo.svg" title="Sign In">
 *   <LoginForm />
 * </AuthLayout>
 * ```
 */

'use client';

// Layout components
export * from './layouts';

// Typed theme style bridge + presets (BaseApp `theme.style`)
export * from './theme';

// Snippets - Reusable UI components (includes Analytics)
export * from './snippets';

// Components (includes ErrorTrackingProvider)
export * from './components';

// Utils
export * from './utils';

// Hooks
export * from './hooks';

// Pages
export * from './pages';
