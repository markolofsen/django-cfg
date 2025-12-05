import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',
    'grpc/index': 'src/grpc/index.ts',
    'pty/index': 'src/pty/index.ts',
  },
  format: ['esm'],
  dts: true,
  clean: true,
  sourcemap: true,
  target: 'node20',
  platform: 'node',
  external: ['electron', 'node-pty'],
  treeshake: true,
});
