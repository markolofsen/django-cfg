import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  useMicDevices,
  useResolvedLanguage,
  useSpeechLanguageInfo,
} from '.';

type Args = {
  override: string;
};

function LanguageInfoCard({ override }: Args) {
  const tag = useResolvedLanguage(override || undefined);
  const info = useSpeechLanguageInfo();

  return (
    <div className="w-[460px] space-y-2 rounded-lg border border-border bg-background p-4 text-sm">
      <div className="text-base font-semibold">Active speech language</div>
      <div className="grid grid-cols-[120px_1fr] gap-y-1 font-mono text-xs">
        <span className="text-muted-foreground">resolved tag</span>
        <span>{tag}</span>
        <span className="text-muted-foreground">info.tag</span>
        <span>{info.tag}</span>
        <span className="text-muted-foreground">iso</span>
        <span>{info.iso}</span>
        <span className="text-muted-foreground">country</span>
        <span>{info.country ?? '—'}</span>
        <span className="text-muted-foreground">name</span>
        <span>{info.name ?? '—'}</span>
        <span className="text-muted-foreground">englishName</span>
        <span>{info.englishName ?? '—'}</span>
        <span className="text-muted-foreground">region</span>
        <span>{info.region ?? '—'}</span>
        <span className="text-muted-foreground">hasUserChoice</span>
        <span>{String(info.hasUserChoice)}</span>
      </div>
      <p className="text-xs text-muted-foreground">
        Pass an override via Controls to see resolution change. Without
        an override the value comes from
        <code className="font-mono"> useSpeechPrefs</code> → i18n →
        <code className="font-mono"> navigator.language</code> →
        <code className="font-mono"> en-US</code>.
      </p>
    </div>
  );
}

function LanguageDeviceMatrix({ override }: Args) {
  const tag = useResolvedLanguage(override || undefined);
  const info = useSpeechLanguageInfo();
  const { devices, refresh } = useMicDevices();

  return (
    <div className="w-[520px] space-y-3 rounded-lg border border-border bg-background p-4 text-sm">
      <div className="text-base font-semibold">Language × Device matrix</div>
      <div className="flex items-center gap-2 text-xs">
        <span className="rounded-md border border-border px-2 py-1 font-mono">
          {tag}
        </span>
        <span className="text-muted-foreground">
          {info.name ?? info.englishName ?? 'unknown locale'}
        </span>
        <button
          type="button"
          onClick={() => void refresh()}
          className="ml-auto rounded-md border border-border px-2 py-1 text-xs hover:bg-muted"
        >
          refresh devices
        </button>
      </div>
      <div className="rounded-md border border-border">
        <div className="border-b border-border bg-muted/40 px-3 py-1 font-mono text-[11px] uppercase tracking-wide text-muted-foreground">
          audio inputs ({devices.length})
        </div>
        {devices.length === 0 ? (
          <div className="px-3 py-4 text-xs text-muted-foreground">
            No devices visible. Browsers hide labels until the page has
            been granted mic permission at least once.
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {devices.map((d) => (
              <li
                key={d.deviceId || d.label}
                className="flex items-center justify-between gap-3 px-3 py-2 font-mono text-[11px]"
              >
                <span className="truncate">{d.label}</span>
                <span className="shrink-0 text-muted-foreground">
                  {d.deviceId ? d.deviceId.slice(0, 12) + '…' : '—'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Languages',
  component: LanguageInfoCard,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Read `useResolvedLanguage` + `useSpeechLanguageInfo` to surface the active BCP-47 tag, ISO subtag, region, and whether the user picked it explicitly. `useMicDevices` lists `audioinput` devices.',
      },
    },
  },
  argTypes: {
    override: {
      control: 'select',
      options: ['', 'en-US', 'en-GB', 'ru-RU', 'de-DE', 'fr-FR', 'ja-JP', 'cmn-Hans-CN'],
      table: { category: 'Resolution' },
    },
  },
  args: { override: '' },
} satisfies Meta<typeof LanguageInfoCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const LanguageInfo: Story = {};

export const Matrix: Story = {
  render: (args) => <LanguageDeviceMatrix {...args} />,
};

export const ExplicitOverride: Story = {
  args: { override: 'ru-RU' },
  parameters: {
    docs: {
      description: {
        story:
          'Pass `override` to `useResolvedLanguage` to force a tag — useful for embedding the field inside a parent that already knows the locale.',
      },
    },
  },
};
