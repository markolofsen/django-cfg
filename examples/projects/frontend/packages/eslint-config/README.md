# @djangocfg/eslint-config

Shared ESLint configuration for the monorepo.

## What's Inside

- **Base Config** - Core ESLint rules
- **Next.js Config** - Next.js specific rules
- **React Config** - React best practices

## Usage

### Next.js App

```json
{
  "extends": ["@djangocfg/eslint-config/next"]
}
```

### React Library

```json
{
  "extends": ["@djangocfg/eslint-config/react"]
}
```

### Base Config

```json
{
  "extends": ["@djangocfg/eslint-config"]
}
```

## Features

- TypeScript support
- React hooks rules
- Import sorting
- Accessibility checks
- Next.js optimizations
