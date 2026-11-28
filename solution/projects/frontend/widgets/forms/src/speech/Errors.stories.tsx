import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  ErrorBanner,
  useVoiceSupport,
  type RecognitionErrorCode,
} from '.';

const CODES: RecognitionErrorCode[] = [
  'unsupported',
  'permission-denied',
  'no-microphone',
  'network',
  'aborted',
  'no-speech',
  'language',
  'engine',
  'unknown',
];

type Args = {
  code: RecognitionErrorCode;
  customMessage: string;
  dismissable: boolean;
};

function ErrorBannerDemo({ code, customMessage, dismissable }: Args) {
  const [dismissed, setDismissed] = useState(false);
  if (dismissed) {
    return (
      <button
        type="button"
        onClick={() => setDismissed(false)}
        className="rounded-md border border-border px-2 py-1 text-xs"
      >
        re-show banner
      </button>
    );
  }
  return (
    <div className="w-[460px]">
      <ErrorBanner
        error={{ code, message: customMessage }}
        onDismiss={dismissable ? () => setDismissed(true) : undefined}
      />
    </div>
  );
}

function AllCodes() {
  return (
    <div className="flex w-[460px] flex-col gap-2">
      {CODES.map((c) => (
        <ErrorBanner key={c} error={{ code: c, message: `(${c})` }} />
      ))}
    </div>
  );
}

function VoiceSupportProbe() {
  const support = useVoiceSupport();
  return (
    <div className="w-[460px] space-y-2 rounded-lg border border-border bg-background p-4 text-sm">
      <div className="text-base font-semibold">useVoiceSupport()</div>
      <div className="grid grid-cols-[140px_1fr] gap-y-1 font-mono text-xs">
        <span className="text-muted-foreground">supported</span>
        <span>{String(support.supported)}</span>
        <span className="text-muted-foreground">reason</span>
        <span>{support.reason ?? '—'}</span>
        <span className="text-muted-foreground">engineId</span>
        <span>{support.engineId ?? '—'}</span>
        <span className="text-muted-foreground">isMobile</span>
        <span>{String(support.isMobile)}</span>
        <span className="text-muted-foreground">isInApp</span>
        <span>{String(support.isInApp)}</span>
      </div>
      {!support.supported && (
        <ErrorBanner
          error={{
            code: support.reason === 'no-mediadevices' ? 'no-microphone' : 'unsupported',
            message: '',
          }}
        />
      )}
      <p className="text-xs text-muted-foreground">
        Hosts call this before mounting <code className="font-mono">VoiceComposerSlot</code>.
        When unsupported the slot returns <code className="font-mono">null</code>.
      </p>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Errors',
  component: ErrorBannerDemo,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Every `RecognitionErrorCode` rendered through `<ErrorBanner>`, plus the `useVoiceSupport` gate that decides whether to mount the mic at all.',
      },
    },
  },
  argTypes: {
    code: {
      control: 'select',
      options: CODES,
      table: { category: 'Banner' },
    },
    customMessage: { control: 'text', table: { category: 'Banner' } },
    dismissable: { control: 'boolean', table: { category: 'Banner' } },
  },
  args: {
    code: 'permission-denied',
    customMessage: '',
    dismissable: true,
  },
} satisfies Meta<typeof ErrorBannerDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const PermissionDenied: Story = {
  args: { code: 'permission-denied', dismissable: false },
};

export const Unsupported: Story = {
  args: { code: 'unsupported', dismissable: false },
};

export const AllCodesGrid: Story = {
  render: () => <AllCodes />,
  parameters: {
    docs: {
      description: {
        story: 'Every code in one view — useful for designers eyeballing copy.',
      },
    },
  },
};

export const VoiceSupportGate: Story = {
  render: () => <VoiceSupportProbe />,
  parameters: {
    docs: {
      description: {
        story:
          'Inspect what `useVoiceSupport` reports inside the Storybook iframe. Firefox and in-app browsers will report `supported: false`.',
      },
    },
  },
};
