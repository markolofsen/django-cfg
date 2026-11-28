import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { BarChart3, CreditCard, Plug, ShieldCheck, Sparkles } from 'lucide-react';

import {
  SettingsForm,
  SettingsDialog,
  useSettingsDialog,
  type SettingsSection,
} from '@djangocfg/layouts';
import {
  MockAuthProvider,
  buildMockUser,
  type MockAuthProviderProps,
} from '@djangocfg/layouts/testing';
import { Button, SettingRow, SettingsBlock } from '@djangocfg/ui-core/components';

import { I18nProvider } from '@djangocfg/i18n';
import { ar, da, de, en, es, fr, it, ja, ko, nl, no, pl, ptBR, ru, sv, tr, zh } from '@djangocfg/i18n/locales';
import { LayoutI18nProvider } from '../../shared/LayoutI18nProvider';

// ─── Inline demo helpers ──────────────────────────────────────────────────────

/**
 * UsageRow — a Claude-style consumption row: label on the left, a small
 * "X% used" caption on the right, and a thin progress bar underneath.
 * Built on a plain `bg-primary` fill over a `bg-muted` track so it needs no
 * extra component dependency.
 */
function UsageRow({ label, percent, caption }: { label: string; percent: number; caption?: string }) {
  const pct = Math.max(0, Math.min(100, percent));
  return (
    <div className="divider-b py-3.5">
      <div className="flex items-baseline justify-between gap-4">
        <span className="text-sm text-foreground">{label}</span>
        <span className="text-[13px] tabular-nums text-muted-foreground">
          {caption ?? `${pct}% used`}
        </span>
      </div>
      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

// ─── App section panels ────────────────────────────────────────────────────────

/** Usage panel — progress-bar rows grouped into blocks. */
function UsagePanel() {
  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <SettingsBlock title="This session">
        <UsageRow label="Messages" percent={42} caption="42% used" />
        <UsageRow label="Context window" percent={68} caption="136K / 200K tokens" />
      </SettingsBlock>

      <SettingsBlock title="Plan limits">
        <UsageRow label="Weekly limit" percent={73} caption="73% used" />
        <UsageRow label="API credits" percent={18} caption="$18 of $100" />
        <UsageRow label="File storage" percent={9} caption="0.9 / 10 GB" />
      </SettingsBlock>
    </div>
  );
}

/**
 * Capabilities panel — toggle rows wired to local state so the switches
 * actually flip in Storybook, plus a navigation row that drills into memory.
 */
function CapabilitiesPanel() {
  const [searchChats, setSearchChats] = React.useState(true);
  const [genMemory, setGenMemory] = React.useState(true);
  const [webSearch, setWebSearch] = React.useState(false);
  const [analysisTool, setAnalysisTool] = React.useState(true);

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <SettingsBlock title="Chat & memory">
        <SettingRow
          label="Search and reference chats"
          description="Let the assistant find and cite your past conversations."
          toggle
          checked={searchChats}
          onToggle={setSearchChats}
        />
        <SettingRow
          label="Generate memory from chat history"
          description="Build a long-term memory of your preferences from previous chats."
          toggle
          checked={genMemory}
          onToggle={setGenMemory}
        />
        <SettingRow
          label="View and manage memory"
          description="Review, edit, or delete what the assistant remembers about you."
          navigation
          onClick={() => {}}
        />
      </SettingsBlock>

      <SettingsBlock title="Tools">
        <SettingRow
          label="Web search"
          description="Allow the assistant to search the web for up-to-date answers."
          toggle
          checked={webSearch}
          onToggle={setWebSearch}
        />
        <SettingRow
          label="Analysis tool"
          description="Run code in a sandbox to analyze data and produce charts."
          toggle
          checked={analysisTool}
          onToggle={setAnalysisTool}
        />
      </SettingsBlock>
    </div>
  );
}

/**
 * Privacy panel — toggle rows + navigation rows + an action row, with a
 * small banner at the top (the Claude "How we use your data" pattern).
 */
function PrivacyPanel() {
  const [improveModel, setImproveModel] = React.useState(false);
  const [usageAnalytics, setUsageAnalytics] = React.useState(true);

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {/* Informational banner. */}
      <div className="flex gap-3 rounded-xl border border-border bg-muted/40 p-4">
        <ShieldCheck className="mt-0.5 size-5 shrink-0 text-primary" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-foreground">Your data stays yours</p>
          <p className="text-[13px] leading-relaxed text-muted-foreground">
            We never train on your conversations unless you explicitly opt in below. You can export
            or delete your data at any time.
          </p>
        </div>
      </div>

      <SettingsBlock title="Data controls">
        <SettingRow
          label="Help improve the model"
          description="Allow your chats to be used to train future models."
          toggle
          checked={improveModel}
          onToggle={setImproveModel}
        />
        <SettingRow
          label="Share usage analytics"
          description="Send anonymized interaction metrics to help us improve the product."
          toggle
          checked={usageAnalytics}
          onToggle={setUsageAnalytics}
        />
        <SettingRow
          label="How we use your data"
          description="Read our privacy policy and data-handling practices."
          navigation
          onClick={() => {}}
        />
      </SettingsBlock>

      <SettingsBlock title="Manage your data">
        <SettingRow
          label="Export data"
          description="Download a copy of your account data and conversations."
          action={
            <Button size="sm" variant="outline">
              Export data
            </Button>
          }
        />
        <SettingRow
          label="Delete all chats"
          description="Permanently remove every conversation from your account."
          navigation
          onClick={() => {}}
        />
      </SettingsBlock>
    </div>
  );
}

/** Generic placeholder panel (still used by Billing / Connectors). */
function DemoPanel({ title, lines }: { title: string; lines: string[] }) {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="rounded-xl border border-border bg-card p-5">
        <h3 className="mb-3 text-sm font-medium text-foreground">{title}</h3>
        <div className="space-y-2">
          {lines.map((l) => (
            <div
              key={l}
              className="flex items-center justify-between border-b border-border/60 py-2 text-sm last:border-0"
            >
              <span className="text-muted-foreground">{l}</span>
              <span className="font-medium text-foreground">—</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const APP_SECTIONS: SettingsSection[] = [
  {
    id: 'usage',
    label: 'Usage',
    icon: BarChart3,
    group: 'workspace',
    title: 'Usage',
    description: 'Track your plan limits and consumption.',
    keywords: ['limits', 'quota', 'credits', 'tokens'],
    content: <UsagePanel />,
  },
  {
    id: 'capabilities',
    label: 'Capabilities',
    icon: Sparkles,
    group: 'workspace',
    title: 'Capabilities',
    description: 'Control what the assistant can do and remember.',
    keywords: ['memory', 'tools', 'web search', 'analysis'],
    content: <CapabilitiesPanel />,
  },
  {
    id: 'privacy',
    label: 'Privacy',
    icon: ShieldCheck,
    group: 'workspace',
    title: 'Privacy',
    description: 'Manage data controls and exports.',
    keywords: ['data', 'training', 'analytics', 'export', 'delete'],
    content: <PrivacyPanel />,
  },
  {
    id: 'billing',
    label: 'Billing',
    icon: CreditCard,
    group: 'workspace',
    title: 'Billing',
    description: 'Payment method and invoices.',
    keywords: ['payment', 'invoice', 'card', 'subscription'],
    content: <DemoPanel title="Billing" lines={['Payment method', 'Plan', 'Invoices']} />,
  },
  {
    id: 'connectors',
    label: 'Connectors',
    icon: Plug,
    group: 'workspace',
    title: 'Connectors',
    description: 'Integrations and external services.',
    keywords: ['integration', 'webhook', 'oauth'],
    content: <DemoPanel title="Connectors" lines={['Slack', 'GitHub', 'Google Drive']} />,
  },
];

const GROUPS = [
  { id: 'general', order: 0 },
  { id: 'workspace', label: 'Workspace', order: 1 },
];

// ─── Frame ────────────────────────────────────────────────────────────────────

interface SettingsFrameArgs {
  preset?: 'full' | 'sparse' | 'admin';
  security?: boolean;
  apiKeys?: boolean;
  searchable?: boolean | 'auto';
  withAppSections?: boolean;
}

function presetToUser(preset: SettingsFrameArgs['preset']): MockAuthProviderProps['user'] {
  switch (preset) {
    case 'sparse':
      return buildMockUser({ first_name: '', last_name: '', company: null, phone: null, position: null, initials: 'JC' });
    case 'admin':
      return buildMockUser({ is_staff: true, is_superuser: true, first_name: 'Avery', last_name: 'Quinn', email: 'avery@acme.com', company: 'Acme Inc.', position: 'Founder', initials: 'AQ' });
    case 'full':
    default:
      return buildMockUser({ company: 'Acme Inc.', position: 'Product Designer', phone: '+1 (555) 010-2233' });
  }
}

// A host-owned preference, to show `generalRows` ("Other") beside the built-ins.
const GENERAL_ROWS = (
  <SettingRow label="Date format" description="Used for dates and reports." action={<Button variant="outline" size="sm">DD.MM.YYYY</Button>} />
);

// Language only renders under a layout i18n context, as in a real app. A host mounts both
// providers on one locale: layout i18n drives the switcher, `@djangocfg/i18n` the copy
// (dialog strings and widgets a host adds). `allTranslations` is the central catalogue a host
// passes (profile labels etc.).
const ALL_TRANSLATIONS = { en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da, 'pt-BR': ptBR };

function WithLocales({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = React.useState('en');
  return (
    <I18nProvider locale={locale as never} allTranslations={ALL_TRANSLATIONS as never} onLocaleChange={(next) => setLocale(next)}>
      <LayoutI18nProvider value={{ locale, locales: ['en', 'ru', 'de', 'es'], onLocaleChange: setLocale }}>
        {children}
      </LayoutI18nProvider>
    </I18nProvider>
  );
}

function frameProps(args: SettingsFrameArgs) {
  return {
    generalRows: GENERAL_ROWS,
    builtins: { security: args.security, apiKeys: args.apiKeys },
    searchable: args.searchable,
    sections: args.withAppSections ? APP_SECTIONS : [],
    groups: args.withAppSections ? GROUPS : undefined,
  };
}

// Inline variant — the form embedded on a page.
function SettingsInlineFrame(args: SettingsFrameArgs) {
  const user = presetToUser(args.preset);
  return (
    <div className="h-screen bg-muted/20 p-6">
      <div className="mx-auto h-full max-w-5xl">
        <MockAuthProvider user={user} isLoading={false}>
          <SettingsForm {...frameProps(args)} />
        </MockAuthProvider>
      </div>
    </div>
  );
}

// Dialog variant — the global modal, opened by a button.
function DialogOpener() {
  const settings = useSettingsDialog();
  return (
    <div className="flex flex-wrap gap-2">
      <Button onClick={() => settings.open()}>Open settings</Button>
      <Button variant="outline" onClick={() => settings.open('usage')}>
        Open on Usage
      </Button>
      <Button variant="outline" onClick={() => settings.open('capabilities')}>
        Open on Capabilities
      </Button>
    </div>
  );
}

function SettingsDialogFrame(args: SettingsFrameArgs) {
  const user = presetToUser(args.preset);
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6">
      <MockAuthProvider user={user} isLoading={false}>
        <DialogOpener />
        {/* syncUrl off in Storybook (the preview iframe URL shouldn't be hijacked). */}
        <SettingsDialog {...frameProps(args)} syncUrl={false} />
      </MockAuthProvider>
    </div>
  );
}

// Dialog variant that auto-opens on the Usage section (progress-bar showcase).
function UsageDialogFrame(args: SettingsFrameArgs) {
  const user = presetToUser(args.preset);
  return (
    <MockAuthProvider user={user} isLoading={false}>
      <AutoOpenUsage />
      <SettingsDialog {...frameProps(args)} syncUrl={false} />
    </MockAuthProvider>
  );
}

// Opens the dialog on the Usage section as soon as the story mounts.
function AutoOpenUsage() {
  const settings = useSettingsDialog();
  React.useEffect(() => {
    settings.open('usage');
    // open() identity is stable enough for a mount-once effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/20 p-6">
      <Button variant="outline" onClick={() => settings.open('usage')}>
        Reopen on Usage
      </Button>
    </div>
  );
}

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta = {
  title: 'Packages/Layouts/SettingsLayout',
  decorators: [(Story) => <WithLocales><Story /></WithLocales>],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Claude-style settings surface: searchable section rail + scrollable detail panel. ' +
          'Available as an inline `SettingsForm` or a global, hash-URL-driven `SettingsDialog` ' +
          '(`useSettingsDialog().open()`). App sections (Usage / Capabilities / Privacy) are built ' +
          'with the universal `SettingRow` + `SettingsBlock` primitives from `@djangocfg/ui-core`. ' +
          '\n\n' +
          '**Note on built-in sections:** the Account section renders fully from the mocked ' +
          '`useAuth()` user. The Account security block and API-keys section fetch live data via real ' +
          'React Query hooks (`useTwoFactorStatus`, `useApiKey`) against the backend, for ' +
          'which Storybook has no mock/MSW layer — so they will show a spinner or an error here. ' +
          'They are intentionally NOT faked; Account is the built-in showcase.',
      },
    },
  },
  argTypes: {
    preset: { control: 'inline-radio', options: ['full', 'sparse', 'admin'] },
    security: { control: 'boolean' },
    apiKeys: { control: 'boolean' },
    searchable: { control: 'inline-radio', options: [true, false, 'auto'] },
    withAppSections: { control: 'boolean' },
  },
  args: {
    preset: 'full',
    // All built-in sections shown in the rail by default so the full surface is
    // visible. (Security/API-keys panels need a live backend, so their BODIES
    // show a 404/empty state in Storybook — that's expected; toggle off via the
    // controls to hide them.)
    security: true,
    apiKeys: true,
    searchable: 'auto',
    withAppSections: true,
  },
} satisfies Meta<SettingsFrameArgs>;

export default meta;
type Story = StoryObj<SettingsFrameArgs>;

export const Inline: Story = {
  render: (args) => <SettingsInlineFrame {...args} />,
};

export const Dialog: Story = {
  render: (args) => <SettingsDialogFrame {...args} />,
};

// Opens straight onto the Usage section to show the progress-bar rows.
export const DialogOnUsage: Story = {
  render: (args) => <UsageDialogFrame {...args} />,
};

export const BuiltinsOnly: Story = {
  args: { withAppSections: false },
  render: (args) => <SettingsInlineFrame {...args} />,
};

export const NoSearch: Story = {
  args: { searchable: false },
  render: (args) => <SettingsInlineFrame {...args} />,
};

// Live-backend built-ins enabled — shows the spinner/error behaviour described
// in the component docs (no Storybook mock layer for these hooks).
export const WithLiveBuiltins: Story = {
  args: { security: true, apiKeys: true },
  render: (args) => <SettingsInlineFrame {...args} />,
};
