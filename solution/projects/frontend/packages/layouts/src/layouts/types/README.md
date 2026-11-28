# Shared Layout Types

Universal type system for all layouts to avoid duplication and ensure consistency.

## Overview

This module provides shared TypeScript types used across all layout components in the `@djangocfg/layouts` package.

## Available Types

### Core Configuration Types

- **`ThemeConfig`** - Theme settings (light/dark/system)
- **`AuthConfig`** - Authentication configuration
- **`ErrorTrackingConfig`** - Error tracking settings
- **`ErrorBoundaryConfig`** - Error boundary options

### Layout Component Types

- **`BaseLayoutProps`** - Base props for all layouts (includes all configs above)
- **`NavigationItem`** - Single navigation item
- **`NavigationSection`** - Group of navigation items
- **`FooterLink`** - Footer link
- **`FooterMenuSection`** - Footer menu section
- **`FooterSocialLinks`** - Social media links
- **`FooterConfig`** - Complete footer configuration

## Usage

### Import Types

```typescript
import type {
  BaseLayoutProps,
  ThemeConfig,
  FooterConfig,
} from '@djangocfg/layouts';
```

### Extend Layout Props

```typescript
import type { BaseLayoutProps } from '@djangocfg/layouts';

interface MyCustomLayoutProps extends BaseLayoutProps {
  customProp?: string;
}
```

## Benefits

1. **No Duplication** - Define types once, use everywhere
2. **Type Safety** - Full TypeScript support across all layouts
3. **Consistency** - All layouts use the same prop names and shapes
4. **Easy Maintenance** - Update types in one place
5. **Better DX** - IntelliSense shows all available options

## File Structure

```
shared/
├── types.ts        # All type definitions
├── index.ts        # Type exports
└── README.md       # This file
```
