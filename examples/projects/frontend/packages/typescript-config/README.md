# @djangocfg/typescript-config

Shared TypeScript configuration for the monorepo.

## What's Inside

- **base.json** - Base TypeScript config
- **nextjs.json** - Next.js specific config
- **react-library.json** - React library config

## Usage

### Next.js App

```json
{
  "extends": "@djangocfg/typescript-config/nextjs.json",
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### React Library/Package

```json
{
  "extends": "@djangocfg/typescript-config/react-library.json",
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Base Config

```json
{
  "extends": "@djangocfg/typescript-config/base.json",
  "compilerOptions": {
    // Your overrides
  }
}
```

## Features

- **Strict Mode** - Enabled for type safety
- **Path Aliases** - Configured for monorepo
- **Module Resolution** - ESNext with bundler resolution
- **JSX Support** - React 19 compatible

## Settings

All configs include:
- `strict: true`
- `esModuleInterop: true`
- `skipLibCheck: true`
- `resolveJsonModule: true`
- `isolatedModules: true`
