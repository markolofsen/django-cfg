# Package Publishing Strategy

## Overview

All packages are published to npm as `@djangocfg/*` scoped packages under MIT license. The publishing system uses a temporary directory (`.tmp`) to automatically replace `workspace:*` dependencies with real npm versions, keeping local development flexible while ensuring npm packages work correctly.

## Package Types

### 🎨 UI/Component Packages (No Build Required)

**Packages:** `@djangocfg/ui`, `@djangocfg/layouts`, `@djangocfg/markdown`

**Strategy:**
- **Local Development:** Direct TS imports via `transpilePackages` in Next.js
- **Publishing:** Source files in `src/` directory
- **Why:** Next.js transpiles them automatically, no build step needed

**Benefits:**
- ✅ Faster development (no rebuild needed)
- ✅ Better debugging (source maps not needed)
- ✅ Smaller package size (no dist overhead)

**package.json:**
```json
{
  "name": "@djangocfg/ui",
  "version": "1.0.1",
  "license": "MIT",
  "author": {
    "name": "DjangoCFG",
    "url": "https://djangocfg.com"
  },
  "main": "./src/index.ts",
  "files": ["src", "README.md", "LICENSE"],
  "exports": {
    ".": "./src/index.ts"
  },
  "publishConfig": {
    "access": "public"
  }
}
```

### 🔧 Utility Packages (Build Required)

**Packages:** `@djangocfg/og-image`, `@djangocfg/api`

**Strategy:**
- **Local Development:** Built with `tsup` in watch mode
- **Publishing:** `dist/` for main exports + `src/` for additional exports
- **Why:** Standalone utilities, need compilation

**Benefits:**
- ✅ Works in any environment (Edge Runtime, Node.js)
- ✅ Optimized output
- ✅ Type definitions generated

**Special Case - @djangocfg/api:**
This package uses a **hybrid approach** - both `dist/` and `src/`:
- `dist/` - Contains compiled main exports (`./dist/index.js`)
- `src/` - Contains additional TypeScript exports for contexts and generated code

**Why both?**
- Main API client is compiled for performance and compatibility
- Contexts and generated code are TypeScript source for better DX
- Allows exports like `@djangocfg/api/cfg/contexts` to work correctly

**package.json:**
```json
{
  "name": "@djangocfg/api",
  "version": "1.0.11",
  "license": "MIT",
  "author": {
    "name": "DjangoCFG",
    "url": "https://djangocfg.com"
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "files": ["dist", "src", "README.md", "LICENSE"],
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./cfg/contexts": {
      "types": "./src/cfg/contexts/index.ts",
      "import": "./src/cfg/contexts/index.ts",
      "default": "./src/cfg/contexts/index.ts"
    },
    "./cfg/generated": {
      "types": "./src/cfg/generated/index.ts",
      "import": "./src/cfg/generated/index.ts"
    }
  },
  "scripts": {
    "build": "tsup"
  },
  "publishConfig": {
    "access": "public"
  }
}
```

### ⚙️ Config Packages (No Build)

**Packages:** `@djangocfg/typescript-config`, `@djangocfg/eslint-config`

**Strategy:**
- **Publishing:** JSON/JS config files only
- **Why:** Configuration files don't need compilation

**package.json:**
```json
{
  "name": "@djangocfg/typescript-config",
  "version": "1.0.1",
  "license": "MIT",
  "author": {
    "name": "DjangoCFG",
    "url": "https://djangocfg.com"
  },
  "files": ["*.json", "*.js", "README.md", "LICENSE"],
  "publishConfig": {
    "access": "public"
  }
}
```

## Files Control

The `"files"` field controls what gets published to npm:

### ✅ What's Included

- `dist/` - Built code (for compiled packages)
- `src/` - Source code (for UI packages)
- `README.md` - Documentation
- Config files (for config packages)

### ❌ What's Excluded (Automatic)

- `node_modules/` - Always excluded
- `.git/` - Always excluded
- `*.test.ts` - Test files excluded
- `.env*` - Environment files excluded
- Any files not in `"files"` array

## Publishing to npm

All packages are configured for public npm publishing under the `@djangocfg` organization.

### Publishing System

The publishing system uses a **temporary directory approach** to maintain `workspace:*` dependencies locally while publishing real versions to npm:

1. **Creates `.tmp` directory** - Temporary workspace for publishing
2. **Copies packages** - Source files (excluding `node_modules`, `dist`)
3. **Replaces dependencies** - All `workspace:*` → actual versions (e.g., `^1.0.1`)
4. **Builds packages** - Compiles utility packages (api, og-image)
5. **Publishes to npm** - From `.tmp` with real dependency versions
6. **Cleans up** - Removes `.tmp` after publishing

**Benefits:**
- ✅ Local files keep `workspace:*` for flexible development
- ✅ npm packages have real versions that work in external projects
- ✅ No manual version replacement needed
- ✅ Automated through Makefile

### Using the Makefile

```bash
cd packages

# View all available commands
make help

# Check npm login status
make check

# Publish packages (interactive)
make publish

# Bump patch version and publish (1.0.0 → 1.0.1)
make publish-patch

# Bump minor version and publish (1.0.0 → 1.1.0)
make publish-minor

# Bump major version and publish (1.0.0 → 2.0.0)
make publish-major

# List all packages with versions
make list

# Clean dist folders and tmp
make clean
```

### Workspace Dependencies

**In Source Files (Local Development):**
```json
{
  "dependencies": {
    "@djangocfg/ui": "workspace:*",
    "@djangocfg/api": "workspace:*"
  },
  "devDependencies": {
    "@djangocfg/typescript-config": "workspace:*"
  }
}
```

**After Publishing to npm (Automatic):**
```json
{
  "dependencies": {
    "@djangocfg/ui": "^1.0.1",
    "@djangocfg/api": "^1.0.10"
  },
  "devDependencies": {
    "@djangocfg/typescript-config": "^1.0.1"
  }
}
```

The Makefile automatically handles this transformation during publishing.

### Manual Publishing (Not Recommended)

If you need to publish manually without the Makefile:

```bash
# 1. Build packages with build scripts
cd packages/og-image
pnpm build
cd ../api
pnpm build

# 2. Manually replace workspace:* in package.json
# 3. Publish
npm publish --access public

# 4. Restore workspace:* dependencies
```

**⚠️ Use `make publish` instead** - it automates all steps and prevents mistakes.

## Local Development

### No Build Needed

For UI/layouts packages, Next.js handles transpilation:

```js
// next.config.ts
export default {
  transpilePackages: [
    '@djangocfg/ui',
    '@djangocfg/layouts',
    '@djangocfg/markdown'
  ]
}
```

### Build During Development

For utility packages with watch mode:

```bash
cd packages/og-image
pnpm dev  # tsup --watch
```

## Verification

Check what would be published:

```bash
# See files that would be included
cd packages/ui
npm pack --dry-run

# Create tarball (doesn't publish)
npm pack
```

## Summary

| Package | Build | Files Included | Reason |
|---------|-------|----------------|--------|
| `ui` | ❌ No | `src/`, `tailwind.config.js` | Next.js transpiles |
| `layouts` | ❌ No | `src/` | Next.js transpiles |
| `markdown` | ❌ No | `src/` | Next.js transpiles |
| `og-image` | ✅ Yes | `dist/` | Edge Runtime, standalone |
| `api` | ✅ Yes | `dist/` + `src/` | Hybrid: compiled main + TS contexts |
| `typescript-config` | ❌ No | `*.json` | Config files |
| `eslint-config` | ❌ No | `*.js` | Config files |

## Dependency Management

### PeerDependencies Strategy

Packages use `peerDependencies` for shared dependencies to avoid duplication:

```json
{
  "peerDependencies": {
    "@djangocfg/api": "workspace:*",
    "@djangocfg/ui": "workspace:*",
    "react": "^19.1.0",
    "next": "^15.4.4"
  }
}
```

**Why `workspace:*` in peerDependencies?**
- Local development: pnpm resolves to local workspace packages
- npm publishing: Makefile replaces with actual versions (e.g., `^1.0.1`)
- External projects: Install the versions they need

### Using Published Packages in External Projects

**Step 1: Install packages from npm**
```bash
pnpm add @djangocfg/ui@^1.0.1
pnpm add @djangocfg/layouts@^1.0.1
pnpm add @djangocfg/api@^1.0.11
pnpm add @djangocfg/og-image@^1.0.1
```

**Step 2: Configure Next.js**

Add `transpilePackages` to transpile TypeScript source packages:

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: [
    "@djangocfg/ui",
    "@djangocfg/layouts",
    "@djangocfg/markdown",
    "@djangocfg/api"  // Required for /cfg/contexts and /cfg/generated exports
  ],
};

export default nextConfig;
```

**Why @djangocfg/api needs transpilation:**
Even though the main API client is pre-compiled in `dist/`, the additional exports from `src/cfg/contexts` and `src/cfg/generated` are TypeScript source files that require transpilation.

**Step 3: Configure Tailwind CSS**

Update paths to reference `node_modules` instead of local packages:

```javascript
// tailwind.config.js
module.exports = {
  // Use UI package as preset
  presets: [require('@djangocfg/ui/tailwind.config')],

  // Content paths must point to node_modules
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@djangocfg/ui/src/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@djangocfg/layouts/src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
};
```

**Step 4: Use in your code**

```typescript
// Import components
import { Button } from '@djangocfg/ui';
import { AppLayout } from '@djangocfg/layouts';

// Import API client
import { api } from '@djangocfg/api';
import { useAccountsContext } from '@djangocfg/api/cfg/contexts';

// Import OG image utilities
import { generateOgImageUrl } from '@djangocfg/og-image/utils';
```

**package.json example:**
```json
{
  "dependencies": {
    "@djangocfg/ui": "^1.0.1",
    "@djangocfg/layouts": "^1.0.1",
    "@djangocfg/api": "^1.0.11",
    "@djangocfg/og-image": "^1.0.1"
  }
}
```

## Published Versions

**Current versions on npm:**

| Package | Version | Size | Status |
|---------|---------|------|--------|
| `@djangocfg/api` | 1.0.11 | 817 KB | ✅ Published |
| `@djangocfg/ui` | 1.0.1 | 68 KB | ✅ Published |
| `@djangocfg/layouts` | 1.0.1 | 88 KB | ✅ Published |
| `@djangocfg/markdown` | 1.0.1 | 1.5 KB | ✅ Published |
| `@djangocfg/og-image` | 1.0.1 | 15 KB | ✅ Published |
| `@djangocfg/typescript-config` | 1.0.1 | 1.9 KB | ✅ Published |
| `@djangocfg/eslint-config` | 1.0.1 | 2.0 KB | ✅ Published |

**Links:**
- npm Organization: https://www.npmjs.com/org/unrealon
- View all packages: https://www.npmjs.com/search?q=%40unrealon

## Author & License

All packages include:
- **Author:** [Reforms.ai](https://reforms.ai)
- **License:** MIT
- **Access:** Public (available on npm)
- **Organization:** @djangocfg

## Common Issues & Solutions

### Issue: TypeScript errors with `@djangocfg/*` imports

**Error:**
```
Module parse failed: Unexpected token
You may need an appropriate loader to handle this file type
```

**Solution:**
Add `transpilePackages` to `next.config.ts`:
```typescript
transpilePackages: [
  '@djangocfg/ui',
  '@djangocfg/layouts',
  '@djangocfg/markdown',
  '@djangocfg/api'  // Required for TypeScript exports
]
```

### Issue: Tailwind classes not working

**Error:**
Tailwind classes from `@djangocfg/ui` components don't apply styles.

**Solution:**
Update `tailwind.config.js` content paths:
```javascript
content: [
  './src/**/*.{js,ts,jsx,tsx,mdx}',
  './node_modules/@djangocfg/ui/src/**/*.{js,ts,jsx,tsx,mdx}',
  './node_modules/@djangocfg/layouts/src/**/*.{js,ts,jsx,tsx,mdx}',
]
```

### Issue: Cannot resolve `@djangocfg/api/cfg/contexts`

**Error:**
```
Module not found: Can't resolve '@djangocfg/api/cfg/contexts'
```

**Solution:**
This was fixed in version 1.0.11. Update to latest version:
```bash
pnpm update @djangocfg/api@latest
```

The `src/` folder is now included in the published package.

### Issue: Old services_old folder causing TypeScript errors

**Solution:**
Exclude from TypeScript check in `tsconfig.json`:
```json
{
  "exclude": [
    "node_modules",
    "src/api/services_old"
  ]
}
```

---

**Last Updated:** 2025-10-11
**Status:** ✅ Published to npm with automated workspace dependency handling
**Tested:** ✅ Successfully tested in external project (bitapi)
