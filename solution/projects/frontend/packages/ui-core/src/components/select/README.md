# Select Components

Unified collection of all select-based components with consistent API supporting **icons** and **badges**.

## Structure

```
components/select/
├── index.ts           # Re-exports everything
├── select.tsx         # Radix UI primitives (enhanced)
├── combobox.tsx       # Searchable single-select
├── multi-select.tsx   # Simple multi-select
├── multi-select-pro/  # Advanced multi-select
│   ├── index.tsx      # MultiSelectPro
│   ├── async.tsx      # Async version
│   └── helpers.tsx    # Option builders
└── types.ts           # Shared types
```

## Components

### 1. Select (Radix Primitives)

Low-level primitives with icon and badge support.

> **Empty-string values are allowed.** Radix forbids `<Select.Item value="" />` (it reserves `''` for "cleared selection"). Our `Select` wrapper substitutes a sentinel (`'__empty__'`) internally for both the controlled value and item values, so consumers can use `''` as a normal enum value (e.g. for "none"). The sentinel never leaks into `onValueChange` — it's an implementation detail.

```tsx
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@djangocfg/ui-core';

// With icon in trigger
<Select>
  <SelectTrigger icon={MailIcon}>
    <SelectValue placeholder="Select email" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="work" icon={BriefcaseIcon} badge="Work">
      john@company.com
    </SelectItem>
    <SelectItem value="personal" icon={HomeIcon}>
      john@gmail.com
    </SelectItem>
  </SelectContent>
</Select>
```

### 2. Combobox

Searchable single-select with icon and badge support.

```tsx
import { Combobox } from '@djangocfg/ui-core';

// Basic usage
<Combobox
  options={[
    { 
      value: 'react', 
      label: 'React',
      icon: ReactIcon,
      badge: 'Popular',
      style: { badgeColor: '#3b82f6' }
    },
    { 
      value: 'vue', 
      label: 'Vue',
      icon: VueIcon,
      badge: 'New',
      style: { gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }
    },
  ]}
  value={selected}
  onValueChange={setSelected}
/>

// With custom render
<Combobox
  options={frameworks}
  renderValue={(option) => (
    <div className="flex items-center gap-2">
      {option?.icon && <option.icon className="h-4 w-4" />}
      <span>{option?.label}</span>
      {option?.badge && <Badge>{option.badge}</Badge>}
    </div>
  )}
/>
```

### 3. MultiSelectPro

Advanced multi-select with badges, icons, animations.

```tsx
import { MultiSelectPro } from '@djangocfg/ui-core';

<MultiSelectPro
  options={[
    { 
      label: 'JavaScript', 
      value: 'js',
      icon: JsIcon,
      style: { badgeColor: '#f7df1e', iconColor: '#000' }
    },
    { 
      label: 'TypeScript', 
      value: 'ts',
      icon: TsIcon,
      badge: 'Recommended',
      style: { badgeColor: '#3178c6' }
    },
    { 
      label: 'Python', 
      value: 'py',
      icon: PythonIcon,
      description: 'Great for ML/AI'
    },
  ]}
  onValueChange={setSelected}
  maxCount={3}
  variant="default"
/>

// With groups
<MultiSelectPro
  options={[
    {
      heading: 'Frontend',
      options: [
        { label: 'React', value: 'react', icon: ReactIcon },
        { label: 'Vue', value: 'vue', icon: VueIcon },
      ]
    },
    {
      heading: 'Backend',
      options: [
        { label: 'Node.js', value: 'node', icon: NodeIcon },
        { label: 'Django', value: 'django', icon: DjangoIcon },
      ]
    }
  ]}
/>
```

### 4. MultiSelectProAsync

Async version with debounced search.

```tsx
import { MultiSelectProAsync } from '@djangocfg/ui-core';

<MultiSelectProAsync
  options={loadedOptions}
  searchValue={search}
  onSearchChange={(value) => {
    setSearch(value);
    debouncedSearch(value); // Your async search
  }}
  isLoading={isLoading}
  onValueChange={setSelected}
/>
```

### 5. Option Builders

Helper utilities for creating options from data.

```tsx
import { createOption, createOptions } from '@djangocfg/ui-core';

// Single option builder
const buildUserOption = createOption({
  getValue: (user) => user.id,
  getLabel: (user) => user.name,
  getDescription: (user) => user.email,
  getIcon: (user) => user.avatar ? AvatarIcon : UserIcon,
  getStyle: (user) => user.isPremium 
    ? { gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }
    : undefined,
});

const option = buildUserOption(user);

// Batch create options
const options = createOptions(users, {
  getValue: (u) => u.id,
  getLabel: (u) => u.name,
  getDescription: (u) => u.role,
  isDisabled: (u) => !u.isActive,
});
```

## Option API

All components share the same option interface:

```typescript
interface BaseSelectOption {
  value: string;
  label: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string | React.ReactNode;
  disabled?: boolean;
  style?: {
    badgeColor?: string;
    iconColor?: string;
    gradient?: string;
  };
}
```

### Examples

```tsx
// Minimal
{ value: 'a', label: 'Option A' }

// With icon
{ value: 'b', label: 'Option B', icon: MailIcon }

// With badge
{ value: 'c', label: 'Option C', badge: 'New' }

// With description
{ value: 'd', label: 'Option D', description: 'Extra info here' }

// Full featured
{
  value: 'e',
  label: 'Premium Option',
  icon: StarIcon,
  badge: '⭐ Premium',
  description: 'Includes all features',
  style: {
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    iconColor: '#fff'
  }
}

// Disabled
{ value: 'f', label: 'Disabled', disabled: true }
```

## Migration

### Old imports (still work for backwards compatibility)

```tsx
import { Combobox, Select, MultiSelectPro } from '@djangocfg/ui-core';
```

### New imports (recommended)

```tsx
import { 
  Select, SelectTrigger, SelectValue, SelectContent, SelectItem,
  Combobox,
  MultiSelectPro,
  MultiSelectProAsync,
  createOption,
  createOptions,
} from '@djangocfg/ui-core';

// Or deep import
import { Combobox } from '@djangocfg/ui-core/components/select';
```

## What's New

✅ **Icon support** — all components can display icons in options and triggers  
✅ **Badge support** — display badges in triggers and dropdown items  
✅ **Custom styling** — gradient badges, custom colors via `style` prop  
✅ **Unified API** — consistent option interface across all components  
✅ **Organized structure** — all select components in one place
