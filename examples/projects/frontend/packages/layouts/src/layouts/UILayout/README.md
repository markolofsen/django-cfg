# UILayout - Config-Driven UI Documentation System

Modern, type-safe layout system for showcasing UI component libraries with built-in "Copy for AI" functionality.

## 🎯 Key Features

- **Config-Driven**: Single source of truth for all component documentation
- **Type-Safe**: Full TypeScript support with strict typing
- **Auto-Rendering**: Components automatically rendered from config
- **AI-Ready**: One-click export of entire documentation for AI consumption
- **Responsive**: Mobile-first design with adaptive sidebar
- **Dark Mode**: Built-in theme support
- **Organized**: Modular config structure by category

## 📁 Structure

```
UILayout/
├── config/                    # All configuration (Single Source of Truth)
│   ├── components/           # Component configs by category
│   │   ├── forms.config.tsx       # 8 form components
│   │   ├── layout.config.tsx      # 5 layout components
│   │   ├── navigation.config.tsx  # 4 navigation components
│   │   ├── overlay.config.tsx     # 11 overlay components
│   │   ├── feedback.config.tsx    # 5 feedback components
│   │   ├── data.config.tsx        # 5 data display components
│   │   ├── specialized.config.tsx # 2 specialized components
│   │   ├── blocks.config.tsx      # 7 landing page blocks
│   │   ├── hooks.config.tsx       # 6 custom hooks
│   │   └── index.ts               # Aggregates all configs
│   ├── categories.config.tsx # Category definitions
│   ├── tailwind.config.ts    # Tailwind 4 guidelines
│   ├── ai-export.config.ts   # AI context generator
│   └── index.ts              # Main config exports
├── components/               # React components
│   ├── AutoComponentDemo.tsx      # Auto-renders from config
│   ├── CategoryRenderer.tsx       # Renders entire category
│   ├── TailwindGuideRenderer.tsx  # Renders Tailwind guide
│   ├── Header.tsx                 # Header with "Copy for AI"
│   ├── Sidebar.tsx
│   └── MobileOverlay.tsx
├── context/                  # React Context
│   └── ShowcaseContext.tsx   # Navigation state management
├── UILayout.tsx              # Main layout component
├── UIGuideView.tsx           # Complete UI guide view
├── UIGuideLanding.tsx        # Landing page
└── UIGuideApp.tsx            # Full app wrapper
```

## 🚀 Quick Start

### Basic Usage

```tsx
import { UILayout, CATEGORIES } from '@djangocfg/layouts';

function MyComponentGuide() {
  const [category, setCategory] = useState('forms');

  return (
    <UILayout
      title="My Component Library"
      categories={CATEGORIES}
      currentCategory={category}
      onCategoryChange={setCategory}
    >
      {/* Your content */}
    </UILayout>
  );
}
```

### Using Category Renderer (Auto-render from config)

```tsx
import { UILayout, CATEGORIES, CategoryRenderer } from '@djangocfg/layouts';

function MyComponentGuide() {
  const [category, setCategory] = useState('forms');

  return (
    <UILayout
      title="My Component Library"
      categories={CATEGORIES}
      currentCategory={category}
      onCategoryChange={setCategory}
    >
      {/* Automatically renders all components in category */}
      <CategoryRenderer categoryId={category} />
    </UILayout>
  );
}
```

### Using Complete UI Guide

```tsx
import { UIGuideApp } from '@djangocfg/layouts';

// Complete pre-configured UI guide with all components
export default function Page() {
  return <UIGuideApp />;
}
```

## 📝 Adding New Components

### 1. Add to Config

Edit the appropriate config file in `config/components/`:

```tsx
// config/components/forms.config.tsx
export const FORM_COMPONENTS: ComponentConfig[] = [
  {
    name: 'MyComponent',
    category: 'forms',
    description: 'A custom form component',
    importPath: "import { MyComponent } from '@mylib/ui';",
    example: `<MyComponent value="test" onChange={handler} />`,
    preview: <MyComponent value="test" onChange={() => {}} />
  },
  // ... other components
];
```

### 2. That's It!

No need to:
- ❌ Create separate demo files
- ❌ Write duplicate rendering code
- ❌ Update multiple places

The component automatically:
- ✅ Appears in the UI guide
- ✅ Gets included in "Copy for AI"
- ✅ Shows in the category with proper formatting

## 🤖 Copy for AI Feature

Click the "Copy for AI" button in the header to export entire documentation including:

- ✅ Tailwind CSS v4 guidelines and best practices
- ✅ All 53 components with full examples
- ✅ Import statements
- ✅ Usage examples
- ✅ Properly formatted for AI consumption

Perfect for giving AI assistants complete context about your UI library!

## 📊 Component Statistics

| Category | Components |
|----------|------------|
| Forms | 8 |
| Layout | 5 |
| Navigation | 4 |
| Overlay | 11 |
| Feedback | 5 |
| Data Display | 5 |
| Specialized | 2 |
| Blocks | 7 |
| Hooks | 6 |
| **Total** | **53** |

## 🎨 Customization

### Custom Categories

```tsx
import type { ComponentCategory } from '@djangocfg/layouts';

const customCategories: ComponentCategory[] = [
  {
    id: 'custom',
    label: 'My Category',
    icon: <MyIcon />,
    count: 5,
    description: 'Custom component category'
  }
];
```

### Custom Config

```tsx
import type { ComponentConfig } from '@djangocfg/layouts';

const customComponents: ComponentConfig[] = [
  {
    name: 'Component',
    category: 'custom',
    description: '...',
    importPath: '...',
    example: '...',
    preview: <Component />
  }
];
```

## 🔧 API Reference

### UILayout Props

```typescript
interface UILayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  categories: ComponentCategory[];
  currentCategory?: string;
  onCategoryChange?: (categoryId: string) => void;
  logo?: ReactNode;
  projectName?: string;
}
```

### ComponentConfig Type

```typescript
interface ComponentConfig {
  name: string;           // Component name
  category: string;       // Category ID
  description: string;    // Short description
  importPath: string;     // Import statement
  example: string;        // Code example
  preview: ReactNode;     // Live preview component
}
```

### Available Exports

```typescript
// Components
export { UILayout, CategoryRenderer, AutoComponentDemo };

// Views
export { UIGuideView, UIGuideApp, UIGuideLanding };

// Config
export {
  CATEGORIES,
  COMPONENTS_CONFIG,
  generateAIContext
};

// Types
export type {
  ComponentConfig,
  ComponentCategory,
  UILayoutProps
};
```

## 🎯 Benefits

1. **Single Source of Truth**: All component data in one place
2. **Zero Duplication**: Write component config once, use everywhere
3. **Type-Safe**: Full TypeScript support prevents errors
4. **Auto-Update**: Add to config, automatically appears everywhere
5. **AI-Friendly**: Built-in export for AI assistants
6. **Maintainable**: Easy to update and extend
7. **Scalable**: Add categories and components effortlessly

## 📖 More Info

See the main package README for complete documentation and examples.
