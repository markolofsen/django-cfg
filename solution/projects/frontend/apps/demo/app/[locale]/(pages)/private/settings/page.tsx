'use client';

import { useThemeContext } from '@djangocfg/ui-core/theme';
import { useLocaleSwitcher } from '@djangocfg/nextjs/i18n/client';

import { useAppTranslations } from '@i18n';

const LOCALE_LABELS: Record<string, string> = {
  en: 'English',
  ru: 'Русский',
  ko: '한국어',
};

const THEMES = ['light', 'dark', 'system'] as const;

export default function SettingsPage() {
  const { app } = useAppTranslations();
  const { theme, setTheme } = useThemeContext();
  const { locale, locales, changeLocale } = useLocaleSwitcher();

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold">{app('settings.title')}</h1>
      </header>

      <div className="rounded-2xl border border-border bg-card p-6 space-y-6">
        <fieldset>
          <legend className="text-sm font-medium text-foreground mb-3">{app('settings.theme')}</legend>
          <div className="flex flex-wrap gap-2">
            {THEMES.map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTheme(t)}
                className={`rounded-full px-4 py-1.5 text-sm border transition-colors ${
                  theme === t
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'border-border text-muted-foreground hover:bg-secondary/50'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="text-sm font-medium text-foreground mb-3">{app('settings.language')}</legend>
          <div className="flex flex-wrap gap-2">
            {locales
              .filter((l) => l in LOCALE_LABELS)
              .map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => changeLocale(l)}
                  className={`rounded-full px-4 py-1.5 text-sm border transition-colors ${
                    locale === l
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:bg-secondary/50'
                  }`}
                >
                  {LOCALE_LABELS[l]}
                </button>
              ))}
          </div>
        </fieldset>
      </div>
    </section>
  );
}
