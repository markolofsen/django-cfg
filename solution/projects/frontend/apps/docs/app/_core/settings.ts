/**
 * Centralized config for the standalone docs site.
 *
 * Single source of truth for brand strings, the main product site URL, GitHub
 * links, and the Nextra shell options. Import from `@core/settings` instead of
 * hardcoding URLs in components or MDX.
 */

const GITHUB_ORG = 'https://github.com/markolofsen/django-cfg';

/** The main product/marketing site (separate app → djangocfg.com). */
const MAIN_SITE = 'https://djangocfg.com';

export const settings = {
  /** Brand / site identity. */
  app: {
    name: 'Django-CFG',
    title: 'Django-CFG Documentation',
    titleTemplate: '%s — Django-CFG Docs',
    description:
      'Django-CFG documentation — a modern, type-safe Django framework with Pydantic v2 configuration.',
    /** This docs site. */
    docsUrl: 'https://docs.djangocfg.com',
    /** The main marketing/product site. */
    siteUrl: MAIN_SITE,
  },

  /** Links back to the main product site (docs only hosts documentation). */
  site: {
    home: MAIN_SITE,
    demo: 'https://demo.djangocfg.com',
    ui: 'https://ui.djangocfg.com',
  },

  /**
   * Public contact details — single source of truth for the /contact page.
   */
  contact: {
    email: 'info@djangocfg.com',
    /** WhatsApp number in E.164 (digits used to build the wa.me link). */
    whatsapp: '+6281339646301',
    /** Book a call. */
    calendly: 'https://calendly.com/markolofsen/meeting',
    /** Office location (display only). */
    location: 'San Francisco, CA',
  },

  /**
   * Extra navbar links beyond the content-driven tabs.
   * Rendered into Nextra's <Navbar> via the `content/_meta.ts` external `href`
   * entries (keys: demo-site / ui-site); kept here as the single source of truth
   * for label + target. Keep these in sync with content/_meta.ts.
   * (The "Home" → main-site tab was removed from the navbar; the main-site URL
   * still lives in `site.home` and is used by the landing hero.)
   */
  nav: {
    demo: { label: 'Demo', href: 'https://demo.djangocfg.com' },
    ui: { label: 'UI', href: 'https://ui.djangocfg.com' },
    /** Primary navbar CTA — links to the live demo. */
    login: { label: 'Get started →', href: 'https://demo.djangocfg.com' },
  },

  /** All GitHub links, derived from one org root. */
  github: {
    org: GITHUB_ORG,
    /** Main repo (editable docs live in the canonical frontend workspace). */
    repo: GITHUB_ORG,
    /** Base used by Nextra's "Edit this page on GitHub". */
    docsRepositoryBase: `${GITHUB_ORG}/tree/main/solution/projects/frontend/apps/docs/content`,
  },

  /** Nextra <Layout> chrome. */
  shell: {
    editLink: 'Edit this page on GitHub',
    feedback: {
      content: 'Question? Give us feedback',
      labels: 'feedback',
    },
    defaultTheme: 'dark' as const,
    /** Force dark across the docs — light theme isn't designed for the navbar
        logo / chrome. Remove to re-enable the theme switcher. */
    forcedTheme: 'dark' as const,
  },

  /** <Head> theme colors. */
  theme: {
    backgroundColor: {
      dark: 'rgb(9, 9, 11)',
      light: 'rgb(250, 250, 250)',
    },
  },

  /** Footer link columns (Vercel-style). */
  footer: {
    columns: [
      {
        title: 'Documentation',
        links: [
          { label: 'Getting Started', href: '/getting-started' },
          { label: 'Configuration', href: '/configuration' },
          { label: 'Features', href: '/features' },
          { label: 'CLI Tools', href: '/cli' },
          { label: 'API Reference', href: '/api' },
        ],
      },
      {
        title: 'Frontend',
        links: [
          { label: 'Architecture', href: '/frontend/architecture' },
          { label: 'Data Layer', href: '/frontend/data-layer' },
          { label: 'Recipes', href: '/frontend/recipes/ui-components' },
          { label: 'DevOps', href: '/devops' },
          { label: 'Deployment', href: '/deployment' },
        ],
      },
      {
        title: 'Resources',
        links: [
          { label: 'Demo', href: 'https://demo.djangocfg.com' },
          { label: 'UI Components', href: 'https://ui.djangocfg.com' },
          { label: 'Blog', href: '/updates/blog' },
          { label: 'Changelog', href: '/updates/releases' },
        ],
      },
      {
        title: 'Company',
        links: [
          { label: 'GitHub', href: GITHUB_ORG },
          { label: 'djangocfg.com', href: MAIN_SITE },
          { label: 'Contact', href: '/contact' },
          { label: 'Security', href: '/updates/security' },
        ],
      },
    ],
    copyright: `© ${new Date().getFullYear()} Django-CFG. MIT Licensed.`,
  },
} as const;

export type Settings = typeof settings;
