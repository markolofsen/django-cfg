import { LottiePlayer } from '@components/home/LottiePlayer';
import { settings } from '@core/settings';

const features = [
  {
    title: 'Type-safe configuration',
    body: 'Replace settings.py with Pydantic v2 models. Config errors are caught at startup, not in production — with full IDE autocomplete and validation.',
  },
  {
    title: 'Auto-discovered extensions',
    body: 'Drop a module into extensions/ and it self-registers: URLs, admin, Constance fields, and scheduled tasks wire up by convention.',
  },
  {
    title: 'Batteries included',
    body: 'User management, payments, leads, LLM, email, Telegram, RQ tasks, currency, geo, and more — built-in apps you enable with a flag.',
  },
  {
    title: 'Type-safe API clients',
    body: 'Generate fully typed TypeScript clients from your DRF endpoints. The frontend and backend share one contract.',
  },
  {
    title: 'Pure-Django admin dashboard',
    body: 'A tabbed admin dashboard built on Django templates + callbacks — no Streamlit, no separate stack to deploy.',
  },
  {
    title: 'CLI-first workflow',
    body: 'Scaffold projects, inspect config, and search settings with the django-cfg CLI. From zero to a running SaaS in minutes.',
  },
];

export function HomeHero() {
  return (
    <div className="home">
      <section className="home__hero">
        <div className="home__hero-copy">
          <span className="home__eyebrow">Type-safe Django framework</span>
          <h1 className="home__title">
            Django, the <span className="home__title-accent">type-safe&nbsp;way.</span>
          </h1>
          <p className="home__subtitle">
            A modern Django framework with Pydantic v2 configuration. Replace
            brittle settings.py with validated models, auto-discovered
            extensions, batteries-included apps, and generated type-safe API
            clients — ship professional SaaS platforms faster.
          </p>
          <div className="home__actions">
            <a href="/getting-started" className="home__btn home__btn--cta">
              Get started →
            </a>
            <a
              href={settings.github.org}
              target="_blank"
              rel="noreferrer"
              className="home__btn home__btn--secondary"
            >
              GitHub
            </a>
          </div>
          <div className="home__cmd">
            <span className="home__cmd-dollar">$</span> pip install django-cfg
          </div>

          <dl className="home__stats">
            <div className="home__stat">
              <dt className="home__stat-value">Pydantic&nbsp;v2</dt>
              <dd className="home__stat-label">Validated config</dd>
            </div>
            <div className="home__stat">
              <dt className="home__stat-value">Batteries</dt>
              <dd className="home__stat-label">Built-in apps</dd>
            </div>
            <div className="home__stat">
              <dt className="home__stat-value">Typed</dt>
              <dd className="home__stat-label">API clients</dd>
            </div>
          </dl>
        </div>

        <div className="home__hero-visual">
          <LottiePlayer
            src="/lottie/coding.json"
            className="home__lottie"
            ariaLabel="Django-CFG developer animation"
          />
        </div>
      </section>

      <section className="home__grid">
        {features.map((f) => (
          <div key={f.title} className="home__card">
            <h3 className="home__card-title">{f.title}</h3>
            <p className="home__card-body">{f.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
