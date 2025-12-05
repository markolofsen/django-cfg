import { defineConfig } from 'vite';

// https://vitejs.dev/config
export default defineConfig({
  build: {
    rollupOptions: {
      external: [
        // Only truly native modules that cannot be bundled
        'node-pty',
      ],
    },
  },
});
