import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { DictationField } from '.';

import { createMockEngine } from './_helpers/mockEngine';

type Args = {
  placeholder?: string;
  rows: number;
  showInterim: boolean;
  showMeter: boolean;
  pushToTalk: boolean;
  pushToTalkKey: string;
  language: string;
  useMock: boolean;
};

function DictationWrap({
  placeholder,
  rows,
  showInterim,
  showMeter,
  pushToTalk,
  pushToTalkKey,
  language,
  useMock,
}: Args) {
  const [value, setValue] = useState('');
  // Toggling useMock rebuilds the engine cleanly.
  const engine = useMemo(
    () => (useMock ? createMockEngine() : undefined),
    [useMock],
  );

  return (
    <div className="w-[560px]">
      <DictationField
        value={value}
        onChange={setValue}
        placeholder={placeholder}
        rows={rows}
        showInterim={showInterim}
        showMeter={showMeter}
        engine={engine}
        language={language || undefined}
        pushToTalk={pushToTalk ? { key: pushToTalkKey } : undefined}
      />
      <p className="mt-3 text-xs text-muted-foreground">
        {useMock
          ? 'Mock engine — scripted partials, no microphone prompt.'
          : 'Real Web Speech API — Chrome/Edge/Safari only. Firefox and in-app browsers auto-hide the mic.'}
      </p>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Dictation',
  component: DictationWrap,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          '`DictationField` — opinionated textarea + mic button. Wires `useDictation` to a controlled `value`, supports push-to-talk, shows an interim transcript and an RMS meter.',
      },
    },
  },
  argTypes: {
    placeholder: { control: 'text', table: { category: 'Textarea' } },
    rows: {
      control: { type: 'number', min: 1, max: 10 },
      table: { category: 'Textarea' },
    },
    showInterim: { control: 'boolean', table: { category: 'Display' } },
    showMeter: { control: 'boolean', table: { category: 'Display' } },
    pushToTalk: { control: 'boolean', table: { category: 'PushToTalk' } },
    pushToTalkKey: {
      control: 'select',
      options: ['alt', 'shift', 'ctrl', 'mod', 'mod+alt'],
      table: { category: 'PushToTalk' },
    },
    language: {
      control: 'select',
      options: ['', 'en-US', 'en-GB', 'ru-RU', 'de-DE', 'fr-FR', 'ja-JP'],
      table: { category: 'Engine' },
    },
    useMock: { control: 'boolean', table: { category: 'Engine' } },
  },
  args: {
    placeholder: 'Type or press the mic to dictate…',
    rows: 3,
    showInterim: true,
    showMeter: true,
    pushToTalk: true,
    pushToTalkKey: 'alt',
    language: '',
    useMock: true,
  },
} satisfies Meta<typeof DictationWrap>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Drive every prop through Controls. */
export const Playground: Story = {};

/** Default appearance — interim ghost, meter, alt-to-talk. */
export const Default: Story = {
  args: {
    showInterim: true,
    showMeter: true,
    pushToTalk: true,
  },
};

/** Two rows, no chrome — suitable for sidebar composers. */
export const Compact: Story = {
  args: {
    rows: 2,
    showInterim: false,
    showMeter: false,
    pushToTalk: false,
  },
};

/** Real browser Web Speech API. Chrome / Edge / Safari only. */
export const BrowserNative: Story = {
  args: { useMock: false },
  parameters: {
    docs: {
      description: {
        story:
          'Talks to the actual browser STT. First mic click triggers a permission prompt; Firefox and in-app browsers will collapse the button.',
      },
    },
  },
};
