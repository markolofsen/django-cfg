'use client';

import { Check, Copy, FlaskConical, KeyRound, Loader2, RefreshCw } from 'lucide-react';
import React from 'react';

import {
  Badge,
  Button,
  Preloader,
  SettingRow,
  SettingsBlock,
} from '@djangocfg/ui-core/components';
import { toast } from '@djangocfg/ui-core/hooks';
import { copyText, cn } from '@djangocfg/ui-core/lib';
import { useAppT } from '@djangocfg/i18n';

import { useSettingsLocale } from '../../i18n';
import { ApiKeyProvider, useApiKeyContext } from './context';

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

// `Intl.DateTimeFormat`, not moment: this was the whole of moment's job here —
// one UTC timestamp rendered in the viewer's zone. moment ships its 137 locale
// files to every consumer that imports anything from this package's barrel,
// which cost the MLS property pages two 805 KB chunks (measured 2026-10-17).
//
// A bare `new Date(iso)` would read a timestamp without a zone designator as
// LOCAL time; the API sends UTC, so the `Z` is appended when it is missing.
function formatDate(iso: string | null, fallback: string, locale: string): string {
  if (!iso) return fallback;
  const utc = /(?:Z|[+-]\d{2}:?\d{2})$/.test(iso) ? iso : `${iso}Z`;
  const date = new Date(utc);
  if (Number.isNaN(date.getTime())) return fallback;
  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

/** Returns true if the backend already masked the key (contains •). */
function isMasked(key: string): boolean {
  return key.includes('•');
}

/**
 * Copies the key the row shows. The row is masked, so the full value is fetched at the click (the reveal call does not rotate the key and the
 * mask stays on screen); a key that was just regenerated is already full and is copied as it is.
 */
function CopyKeyButton() {
  const t = useAppT();
  const { fullKey } = useApiKeyContext();
  const [state, setState] = React.useState<'idle' | 'busy' | 'copied'>('idle');
  const onClick = async () => {
    setState('busy');
    const key = await fullKey();
    const ok = key ? await copyText(key) : false;
    if (!ok) toast.error('Failed to copy the API key');
    setState(ok ? 'copied' : 'idle');
    if (ok) window.setTimeout(() => setState('idle'), 2000);
  };
  const label = state === 'copied' ? t('ui.actions.copied') : t('ui.actions.copyToClipboard');
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="shrink-0"
      aria-label={label}
      tooltip={label}
      disabled={state === 'busy'}
      onClick={onClick}
    >
      {state === 'busy' ? <Loader2 className="h-4 w-4 animate-spin" /> : state === 'copied' ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
    </Button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Inner component (uses context)
// ─────────────────────────────────────────────────────────────────────────────

function ApiKeyCard() {
  const locale = useSettingsLocale();
  const {
    labels,
    apiKey,
    reissuedAt,
    createdAt,
    isLoading,
    error,
    isArmed,
    arm,
    disarm,
    regenerate,
    isRegenerating,
    isFresh,
    dismissFresh,
    testKey,
    isTesting,
    testResult,
  } = useApiKeyContext();

  if (isLoading) {
    return <Preloader variant="inline" className="py-10" />;
  }

  const masked = apiKey ? isMasked(apiKey) : false;
  const displayKey = apiKey ?? '—';

  // Title-row state badge (read-only "Active" indicator). A `div` wrapper —
  // `Badge` renders a block `<div>`, which is invalid inside a `<span>`/`<p>`.
  // SettingRow renders `description` inside a block, so this is valid.
  const titleDescription = (
    <div className="flex flex-wrap items-center gap-2">
      {apiKey && <Badge variant="secondary" className="text-xs">{labels.active}</Badge>}
      <span>{labels.description}</span>
    </div>
  );

  // Action buttons (arm/regenerate/test) for the title row.
  const actions = isArmed ? (
    <div className="flex items-center gap-2">
      <Button
        variant="destructive"
        size="sm"
        onClick={regenerate}
        disabled={isRegenerating}
      >
        {isRegenerating
          ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{labels.regenerating}</>
          : labels.confirmRegenerate}
      </Button>
      <Button variant="ghost" size="sm" onClick={disarm} disabled={isRegenerating}>
        Cancel
      </Button>
    </div>
  ) : (
    // Title row keeps a single action (Regenerate). The Test action moves next
    // to the fresh key below, so this row stays uncluttered.
    <Button
      variant="outline"
      size="sm"
      onClick={arm}
      disabled={!apiKey || isRegenerating}
    >
      <RefreshCw className="mr-2 h-4 w-4" />
      {labels.regenerate}
    </Button>
  );

  return (
    <SettingsBlock>
      <SettingRow
        label={labels.title}
        description={titleDescription}
        action={actions}
      />

      {/* Fresh-key banner — subtle, primary-tinted note */}
      {isFresh && (
        <div className="flex items-center gap-2 rounded-control bg-accent px-3 py-2 text-sm text-foreground">
          <KeyRound className="w-4 h-4 flex-shrink-0 text-primary" />
          <span className="flex-1">{labels.freshKey}</span>
          <Button variant="ghost" size="sm" className="h-7 px-2" onClick={dismissFresh}>
            <Check className="w-4 h-4 mr-1" />
            {labels.done}
          </Button>
        </div>
      )}

      {/* Test result banner */}
      {testResult !== null && (
        <div className={cn(
          'flex items-center gap-2 rounded-control px-3 py-2 text-sm',
          testResult
            ? 'bg-accent text-foreground'
            : 'bg-destructive/10 text-destructive',
        )}>
          <FlaskConical className="w-4 h-4 flex-shrink-0" />
          <span>{testResult ? labels.testSuccess : labels.testFailed}</span>
        </div>
      )}

      {/* API key value row */}
      {apiKey && (
        <SettingRow label={labels.keyRow} stacked>
          <div className="flex items-center gap-2">
            <div className="flex-1 min-w-0 rounded-control bg-muted px-3 py-2.5 font-mono text-sm select-all">
              <span className={cn(masked && 'tracking-widest')}>
                {displayKey}
              </span>
            </div>

            {/* Copy always (a masked key is fetched at the click); Test only when the key is fresh (full key after regenerate) */}
            <CopyKeyButton />
            {isFresh && (
              <>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={testKey}
                  disabled={isTesting}
                  className="shrink-0"
                >
                  {isTesting
                    ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />{labels.testing}</>
                    : <><FlaskConical className="mr-2 h-4 w-4" />{labels.test}</>}
                </Button>
              </>
            )}
          </div>
        </SettingRow>
      )}

      {/* Dates */}
      {apiKey && createdAt && (
        <SettingRow label={labels.created} value={formatDate(createdAt, '—', locale)} />
      )}
      {apiKey && (
        <SettingRow label={labels.reissued} value={formatDate(reissuedAt, labels.neverReissued, locale)} />
      )}

      {error && (
        <p className="pt-3 text-sm text-destructive">{error}</p>
      )}
    </SettingsBlock>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Export (wraps with provider)
// ─────────────────────────────────────────────────────────────────────────────

export const ApiKeySection: React.FC = () => (
  <ApiKeyProvider>
    <ApiKeyCard />
  </ApiKeyProvider>
);
