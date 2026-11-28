'use client';

import { useMemo, useRef, type ReactNode } from 'react';

import type { AttachmentsCapability, ChatSoundsCapability, ModelsCapability, VoiceSoundsCapability } from '../../../chat/core';
import { useSpeechLanguage } from '@djangocfg/ui-core/lib/speech-language';
import type { ChatStore } from '../../../chat/store';
import { Chat, ChatTranscript, AttachmentRenderer, DataRenderer, ReasoningRenderer, ToolRenderer } from '../../../chat/ui';
import { ChatProvider } from '../../../chat/store';
import { PartRegistryProvider, type PartRegistry, type PartRenderProps } from '../../../chat/primitives';
import { type ChatAdapter, type ChatCapabilities, type ChatMessage } from '../../../chat/core';
import { Response } from '../../../chat/content';

import { useAssistantLocale, type SessionNotice } from '../../../i18n/assistant';
import { bundledEarcons } from '../composer/dictation/earcons';
import { createWholeTranscriptSpeech } from '../composer/dictation/whole-transcript';
import { AssistantComposer } from '../composer/assistant-composer';
import { MessageFooter } from './message-footer';
import { NoticeLine } from './notice-line';

/** Draws one `data` part of a known `kind`. Return `undefined` to hand the part to the widget's own renderer. */
export type DataPartRenderer = (data: unknown, props: PartRenderProps) => ReactNode | undefined;

/** The dictation language the composer offers a picker for: a BCP-47 tag the host remembers. */
export interface SpeechLanguage {
  value: string;
  onChange: (language: string) => void;
}

interface Props {
  adapter: ChatAdapter;
  /** The starter rows of an empty chat: a prompt, or `{ prompt, icon }` with an icon key (`SUGGESTION_ICON_KEYS`). Absent: none. */
  suggestions?: (string | { prompt: string; icon?: string })[];
  /**
   * A transcript the host feeds itself (a call's polled lines arrive with `store.receive`). With it the chat does not seed or reset the transcript from `conversation`; the adapter and the
   * store are the host's. Absent: the chat owns its store (the assistant's session).
   */
  store?: ChatStore;
  /** Capabilities added to the assistant's own, which they win over: `mentions`, `recipients`, `authors`, or `voice: false` / `sounds: false` for a host with no dictation. */
  capabilities?: ChatCapabilities;
  /** Part renderers added to the assistant's own (`text`, `data`, `attachment`, `reasoning`, `tool`), which they win over: a call draws a person's line with its `@` mentions picked out. */
  renderers?: PartRegistry;
  /** An extra row under each message, below the copy action and the time (a private-line note, a reply's progress, Retry). */
  footer?: (message: ChatMessage) => ReactNode;
  /** The composer's shape: `compact` is the phone-sized one (one row, no ring, Enter is a newline on touch); absent, the stacked field with its controls beneath. */
  composer?: { compact?: boolean };
  /** A viewer who cannot post: this replaces the composer. */
  readOnly?: ReactNode;
  /** What the empty room shows above the starter rows: `<AssistantGreeting title="…" mark={…} />`, or any node. Absent: the widget's plain empty line. */
  greeting?: ReactNode;
  /** The room on screen: `id` changes when the thread is reloaded (reconcile, a new or another session), which reseeds the transcript. */
  conversation?: { id?: string; history: readonly ChatMessage[] };
  /** What the unsent draft is kept under: the session's own id, so each session keeps its draft across reseeds. Absent: the conversation `id`. */
  draftRoom?: string;
  /** The host's drawing of structured parts, by `kind` (for example `citations`). Unknown kinds fall through to the widget. */
  dataRenderers?: Readonly<Record<string, DataPartRenderer>>;
  /** Dictation language and its picker (the microphone menu). Absent: the assistant's own picker (the viewer's last pick, else the page and browser language), always shown. */
  speech?: SpeechLanguage;
  /** Attach files: which kinds, how large, how many, and the `upload` that stores them. Absent: no attach button (a host that cannot store files shows none). The same object as `capabilities.attachments`, which it is merged into. */
  attachments?: AttachmentsCapability;
  /** A model switch in the composer: the options (see `useModelAliases`), the chosen id and its setter. Absent: no switch, and no `model` in the request. */
  models?: ModelsCapability;
  /** The dictation start/stop tones. Absent: the bundled ones (Web Audio, no files). `false`: silent. */
  sounds?: VoiceSoundsCapability | false;
  /** The message sounds (sent, answer starts, answer done, error). Absent: the widget's bundled ones, on. `false`: silent. */
  messageSounds?: ChatSoundsCapability | false;
  /** A plain line above the composer: reconnecting, or a stalled run with its Retry (`onRetry`). */
  notice?: SessionNotice | null;
  onRetry?: () => void;
  /** Raise to put the caret in the field (the panel was just opened on a device with a keyboard). Not applied on first render. */
  focusWhen?: boolean;
  /** A keyboard device: after a send the caret goes back to the field (to the microphone when the send ended a dictation). */
  refocus?: boolean;
  className?: string;
}

const EMPTY_ROOM = { history: [] } as const;
const NO_RENDERERS: Readonly<Record<string, DataPartRenderer>> = {};
const NO_SUGGESTIONS: NonNullable<Props['suggestions']> = [];

/**
 * The chat: the framework widget with markdown text, the host's structured parts, message actions, and the full composer (dictation with its language menu,
 * recall of sent prompts with the arrow keys, an unsent draft that survives a reload). The widget's packaged layout shows only a bare composer, so the layout
 * is composed here from its own primitives: every behaviour is the widget's, nothing is re-implemented.
 */
export function AssistantChat({ adapter, suggestions = NO_SUGGESTIONS, store, capabilities: extra, renderers: hostRenderers, footer, composer: shape, readOnly, greeting, conversation = EMPTY_ROOM, draftRoom, dataRenderers = NO_RENDERERS, speech: given, attachments, models, sounds, messageSounds, notice, onRetry, focusWhen, refocus, className }: Props) {
  const renderers = useMemo<PartRegistry>(
    () => ({
      text: ({ part }: PartRenderProps) => (part.type === 'text' ? <Response>{part.text}</Response> : null),
      data: (props: PartRenderProps) => {
        const { part } = props;
        if (part.type === 'data') {
          const drawn = dataRenderers[part.kind]?.(part.data, props);
          if (drawn !== undefined) return drawn;
        }
        return DataRenderer(props);
      },
      attachment: AttachmentRenderer,
      // Drawn by default: a thought or a tool call that reaches the transcript (a trace step, a host adapter's chunk) must not be silent.
      reasoning: ReasoningRenderer,
      tool: ToolRenderer,
      ...hostRenderers,
    }),
    [dataRenderers, hostRenderers],
  );
  const own = useSpeechLanguage({ uiLocale: useAssistantLocale() });
  const speech = given ?? { value: own.language, onChange: own.setLanguage };
  // The language is read at each start, through a ref: the capability must not be rebuilt when the picker changes.
  const language = useRef(speech?.value);
  language.current = speech?.value;
  const voice = useMemo(() => createWholeTranscriptSpeech(() => language.current ?? (typeof navigator === 'undefined' ? 'en-US' : navigator.language)), []);
  const capabilities = useMemo<ChatCapabilities>(
    () => ({
      ...(suggestions.length === 0 ? {} : { suggestions: { items: suggestions.map((row, index) => { const item = typeof row === 'string' ? { prompt: row } : row; return { id: `s${index}`, title: item.prompt, prompt: item.prompt, ...('icon' in item && item.icon ? { icon: item.icon } : {}) }; }) } }),
      ...(voice ? { voice } : {}),
      ...(sounds === false ? {} : { voiceSounds: sounds ?? bundledEarcons }),
      ...(messageSounds === undefined ? {} : { sounds: messageSounds }),
      ...(attachments === undefined ? {} : { attachments }),
      ...(models === undefined ? {} : { models }),
      ...extra,
    }),
    [suggestions, voice, sounds, messageSounds, attachments, models, extra],
  );
  const slots = useMemo(
    () => ({
      // Progress while a run streams is the widget's own pending row inside the transcript; a second line under the composer repeated it and
      // moved the input. Only a rare notice (reconnecting, stalled) uses this slot.
      footer: (
        <>
          {notice ? <NoticeLine notice={notice} onRetry={onRetry} /> : null}
        </>
      ),
    }),
    [notice, onRetry],
  );
  const frame = `assistant-chat flex h-full min-h-0 flex-col ${className ?? ''}`;
  const body = (
    <>
      <ChatTranscript {...(greeting === undefined ? {} : { empty: greeting })} footer={(message) => <MessageFooter message={message}>{footer?.(message)}</MessageFooter>} />
      {readOnly ?? <AssistantComposer speech={speech} draftRoom={draftRoom ?? conversation.id ?? 'assistant'} focusWhen={focusWhen} refocus={refocus} compact={shape?.compact} />}
    </>
  );
  // A host-fed transcript: no seeding from `conversation` (it would wipe the lines the host has received), so the providers are mounted here. The box is the one `<Chat>` draws.
  if (store) {
    return (
      <ChatProvider adapter={adapter} store={store} capabilities={capabilities}>
        <PartRegistryProvider renderers={renderers}>
          <div className={`relative ${frame}`}>
            {body}
            {slots.footer}
          </div>
        </PartRegistryProvider>
      </ChatProvider>
    );
  }
  return <Chat adapter={adapter} capabilities={capabilities} renderers={renderers} conversation={conversation} slots={slots} className={frame} body={{ kind: 'custom', children: body }} />;
}
