import { useEffect, useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, waitFor, within } from 'storybook/test';

import { Textarea } from '@djangocfg/ui-core/components';
import {
  LanguageChip,
  LevelWave,
  useSpeechPrefs,
  VoiceComposerSlot,
  VoiceControlMenu,
} from '.';

import { createMockEngine } from './_helpers/mockEngine';

/**
 * The claude.ai-reference voice controls (voice-composer-rethink track,
 * 2026-08-03): the mic chevron menu (live meter · devices · language ·
 * hold-to-record), the in-recording language chip, and the rolling
 * level wave. Language visibility is the contract under test — the
 * "silently listened in the wrong language" failure class must stay
 * dead.
 */
const meta = {
  title: 'Widgets/Forms/Speech/Voice controls',
  component: VoiceControlMenu,
  tags: ['autodocs', 'contract'],
} satisfies Meta<typeof VoiceControlMenu>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Reset persisted prefs on mount so stories are order-independent. */
function usePrefsReset(): void {
  useState(() => {
    useSpeechPrefs.getState().reset();
    return null;
  });
}

function ControlMenuHost() {
  usePrefsReset();
  return (
    <div className="flex h-40 w-[420px] items-start justify-end p-4">
      <VoiceControlMenu />
    </div>
  );
}

export const ControlMenu: Story = {
  render: () => <ControlMenuHost />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByLabelText('Voice input options'));
    // Panel content portals to the body — search the whole screen.
    const screen = within(document.body);
    await waitFor(async () => {
      await expect(screen.getByText('Hold to record')).toBeVisible();
      await expect(screen.getByText('System default')).toBeVisible();
      await expect(screen.getByText('Language')).toBeVisible();
    });
    // THE regression this panel exists for: entering the language view
    // must keep the SAME popover open (the old menu→popover chain
    // dismissed both), and search works right there.
    await userEvent.click(screen.getByText('Language'));
    const search = await screen.findByPlaceholderText('Search language…');
    await userEvent.type(search, 'hecc');
    await waitFor(async () => {
      await expect(screen.getByText('Русский')).toBeVisible();
      await expect(screen.queryByText('Deutsch')).not.toBeInTheDocument();
    });
    // Picking closes the whole panel.
    await userEvent.click(screen.getByText('Русский'));
    await waitFor(async () => {
      await expect(
        screen.queryByPlaceholderText('Search language…'),
      ).not.toBeInTheDocument();
    });
  },
};

function LanguageChipHost() {
  usePrefsReset();
  return (
    <div className="flex h-64 w-[420px] items-start justify-end p-4">
      <LanguageChip />
    </div>
  );
}

export const LanguageChipMenu: Story = {
  render: () => <LanguageChipHost />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // The chip announces the ACTIVE language, not a generic mic label.
    const chip = canvas.getByLabelText(/^Recognition language:/);
    await userEvent.click(chip);
    const screen = within(document.body);
    await waitFor(async () => {
      // The Auto row shows what the resolver picked automatically.
      await expect(screen.getByText(/^Auto · /)).toBeVisible();
      await expect(screen.getByText('Русский')).toBeVisible();
    });
    // LAYOUT-INDEPENDENT search: "hecc" is «русс» typed on the EN
    // layout — it must find Русский and drop unrelated rows.
    const search = await screen.findByPlaceholderText('Search language…');
    await userEvent.type(search, 'hecc');
    await waitFor(async () => {
      await expect(screen.getByText('Русский')).toBeVisible();
      await expect(screen.queryByText('Deutsch')).not.toBeInTheDocument();
    });
  },
};

function WaveDemo() {
  const [level, setLevel] = useState(0.2);
  useEffect(() => {
    const id = window.setInterval(() => {
      setLevel(Math.abs(Math.sin(Date.now() / 300)) * 0.9);
    }, 120);
    return () => window.clearInterval(id);
  }, []);
  return (
    <div className="flex items-center gap-3 p-4 text-muted-foreground">
      <LevelWave level={level} active bars={24} height={16} />
      <span className="font-mono text-xs">{level.toFixed(2)}</span>
    </div>
  );
}

export const Wave: Story = {
  // Interval-driven animation — screenshots would flake in CI.
  tags: ['manual'],
  render: () => <WaveDemo />,
};

function RecordingSurfaceHost() {
  usePrefsReset();
  const [value, setValue] = useState('');
  const engine = useMemo(() => createMockEngine(), []);
  return (
    <div className="flex w-[560px] flex-col gap-3 p-4">
      <Textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Dictated text lands here"
        rows={3}
      />
      <div className="flex items-center justify-end gap-1.5">
        <VoiceComposerSlot value={value} onChange={setValue} engine={engine} />
      </div>
    </div>
  );
}

/**
 * Doubles as the regression test for the `usesMicrophone: false` contract.
 *
 * The Vitest run declares the environment microphone-less, and the mock is an
 * external engine, so the mic button below exists ONLY if `useVoiceSupport`
 * skips the `getUserMedia` gate for engines that capture outside the browser.
 * It did not until 2026-09-09, and this story went red the moment the
 * environment stopped pretending headless Chromium had a microphone.
 */
export const RecordingSurface: Story = {
  render: () => <RecordingSurfaceHost />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByLabelText('Dictate message'));
    await waitFor(async () => {
      // While listening the cluster exposes exactly two things: the
      // red stop-mic (same button, in place) and the ACTIVE
      // recognition language — the visibility contract.
      await expect(canvas.getByLabelText('Stop dictation')).toBeVisible();
      await expect(
        canvas.getByLabelText(/^Recognition language:/),
      ).toBeVisible();
    });
    // The mock engine streams partials into the textarea.
    await waitFor(async () => {
      const textarea =
        canvas.getByPlaceholderText<HTMLTextAreaElement>(
          'Dictated text lands here',
        );
      await expect(textarea.value.length).toBeGreaterThan(0);
    });
    // Esc discards: the composer rolls back to the pre-dictation anchor.
    await userEvent.keyboard('{Escape}');
    await waitFor(async () => {
      const textarea =
        canvas.getByPlaceholderText<HTMLTextAreaElement>(
          'Dictated text lands here',
        );
      await expect(textarea.value).toBe('');
    });
  },
};

export const LanguageSwitchMidRecording: Story = {
  render: () => <RecordingSurfaceHost />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByLabelText('Dictate message'));
    // English mock phrases stream in first.
    await waitFor(async () => {
      const textarea =
        canvas.getByPlaceholderText<HTMLTextAreaElement>(
          'Dictated text lands here',
        );
      await expect(textarea.value).toMatch(/[A-Za-z]/);
    });
    // Switch the language chip mid-recording. The engine must be torn
    // down and restarted with ru-RU (the restart waits for 'closed' —
    // the race that silently killed the session before 2026-08-03).
    await userEvent.click(canvas.getByLabelText(/^Recognition language:/));
    const screen = within(document.body);
    await userEvent.click(await screen.findByText('Русский'));
    await waitFor(
      async () => {
        const textarea =
          canvas.getByPlaceholderText<HTMLTextAreaElement>(
            'Dictated text lands here',
          );
        // The mock honours the session language: Cyrillic proves the
        // NEW session actually started in ru-RU.
        await expect(textarea.value).toMatch(/[А-Яа-яЁё]/);
      },
      { timeout: 5000 },
    );
  },
};
