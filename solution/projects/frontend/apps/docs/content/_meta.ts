/**
 * Docs information architecture for the standalone docs site (docs.djangocfg.com).
 *
 * Top-level navbar entries use `type: 'page'`. Everything else is sidebar
 * structure. URLs are root-based (no /docs prefix) — this site IS the docs domain.
 */
export default {
  // ── Landing (hidden from sidebar; full-width, no sidebar/toc) ──
  index: {
    type: 'page',
    display: 'hidden',
    theme: {
      layout: 'full',
      sidebar: false,
      toc: false,
      breadcrumb: false,
      pagination: false,
      timestamp: false,
    },
  },

  // ── Navbar: Docs (the documentation tree) ──
  'getting-started': {
    type: 'page',
    title: 'Docs',
  },

  '---core': { type: 'separator', title: 'Core' },
  core: 'Core',
  configuration: 'Configuration',
  database: 'Database',

  '---features': { type: 'separator', title: 'Features' },
  features: 'Features',
  extensions: 'Extensions',

  '---frontend': { type: 'separator', title: 'Frontend (Next.js)' },
  frontend: 'Frontend',

  '---guides': { type: 'separator', title: 'Guides' },
  guides: 'Guides',
  deployment: 'Deployment',

  '---reference': { type: 'separator', title: 'Reference' },
  api: 'API Reference',

  // ── Navbar: CLI ──
  cli: {
    type: 'page',
    title: 'CLI',
  },

  // ── Navbar: Updates (blog / releases / security) ──
  updates: {
    type: 'page',
    title: 'Updates',
  },

  // ── Navbar: external product links (Nextra appends its own ↗) ──
  // Source of truth for these URLs: settings.site.demo / settings.site.ui.
  'demo-site': {
    type: 'page',
    title: 'Demo',
    href: 'https://demo.djangocfg.com',
  },
  'ui-site': {
    type: 'page',
    title: 'UI',
    href: 'https://ui.djangocfg.com',
  },

  // ── Navbar: Contact (standalone marketing-style page — no TOC/sidebar) ──
  contact: {
    type: 'page',
    title: 'Contact',
    theme: {
      toc: false,
      sidebar: false,
      breadcrumb: false,
      pagination: false,
      timestamp: false,
    },
  },

  // ── Navbar: Business ──
  business: {
    type: 'page',
    title: 'Business',
    display: 'hidden',
  },
};
