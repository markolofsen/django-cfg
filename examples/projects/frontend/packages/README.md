# @djangocfg Packages

Internal packages for the Unrealon monorepo.

## Available Packages

- **@djangocfg/api** - Type-safe API client
- **@djangocfg/eslint-config** - Shared ESLint configuration
- **@djangocfg/layouts** - Layout system and components
- **@djangocfg/markdown** - Markdown parsing utilities
- **@djangocfg/og-image** - OG image generation
- **@djangocfg/typescript-config** - Shared TypeScript configuration
- **@djangocfg/ui** - UI components and Tailwind preset

## Publishing to NPM

### Prerequisites

1. Login to npm:
```bash
npm login
```

2. Make sure all packages are ready to publish

### Quick Start

```bash
# Show available commands
make help

# Check npm login status
make check

# List all packages and versions
make list

# Build all packages
make build

# Publish with current versions
make publish

# Bump patch version (1.0.0 -> 1.0.1) and publish
make publish-patch

# Bump minor version (1.0.0 -> 1.1.0) and publish
make publish-minor

# Bump major version (1.0.0 -> 2.0.0) and publish
make publish-major
```

### Publishing Workflow

**Option 1: Quick Patch Release**
```bash
cd packages
make publish-patch
```

**Option 2: Manual Version Control**
```bash
# 1. Update versions manually in package.json files
# 2. Build and publish
make build
make publish
```

**Option 3: Minor/Major Release**
```bash
# Minor release (new features)
make publish-minor

# Major release (breaking changes)
make publish-major
```

### What Happens

1. **Check** - Verifies you're logged in to npm
2. **Clean** - Removes all dist folders
3. **Build** - Builds all packages with pnpm
4. **Bump** (if using publish-patch/minor/major) - Updates version in package.json
5. **Publish** - Publishes to npm with `--access public`

### Notes

⚠️ All packages are published with `--access public` flag since they are scoped packages (@djangocfg)

⚠️ Make sure to test packages locally before publishing

⚠️ Publishing is irreversible - you cannot unpublish after 24 hours

### Troubleshooting

**Not logged in to npm:**
```bash
npm login
```

**Package already exists at this version:**
- Bump version: `make publish-patch`
- Or manually update version in package.json

**Build failed:**
- Check package build script
- Install dependencies: `pnpm install`
- Fix TypeScript errors

**Permission denied:**
- Make sure you're part of @djangocfg organization on npm
- Or publish to your own scope
