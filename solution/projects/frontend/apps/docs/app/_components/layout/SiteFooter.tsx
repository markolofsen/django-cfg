import { settings } from '@core/settings';

/**
 * Vercel-style site footer: brand block (logo + tagline) on the left, link
 * columns on the right, then a bottom bar with copyright + GitHub.
 * Plain CSS (.site-footer* in app/_core/styles/) — no Nextra utilities.
 */
export function SiteFooter() {
  // Prepare all data above the JSX — no logic inlined in the return.
  const { name, description } = settings.app;
  const { copyright } = settings.footer;
  const githubUrl = settings.github.org;

  const columns = settings.footer.columns.map((col) => ({
    title: col.title,
    links: col.links.map((link) => ({
      ...link,
      external: link.href.startsWith('http'),
    })),
  }));

  return (
    <div className="site-footer">
      <div className="site-footer__inner">
        <div className="site-footer__top">
          <div className="site-footer__brand">
            <span className="site-footer__logo">
              <img src="/static/logos/vector_white.svg" alt={name} />
              <b>{name}</b>
            </span>
            <p className="site-footer__tagline">{description}</p>
          </div>

          <div className="site-footer__cols">
            {columns.map((col) => (
              <div key={col.title}>
                <h3 className="site-footer__title">{col.title}</h3>
                <ul className="site-footer__list">
                  {col.links.map((link) => (
                    <li key={link.href}>
                      <a
                        href={link.href}
                        target={link.external ? '_blank' : undefined}
                        rel={link.external ? 'noreferrer' : undefined}
                        className="site-footer__link"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="site-footer__bottom">
          <span className="site-footer__copyright">{copyright}</span>
          <a
            href={githubUrl}
            target="_blank"
            rel="noreferrer"
            className="site-footer__bottom-link"
          >
            GitHub ↗
          </a>
        </div>
      </div>
    </div>
  );
}
