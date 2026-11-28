import nextra from 'nextra';

const withNextra = nextra({
  // Docs are served from the app root on this standalone site (docs.djangocfg.com).
  // (The old embedded app used contentDirBasePath: '/docs' because it shared a
  // domain with marketing; here docs own the whole site.)
});

/** @type {import('next').NextConfig} */
const config = {
  // `standalone` is for self-hosted / Docker only. On Vercel it breaks routing
  // (every route 404s), so enable it only when BUILD_STANDALONE=1 (Docker build).
  //
  // Setting it in the Dockerfile is NOT enough: Turbo 2 runs tasks in strict env
  // mode, so a variable the build is not declared to read simply is not there.
  // `BUILD_STANDALONE` must stay listed under tasks.build.env in
  // ../../turbo.json — without it this branch silently stays off, the build
  // still succeeds, and the runner stage fails on a missing .next/standalone.
  ...(process.env.BUILD_STANDALONE ? { output: 'standalone' } : {}),
  reactStrictMode: true,
  // Moved pages keep their old URL working (search engines and old links).
  async redirects() {
    return [
      // 2.4.0: Unfold removed, the page became the stock-admin site config.
      { source: '/features/modules/django-unfold', destination: '/features/modules/admin-site', permanent: true },
      { source: '/features/modules/django-unfold/:path*', destination: '/features/modules/admin-site', permanent: true },
    ];
  },
  // Type-checking is ON in the build (no ignoreBuildErrors) — the migrated
  // content/_meta.ts files type-check cleanly against Nextra's MetaRecord, so
  // real type errors should fail CI. `pnpm check` runs the same check standalone.
};

export default withNextra(config);
