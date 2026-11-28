/**
 * Smoke suite of the GENERATED client (H2.1 of djangocfg `@dev/active/orval-client-hardening`).
 *
 * `smoke/**` calls operations from the tracked Orval tree in `src/_api/generated`, the output of
 * `manage.py gen --target packages` in `solution/django` (`make generate` here). That tree's runtime shim imports
 * this package's handwritten runtime by a relative path, so the suite exercises generated code plus the current
 * runtime source, with no build and no Django process. `pnpm test` runs it after the unit tests, and
 * `make test-fast` in django-cfg runs it through
 * `django_generator/tests/integration/test_generated_client_smoke.py`.
 *
 * The suite has its own config for one reason: `inlinePublicEnv`. Next.js replaces the literal text
 * `process.env.NEXT_PUBLIC_NAME` when it builds a page and leaves every other way of reading the environment
 * (`globalThis.process.env`, an aliased `process.env`) empty in the browser. `@djangocfg/api@2.1.663` read it
 * indirectly and sent every request to the page's own origin. Vitest's `define` cannot reproduce that: it turns
 * `process.env.*` entries into runtime assignments, which an indirect read would also see.
 */
import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

import { SMOKE_BUILD_ENV } from './smoke/env.ts';

const SRC = fileURLToPath(new URL('./src/', import.meta.url));
const PUBLIC_ENV_READ = /\bprocess\.env\.(NEXT_PUBLIC_[A-Z0-9_]+)\b/g;

function inlinePublicEnv(values: Readonly<Record<string, string>>) {
  return {
    name: 'djangocfg:inline-next-public-env',
    enforce: 'pre' as const,
    transform(code: string, id: string) {
      if (!id.startsWith(SRC) || !code.includes('process.env.NEXT_PUBLIC_')) return null;
      return {
        code: code.replace(PUBLIC_ENV_READ, (_read, name: string) =>
          name in values ? JSON.stringify(values[name]) : 'undefined',
        ),
        map: null,
      };
    },
  };
}

export default defineConfig({
  root: fileURLToPath(new URL('.', import.meta.url)),
  plugins: [inlinePublicEnv(SMOKE_BUILD_ENV)],
  test: {
    // Per file: the browser cases opt into jsdom with a `@vitest-environment` header.
    environment: 'node',
    include: ['smoke/**/*.test.ts'],
  },
});
