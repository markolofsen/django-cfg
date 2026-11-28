'use client';

import { Plug } from 'lucide-react';

import { CopyButton } from '@djangocfg/ui-core';

import { agentSetupPrompt, manualFields, mcpServersConfig, type ManualField } from '../install';
import { AccessBar } from './access/AccessBar';
import { BRANDS, brandById, nameOf, type Variant } from './clients';
import { useMcpConnect } from './context';
import { QuickConnect } from './QuickConnect';
import { Field, Header, PrimaryAction, SMALL_ACTION, Steps, Tile } from './parts';
import { HINT, NAME } from './styles';
import { ServerCan } from '../info/ServerCan';
import { McpRenew } from '../renew/McpRenew';

import type { McpConnectCopy } from '../i18n';

/** The screen for the current view. Home is tiles only; everything else adds a way back. */
export function Views() {
  const { view } = useMcpConnect();
  switch (view.kind) {
    case 'home':
      return <Home />;
    case 'manual':
      return <Manual />;
    case 'brand':
      return <BrandScreen id={view.id} />;
  }
}

const GRID = 'grid grid-cols-2 gap-2 sm:grid-cols-3';

/** One screen, one tile per app plus "Other app", nothing else: no key, no list. */
function Home() {
  const { labels, go } = useMcpConnect();
  return (
    <div className={GRID}>
      {BRANDS.map((brand) => (
        <Tile key={brand.id} layout="tile" Mark={brand.Mark} name={brand.name} literal onClick={() => go({ kind: 'brand', id: brand.id })} />
      ))}
      <Tile layout="tile" Mark={Plug} name={labels.otherApp} literal={false} onClick={() => go({ kind: 'manual' })} />
    </div>
  );
}

/** The steps a client needs, by how it connects. At most three. */
function stepsFor(variant: Variant, labels: McpConnectCopy): string[] {
  switch (variant.flow) {
    case 'connector':
      return [labels.stepConnector1, labels.stepConnector2];
    case 'url':
      return [labels.stepUrl1, labels.stepUrl2.replace('{where}', variant.where ? labels[variant.where] : ''), labels.stepUrl3];
    case 'command':
      return [labels.stepCmd1, labels.stepCmd2];
    case 'link':
      return [labels.stepLink1, labels.stepLink2];
  }
}

/**
 * One app: its mark and name, then one section per way to connect it (a web connector, a terminal command, a deeplink), each with
 * its primary action and few steps. OAuth ways never show a key; the key bar appears once, if any way needs the key.
 */
function BrandScreen({ id }: { id: string }) {
  const { labels } = useMcpConnect();
  const brand = brandById(id);
  if (!brand) return <Header />;
  const { Mark } = brand;
  const several = brand.variants.length > 1;
  return (
    <div className="flex flex-col gap-4">
      <Header />
      <div className="flex items-center gap-3">
        <Mark width={32} height={32} className="shrink-0" aria-hidden />
        <span translate="no" className="text-base font-semibold leading-6 text-foreground">
          {brand.name}
        </span>
      </div>
      {brand.variants.map((variant) => (
        <Way key={variant.id} variant={variant} titled={several} />
      ))}
      {brand.variants.some((v) => v.auth === 'key') ? <AccessBar /> : null}
      <ServerCan />
    </div>
  );
}

/** One way to connect an app: a title when the app has several, the primary action, the steps. */
function Way({ variant, titled }: { variant: Variant; titled: boolean }) {
  const { labels } = useMcpConnect();
  return (
    <section className={titled ? 'flex flex-col gap-3 rounded-xl border border-border bg-background p-4' : 'flex flex-col gap-4'}>
      <span className="flex min-w-0 flex-col">
        {titled ? (
          <span translate="no" className={NAME}>
            {nameOf(variant, labels)}
          </span>
        ) : null}
        <span className={HINT}>{labels[variant.hint]}</span>
      </span>
      <PrimaryAction variant={variant} />
      <Steps items={stepsFor(variant, labels).map((text) => ({ text }))} />
    </section>
  );
}

const FIELD_LABEL = {
  url: 'fieldUrl',
  name: 'fieldName',
  header: 'fieldHeader',
  secret: 'fieldSecret',
} as const satisfies Record<ManualField['id'], keyof McpConnectCopy>;

/** Any other app: a stepper card with the form's values where each step needs them, then two shortcuts. */
function Manual() {
  const { server, labels, access } = useMcpConnect();
  const key = access.kind === 'signedIn' && access.key.kind === 'ready' ? access.key.key : null;
  const fields = manualFields(server, key);
  const field = (id: ManualField['id']) => {
    const f = fields.find((x) => x.id === id);
    return <Field key={id} label={labels[FIELD_LABEL[id]]} shown={f?.shown ?? '••••'} value={f?.value ?? null} />;
  };
  const prompt = agentSetupPrompt(server, key, { body: labels.promptBody, keyLine: labels.promptKeyLine });

  return (
    <div className="flex flex-col gap-4">
      <Header />
      <QuickConnect />
      <span className={HINT}>{labels.manualLede}</span>
      <div className="rounded-xl border border-border bg-background p-4 pb-0">
        <Steps
          items={[
            { text: labels.manualStep1 },
            { text: labels.manualStep2, extra: <>{field('url')}{field('name')}<span className={NAME}>{labels.fieldAuth}: {labels.authOauth}</span></> },
            { text: labels.manualStep3, extra: <>{field('header')}{field('secret')}<span className={HINT}>{labels.noBasic}</span></> },
          ]}
      />
      </div>
      {/* The key already sits in the last step once it is ready; the bar is only for the states that need a control. */}
      {access.kind === 'signedIn' && access.key.kind === 'ready' ? null : <AccessBar />}
      <div className="flex flex-col gap-2">
        <Shortcut title={labels.copyPrompt} hint={labels.promptHint} value={prompt} />
        <Shortcut title={labels.otherFamily} hint={labels.configHint} value={key ? mcpServersConfig(server, key) : null} />
      </div>
      <ServerCan />
      {access.kind === 'signedIn' && access.renewal ? <McpRenew renewal={access.renewal} /> : null}
    </div>
  );
}

/** A secondary Copy: what it copies and why. */
function Shortcut({ title, hint, value }: { title: string; hint: string; value: string | null }) {
  const { labels, access } = useMcpConnect();
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-3 py-2.5">
      <span className="flex min-w-0 flex-1 flex-col">
        <span className={NAME}>{title}</span>
        <span className={HINT}>{hint}</span>
      </span>
      {access.kind === 'signedIn' && value ? (
        <CopyButton value={value} size="sm" variant="outline" className={SMALL_ACTION} iconClassName="size-3.5">
          {labels.copy}
        </CopyButton>
      ) : (
        <CopyButton value="" size="sm" variant="outline" className={SMALL_ACTION} iconClassName="size-3.5" disabled>
          {labels.copy}
        </CopyButton>
      )}
    </div>
  );
}
