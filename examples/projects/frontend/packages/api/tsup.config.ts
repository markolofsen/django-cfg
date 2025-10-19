import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  outDir: 'dist',
  target: 'node18',
  platform: 'node',
  sourcemap: true,
  clean: true,
  dts: true,
  external: ['react', 'react-dom', 'next', '@djangocfg/auth'],
  outExtension({ format }) {
    return format === 'esm' ? { js: '.mjs' } : { js: '.cjs' };
  },
});
