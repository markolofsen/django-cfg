# Routes Module

**Simple, flat structure. 5 files total.**

## 📁 Structure

```
routes/
├── index.ts         # Main exports + singleton (150 lines)
├── definitions.ts   # Route definitions (250 lines)
├── menus.ts         # Menu generation (120 lines)
├── guards.ts        # Route protection (40 lines)
└── helpers.ts       # Utilities (90 lines)
```

**Total:** ~650 lines across 5 files

## 🚀 Quick Start

```typescript
import { routes, generatePublicNavigation, menuGroups } from '@/core/routes';

// Access routes
const home = routes.public.home;
const dashboard = routes.private.overview;

// Menus (pre-generated)
const navMenu = generatePublicNavigation();
const dashMenu = menuGroups;

// Route guards
if (isPrivateRoute('/private/profile')) {
  // Handle protected route
}

// Utilities
const title = getPageTitle('/private/workspaces');
const breadcrumbs = generateBreadcrumbs('/private/profile');
```

## 📝 Adding New Routes

Edit `definitions.ts`:

```typescript
readonly pricing = this.route('/pricing', {
  label: 'Pricing',
  description: 'View pricing plans',
  icon: DollarSign,
  protected: false,
  group: 'main',      // For menu generation
  order: 2,           // Order in menu
});
```

Menu updates automatically! ✨

## 💡 Why This Structure is Better

### Before (18 files, 3 directories)
```
routes/
├── types.ts
├── base.ts
├── instance.ts
├── public.ts
├── private.ts
├── guards.ts
├── menu/
│   ├── index.ts
│   ├── types.ts
│   ├── generators.ts
│   ├── dashboard.ts
│   ├── public.ts
│   └── footer.ts
└── utils/
    ├── index.ts
    ├── active.ts
    ├── breadcrumbs.ts
    └── titles.ts
```

### After (5 files, flat)
```
routes/
├── index.ts         # Everything you need
├── definitions.ts   # All routes
├── menus.ts         # All menus
├── guards.ts        # Protection
└── helpers.ts       # Utils
```

## ✅ Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Files** | 18 | 5 |
| **Directories** | 3 (nested) | 1 (flat) |
| **index.ts files** | 3 | 1 |
| **Navigation** | Jump between many files | One file per concern |
| **Imports** | Complex paths | Simple imports |
| **Maintenance** | Hard to find code | Easy to locate |

## 🔍 File Responsibilities

### definitions.ts
- Route definitions (Public + Private)
- Route metadata
- Dynamic route helpers

### menus.ts
- Menu generation functions
- Dashboard menu
- Public navigation
- Footer navigation

### guards.ts
- Route protection checks
- Redirect logic
- Auth detection

### helpers.ts
- Page titles
- Active route checking
- Breadcrumb generation

### index.ts
- Singleton instance
- All exports
- Bound helper functions

## 📚 Examples

See `appLayoutConfig.ts` for real usage.

---

**Clean. Simple. Maintainable.** 🚀
