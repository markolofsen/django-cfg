import { createBaseNextConfig } from '@djangocfg/nextjs/config';

const config = createBaseNextConfig({
  openBrowser: false,
  checkUpdates: false,
  checkPackages: false,
});

export default config;
