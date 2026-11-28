import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Send } from 'lucide-react';

import { Textarea } from '@djangocfg/ui-core/components';
import { VoiceComposerSlot } from '.';

import { createMockEngine } from './_helpers/mockEngine';

type Args = {
  size: 'sm' | 'md' | 'lg';
  hideOnMobile: boolean;
  silenceMs: number;
  maxSeconds: number;
  sounds: boolean;
  useMock: boolean;
};

function FakeComposer({
  size,
  hideOnMobile,
  silenceMs,
  maxSeconds,
  sounds,
  useMock,
}: Args) {
  const [value, setValue] = useState('');
  const [submitted, setSubmitted] = useState<string[]>([]);
  const engine = useMemo(
    () => (useMock ? createMockEngine() : undefined),
    [useMock],
  );

  function submit() {
    const trimmed = value.trim();
    if (!trimmed) return;
    setSubmitted((s) => [...s, trimmed]);
    setValue('');
  }

  return (
    <div className="flex w-[560px] flex-col gap-3">
      {submitted.length > 0 && (
        <div className="flex flex-col gap-1 rounded-lg border border-border bg-background p-3">
          <div className="text-[11px] uppercase tracking-wide text-muted-foreground">
            sent
          </div>
          {submitted.map((m, i) => (
            <div
              key={i}
              className="rounded-md bg-muted/40 px-2 py-1 text-xs"
            >
              {m}
            </div>
          ))}
        </div>
      )}
      <div className="flex items-end gap-2 rounded-lg border border-border bg-background p-2">
        <Textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          rows={2}
          placeholder="Type or press the mic to dictate…"
          className="flex-1 resize-none border-none shadow-none focus-visible:ring-0"
        />
        <div className="flex items-center gap-1">
          <VoiceComposerSlot
            value={value}
            onChange={setValue}
            engine={engine}
            hideOnMobile={hideOnMobile}
            silenceMs={silenceMs}
            maxSeconds={maxSeconds}
            size={size}
            sounds={sounds}
            onFinish={() => undefined}
          />
          <button
            type="button"
            onClick={submit}
            className="inline-flex h-9 items-center justify-center rounded-full bg-primary px-3 text-primary-foreground hover:bg-primary/90"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
      <p className="text-xs text-muted-foreground">
        Standalone usage (no <code className="font-mono">ChatProvider</code>) — pass
        <code className="font-mono"> value</code> /
        <code className="font-mono"> onChange</code> directly. Inside a real chat the
        slot reads the composer handle registered by{' '}
        <code className="font-mono">useRegisterComposer</code> automatically and you
        can omit both props.
      </p>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Composer slot',
  component: FakeComposer,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          '`VoiceComposerSlot` is a drop-in mic button for chat composers. It returns `null` when the host browser cannot do STT. This story wires it into a plain textarea via explicit `value`/`onChange`; inside `<ChatProvider>` it reads the registered composer handle on its own.',
      },
    },
  },
  argTypes: {
    size: {
      control: 'inline-radio',
      options: ['sm', 'md', 'lg'],
      table: { category: 'Button' },
    },
    hideOnMobile: { control: 'boolean', table: { category: 'Button' } },
    silenceMs: {
      control: { type: 'number', min: 500, max: 8000, step: 250 },
      table: { category: 'AutoStop' },
    },
    maxSeconds: {
      control: { type: 'number', min: 10, max: 300, step: 5 },
      table: { category: 'AutoStop' },
    },
    sounds: { control: 'boolean', table: { category: 'Audio' } },
    useMock: { control: 'boolean', table: { category: 'Engine' } },
  },
  args: {
    size: 'md',
    hideOnMobile: false,
    silenceMs: 2500,
    maxSeconds: 90,
    sounds: true,
    useMock: true,
  },
} satisfies Meta<typeof FakeComposer>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const InsideTextarea: Story = {};

export const NoSounds: Story = { args: { sounds: false } };

export const LargeButton: Story = { args: { size: 'lg' } };

export const BrowserNative: Story = {
  args: { useMock: false },
  parameters: {
    docs: {
      description: {
        story:
          'Uses real Web Speech API. Slot collapses to `null` in Firefox / in-app WebViews via `useVoiceSupport`.',
      },
    },
  },
};

/**
 * State showcase — three composer slots side by side. The mock engine
 * starts dictating on press: `idle` mic → pulsing `listening` ring →
 * `processing` spinner while the final result settles. Press the mic in
 * each to drive it through the cycle and watch the animated transitions.
 */
function StatesShowcase() {
  const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
  return (
    <div className="flex flex-col gap-6">
      <p className="max-w-[460px] text-xs text-muted-foreground">
        Press a mic to run the mock dictation. The button reflects four
        engine-driven states: <code className="font-mono">idle</code>,{' '}
        <code className="font-mono">listening</code> (pulsing circle overlay +
        accent fill), <code className="font-mono">processing</code> (spinner)
        and <code className="font-mono">error</code> (destructive tint).
      </p>
      <div className="flex items-end gap-8">
        {sizes.map((size) => (
          <div key={size} className="flex flex-col items-center gap-2">
            <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
              {size}
            </span>
            <SlotCell size={size} />
          </div>
        ))}
      </div>
    </div>
  );
}

function SlotCell({ size }: { size: 'sm' | 'md' | 'lg' }) {
  const [value, setValue] = useState('');
  const [state, setState] = useState('idle');
  const engine = useMemo(() => createMockEngine(), []);
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="rounded-lg border border-border bg-background p-2">
        <VoiceComposerSlot
          value={value}
          onChange={setValue}
          engine={engine}
          size={size}
          sounds={false}
          onStateChange={setState}
        />
      </div>
      <span className="font-mono text-[10px] text-muted-foreground">{state}</span>
    </div>
  );
}

export const RecordingStates: StoryObj = {
  render: () => <StatesShowcase />,
  parameters: {
    docs: {
      description: {
        story:
          'Recording feedback + state machine. Each slot reports its current `VoiceSlotState` via `onStateChange` below the button.',
      },
    },
  },
};
