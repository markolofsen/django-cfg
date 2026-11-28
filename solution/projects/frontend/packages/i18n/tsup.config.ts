import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    'cli/index': 'src/cli/index.ts',
    // Built with `index` so both share ONE context chunk: `createCopy` reads the
    // provider the host mounts from the root entry.
    'copy/index': 'src/copy/index.ts',
    'copy/testing': 'src/copy/testing.ts',
  },
  format: ['esm'],
  dts: true,
  splitting: true,
  sourcemap: true,
  clean: true,
  treeshake: true,
  minify: false,
  target: 'es2020',
  platform: 'node',
  external: ['react', 'jiti'],
  outExtension() {
    return { js: '.mjs' };
  },
});
