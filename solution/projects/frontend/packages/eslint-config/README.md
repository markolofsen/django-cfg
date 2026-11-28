# @djangocfg/eslint-config

> Shared ESLint configurations for Next.js, React, and TypeScript projects with best practices and Prettier integration

[![npm version](https://img.shields.io/npm/v/@djangocfg/eslint-config.svg)](https://www.npmjs.com/package/@djangocfg/eslint-config)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Part of [DjangoCFG](https://djangocfg.com)** — a modern Django framework for building production-ready SaaS applications. All `@djangocfg/*` packages are designed to work together, providing type-safe configuration, real-time features, and beautiful admin interfaces out of the box.

---

## Overview

`@djangocfg/eslint-config` provides battle-tested ESLint configurations for modern JavaScript and TypeScript projects. It includes presets for Next.js applications, React libraries, and general TypeScript projects.

## Features

- **Next.js Preset** - Optimized rules for Next.js App Router
- **React Preset** - React hooks and JSX best practices
- **TypeScript Support** - Full typescript-eslint integration
- **Prettier Compatible** - Works seamlessly with Prettier
- **Turbo Support** - Turborepo-aware caching rules
- **ESLint 9** - Uses flat config format

## Installation

```bash
npm install -D @djangocfg/eslint-config eslint
# or
pnpm add -D @djangocfg/eslint-config eslint
# or
yarn add -D @djangocfg/eslint-config eslint
```

## Usage

### Next.js Projects

```js
// eslint.config.mjs
import nextConfig from '@djangocfg/eslint-config/next-js';

export default nextConfig;
```

### React Libraries

```js
// eslint.config.mjs
import reactConfig from '@djangocfg/eslint-config/react-internal';

export default reactConfig;
```

### Base TypeScript

```js
// eslint.config.mjs
import baseConfig from '@djangocfg/eslint-config/base';

export default baseConfig;
```

## Available Configs

| Config | Description |
|--------|-------------|
| `@djangocfg/eslint-config/base` | Base TypeScript configuration |
| `@djangocfg/eslint-config/next-js` | Next.js App Router configuration |
| `@djangocfg/eslint-config/react-internal` | React library configuration |

## Included Plugins

- `@eslint/js` - ESLint recommended rules
- `typescript-eslint` - TypeScript linting
- `eslint-plugin-react` - React specific rules
- `eslint-plugin-react-hooks` - Hooks rules
- `@next/eslint-plugin-next` - Next.js rules
- `eslint-plugin-turbo` - Turborepo rules
- `eslint-config-prettier` - Prettier compatibility

## Documentation

Full documentation available at [djangocfg.com](https://djangocfg.com)

## Contributing

Issues and pull requests are welcome at [GitHub](https://github.com/markolofsen/django-cfg)

## License

MIT - see [LICENSE](./LICENSE) for details
