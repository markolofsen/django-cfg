import type { Metadata } from 'next';
import '@fontsource-variable/plus-jakarta-sans';
import { Layout, Navbar } from 'nextra-theme-docs';
import { Head } from 'nextra/components'; // `Search` removed — search disabled in <Layout> below
import { getPageMap } from 'nextra/page-map';
import 'nextra-theme-docs/style.css';
import '@core/styles/index.css';

import { settings } from '@core/settings';
import { SiteFooter } from '@components/layout/SiteFooter';
import { OrganizationJsonLd, SoftwareApplicationJsonLd } from '@components/seo/json-ld';

export const metadata: Metadata = {
  metadataBase: new URL(settings.app.docsUrl),
  title: {
    default: settings.app.title,
    template: settings.app.titleTemplate,
  },
  description: settings.app.description,
  icons: { icon: '/favicon.png' },
};

const logo = (
  <span className="brand-logo">
    {/* white mark on the dark-default theme */}
    <img src="/static/logos/vector_white.svg" alt="Django-CFG" />
    <b>Django-CFG</b>
  </span>
);

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pageMap = await getPageMap();
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head backgroundColor={settings.theme.backgroundColor} />
      <body>
        <OrganizationJsonLd />
        <SoftwareApplicationJsonLd />
        {/* Search disabled (search={null}). To re-enable: import { Search } from 'nextra/components' and pass search={<Search placeholder="Search docs…" />}. */}
        <Layout
          navbar={
            <Navbar logo={logo} logoLink="/" projectLink={settings.github.org}>
              <a
                className="navbar-login"
                href={settings.nav.login.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                {settings.nav.login.label}
              </a>
            </Navbar>
          }
          search={null}
          pageMap={pageMap}
          docsRepositoryBase={settings.github.docsRepositoryBase}
          editLink={settings.shell.editLink}
          feedback={settings.shell.feedback}
          sidebar={{ defaultMenuCollapseLevel: 1, autoCollapse: true }}
          footer={<SiteFooter />}
          nextThemes={{
            defaultTheme: settings.shell.defaultTheme,
            forcedTheme: settings.shell.forcedTheme,
          }}
        >
          {children}
        </Layout>
      </body>
    </html>
  );
}
