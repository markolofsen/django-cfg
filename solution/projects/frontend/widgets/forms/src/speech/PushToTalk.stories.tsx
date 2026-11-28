import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  DictationButton,
  PushToTalkHint,
  useSpeechRecognition,
  usePushToTalk,
} from '.';

import { createMockEngine } from './_helpers/mockEngine';

type Args = {
  chord: string;
  enabled: boolean;
  showHint: boolean;
};

function PushToTalkDemo({ chord, enabled, showHint }: Args) {
  const engine = useMemo(() => createMockEngine({ partialIntervalMs: 80 }), []);
  const rec = useSpeechRecognition({ engine });
  usePushToTalk(rec, { key: chord, enabled });

  const [log, setLog] = useState<string[]>([]);

  return (
    <div className="flex w-[420px] flex-col gap-3 rounded-lg border border-border bg-background p-4">
      <div className="flex items-center gap-3">
        <DictationButton
          status={rec.status}
          onClick={() => void rec.toggle()}
        />
        <div className="flex flex-1 flex-col">
          <span className="text-xs text-muted-foreground">status</span>
          <span className="font-mono text-sm">{rec.status}</span>
        </div>
        {showHint && <PushToTalkHint chord={chord} />}
      </div>
      <textarea
        readOnly
        rows={3}
        value={rec.transcript.final}
        placeholder="Final transcript will appear here…"
        className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm"
      />
      <div className="text-xs text-muted-foreground">
        Hold the chord anywhere on the page (not while typing). Release to
        commit. Click the button below to log when you press.
      </div>
      <button
        type="button"
        onClick={() =>
          setLog((l) => [...l.slice(-4), `clicked at ${new Date().toLocaleTimeString()}`])
        }
        className="rounded-md border border-border px-2 py-1 text-xs hover:bg-muted"
      >
        log click
      </button>
      {log.length > 0 && (
        <pre className="rounded-md bg-muted/40 p-2 font-mono text-[11px] leading-snug">
          {log.join('\n')}
        </pre>
      )}
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Push to talk',
  component: PushToTalkDemo,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          '`usePushToTalk` — hold a chord to talk, release to commit. Skips keydown inside text fields unless the chord includes a modifier.',
      },
    },
  },
  argTypes: {
    chord: {
      control: 'select',
      options: ['alt', 'shift', 'ctrl', 'mod', 'mod+alt', 'mod+shift'],
      table: { category: 'Binding' },
    },
    enabled: { control: 'boolean', table: { category: 'Binding' } },
    showHint: { control: 'boolean', table: { category: 'Hint' } },
  },
  args: {
    chord: 'alt',
    enabled: true,
    showHint: true,
  },
} satisfies Meta<typeof PushToTalkDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const HoldAlt: Story = { args: { chord: 'alt', showHint: true } };

export const ModShift: Story = {
  args: { chord: 'mod+shift', showHint: true },
};

export const HintOnly: Story = {
  args: { enabled: false, showHint: true },
  parameters: {
    docs: {
      description: {
        story: 'Render `<PushToTalkHint>` standalone — no binding active.',
      },
    },
  },
};
