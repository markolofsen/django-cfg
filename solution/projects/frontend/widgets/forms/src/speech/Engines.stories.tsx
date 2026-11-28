import { useEffect, useMemo, useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  DictationButton,
  ErrorBanner,
  createExternalEngine,
  createHttpEngine,
  createWebSocketEngine,
  createWebSpeechEngine,
  useSpeechRecognition,
  type ExternalEngineHandle,
  type RecognitionEngine,
  type RecognitionError,
} from '.';

import { createMockEngine } from './_helpers/mockEngine';

type EngineKind = 'webspeech' | 'http' | 'websocket' | 'external' | 'mock';

type Args = {
  engine: EngineKind;
  catchErrors: boolean;
};

function EnginePanel({ engine: kind, catchErrors }: Args) {
  const externalHandleRef = useRef<ExternalEngineHandle | null>(null);
  const [error, setError] = useState<RecognitionError | null>(null);

  const engine = useMemo<RecognitionEngine | undefined>(() => {
    setError(null);
    switch (kind) {
      case 'webspeech':
        return createWebSpeechEngine();
      case 'http':
        // Dummy endpoint — `start()` will fail when MediaRecorder tries to
        // POST. We surface that to <ErrorBanner> via onError below.
        return createHttpEngine({
          url: 'https://example.invalid/stt',
          chunkMs: 750,
          parse: async () => null,
        });
      case 'websocket':
        return createWebSocketEngine({
          url: 'wss://example.invalid/listen',
          chunkMs: 250,
          parseMessage: () => ({ kind: 'ignore' }),
        });
      case 'external':
        return createExternalEngine({
          id: 'manual-feeder',
          supported: true,
          onStart: () => undefined,
          onStop: () => undefined,
          subscribe: (handle) => {
            externalHandleRef.current = handle;
            handle.markListening();
            return () => {
              externalHandleRef.current = null;
            };
          },
        });
      case 'mock':
      default:
        return createMockEngine();
    }
  }, [kind]);

  const rec = useSpeechRecognition({
    engine,
    onError: (e) => {
      if (catchErrors) setError(e);
    },
  });

  // Reset any banner when the user toggles engine.
  useEffect(() => {
    setError(null);
  }, [kind]);

  const showFeeder = kind === 'external';

  return (
    <div className="flex w-[520px] flex-col gap-3 rounded-lg border border-border bg-background p-4 text-sm">
      <div className="flex items-center gap-3">
        <DictationButton
          status={rec.status}
          onClick={() => void rec.toggle()}
          isSupported={engine?.isSupported ?? false}
        />
        <div className="flex flex-1 flex-col">
          <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
            engine
          </span>
          <span className="font-mono text-xs">
            {engine?.id ?? 'none'} · supported={String(engine?.isSupported ?? false)}
          </span>
        </div>
        <span className="rounded-md border border-border px-2 py-1 font-mono text-[11px]">
          {rec.status}
        </span>
      </div>
      {error && <ErrorBanner error={error} onDismiss={() => setError(null)} />}
      <textarea
        readOnly
        rows={3}
        value={rec.transcript.final + (rec.transcript.interim ? ` ${rec.transcript.interim}` : '')}
        placeholder="Transcript will appear here…"
        className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm"
      />
      {showFeeder && (
        <div className="flex flex-wrap gap-2 rounded-md border border-dashed border-border p-2">
          <span className="w-full text-[11px] uppercase tracking-wide text-muted-foreground">
            external feeder
          </span>
          <button
            type="button"
            onClick={() =>
              externalHandleRef.current?.emitPartial('typing live partial…')
            }
            className="rounded-md border border-border px-2 py-1 text-xs hover:bg-muted"
          >
            emit partial
          </button>
          <button
            type="button"
            onClick={() => externalHandleRef.current?.emitFinal('Hello from the host.')}
            className="rounded-md border border-border px-2 py-1 text-xs hover:bg-muted"
          >
            emit final
          </button>
          <button
            type="button"
            onClick={() =>
              externalHandleRef.current?.emitError({
                code: 'engine',
                message: 'Manual error from host',
              })
            }
            className="rounded-md border border-border px-2 py-1 text-xs hover:bg-muted"
          >
            emit error
          </button>
        </div>
      )}
      <p className="text-xs text-muted-foreground">
        {kind === 'http' || kind === 'websocket'
          ? 'Dummy endpoint — pressing the mic will likely surface a network/engine error. Set onError in your real integration to display a banner like the one above.'
          : kind === 'webspeech'
            ? 'Real Web Speech API. Chrome/Edge/Safari only; the mic prompt will appear on first click.'
            : kind === 'external'
              ? 'External engine — frontend never owns audio. Use the buttons above to simulate host events (Wails / Tauri / native sidecar).'
              : 'Deterministic mock — no microphone, no network.'}
      </p>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Engines',
  component: EnginePanel,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Plug `createWebSpeechEngine` / `createHttpEngine` / `createWebSocketEngine` / `createExternalEngine` into `useSpeechRecognition`. HTTP and WebSocket stories use dummy URLs — set an `onError` handler in production to display fallbacks.',
      },
    },
  },
  argTypes: {
    engine: {
      control: 'inline-radio',
      options: ['webspeech', 'http', 'websocket', 'external', 'mock'],
      table: { category: 'Engine' },
    },
    catchErrors: { control: 'boolean', table: { category: 'Engine' } },
  },
  args: { engine: 'mock', catchErrors: true },
} satisfies Meta<typeof EnginePanel>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const WebSpeech: Story = {
  args: { engine: 'webspeech' },
  parameters: {
    docs: {
      description: {
        story:
          'Default browser engine. `isSupported` is `false` in Firefox / in-app WebViews — `DictationButton` disables itself automatically.',
      },
    },
  },
};

export const Http: Story = {
  args: { engine: 'http' },
  parameters: {
    docs: {
      description: {
        story:
          '`createHttpEngine` posts MediaRecorder chunks to your endpoint. Story uses a dummy URL — pressing the mic surfaces an engine error through `<ErrorBanner>`.',
      },
    },
  },
};

export const WebSocket: Story = {
  args: { engine: 'websocket' },
  parameters: {
    docs: {
      description: {
        story:
          '`createWebSocketEngine` opens a persistent connection. Dummy URL — connection fails immediately so you can see the error path.',
      },
    },
  },
};

export const External: Story = {
  args: { engine: 'external' },
  parameters: {
    docs: {
      description: {
        story:
          '`createExternalEngine` for backends that own capture and transcription (Wails / Tauri / native sidecar). Use the feeder buttons to simulate host events.',
      },
    },
  },
};

export const Mock: Story = {
  args: { engine: 'mock' },
  parameters: {
    docs: {
      description: {
        story:
          'Deterministic mock — scripted partials / finals. Used everywhere CI must avoid microphone prompts.',
      },
    },
  },
};
