# @djangocfg/typescript-config

> Shared TypeScript configurations for Next.js, React libraries, and Node.js projects with strict type checking

[![npm version](https://img.shields.io/npm/v/@djangocfg/typescript-config.svg)](https://www.npmjs.com/package/@djangocfg/typescript-config)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Part of [DjangoCFG](https://djangocfg.com)** — a modern Django framework for building production-ready SaaS applications. All `@djangocfg/*` packages are designed to work together, providing type-safe configuration, real-time features, and beautiful admin interfaces out of the box.

---

## Overview

`@djangocfg/typescript-config` provides battle-tested TypeScript configurations for modern web development. It includes presets for Next.js applications, React component libraries, and general TypeScript projects.

## Features

- **Strict Mode** - Maximum type safety with strict compiler options
- **Next.js Preset** - Optimized for Next.js App Router
- **React Library Preset** - Configured for publishing React packages
- **Path Aliases** - Standard path mapping configuration
- **Modern Target** - ES2022 output for modern runtimes

## Installation

```bash
npm install -D @djangocfg/typescript-config
# or
pnpm add -D @djangocfg/typescript-config
# or
yarn add -D @djangocfg/typescript-config
```

## Usage

### Next.js Application

```json
{
  "extends": "@djangocfg/typescript-config/nextjs.json",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### React Library

```json
{
  "extends": "@djangocfg/typescript-config/react-library.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### Base Configuration

```json
{
  "extends": "@djangocfg/typescript-config/base.json",
  "compilerOptions": {
    "outDir": "dist"
  }
}
```

## Available Configs

| Config | Description |
|--------|-------------|
| `base.json` | Base strict TypeScript configuration |
| `nextjs.json` | Next.js App Router configuration |
| `react-library.json` | React component library configuration |

## Compiler Options

All configurations include these strict options:

```json
{
  "strict": true,
  "esModuleInterop": true,
  "skipLibCheck": true,
  "resolveJsonModule": true,
  "isolatedModules": true,
  "noUncheckedIndexedAccess": true,
  "noImplicitOverride": true,
  "forceConsistentCasingInFileNames": true
}
```

## Documentation

Full documentation available at [djangocfg.com](https://djangocfg.com)

## Contributing

Issues and pull requests are welcome at [GitHub](https://github.com/markolofsen/django-cfg)

## License

MIT - see [LICENSE](./LICENSE) for details
