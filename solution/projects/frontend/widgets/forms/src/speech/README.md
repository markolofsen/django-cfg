# SpeechRecognition

Decomposed Speech-to-Text for the React app. **Headless core + composable UI parts + lazy bundle**, just like [`Chat`](../Chat) and [`AudioPlayer`](../AudioPlayer).

The default backend is the browser's native Web Speech API (zero deps, zero network). For anything else — Deepgram, AssemblyAI, OpenAI Whisper, your own Django/FastAPI gateway — plug a custom engine into the same hook. No SDK lock-in.

```bash
pnpm add @djangocfg/ui-tools
```

Subpath import (recommended — keeps the rest of `ui-tools` out of your bundle):

```ts
import {
  useSpeechRecognition,
  DictationField,
  createWebSpeechEngine,
  createHttpEngine,
  createWebSocketEngine,
} from '@djangocfg/ui-tools/speech-recognition';
```

---

## Quick start

```tsx
import {
  DictationButton,
  TranscriptView,
  useSpeechRecognition,
} from '@djangocfg/ui-tools/speech-recognition';

function Dictate() {
  const rec = useSpeechRecognition();         // Web Speech engine, browser language
  return (
    <div className="flex items-start gap-3">
      <DictationButton status={rec.status} onClick={() => rec.toggle()} />
      <TranscriptView transcript={rec.transcript} />
    </div>
  );
}
```

That's the whole "make me type with my voice" flow. With no config, the hook uses `createWebSpeechEngine()` and the shared dictation language (`useSpeechLanguage` from `@djangocfg/ui-core/lib/speech-language`; with no pick it is guessed from `navigator.languages`).

---

## DictationField — the opinionated widget

A textarea + mic button + interim ghost + push-to-talk hint, all wired up. Final segments are appended to the controlled `value`.

```tsx
import { DictationField } from '@djangocfg/ui-tools/speech-recognition';

const [text, setText] = useState('');

<DictationField
  value={text}
  onChange={setText}
  language="ru-RU"
  pushToTalk={{ key: 'alt' }}
  placeholder="Type or hold ⌥ to talk…"
/>
```

For voice-memo flows there's `VoiceMessageRecorder`: press the mic, dictate freely, silence-detection or 60-second cap triggers `onSubmit(text, segments)`.

---

## Custom engines — the whole point

`useSpeechRecognition` doesn't care **how** audio becomes text. The `RecognitionEngine` interface is small enough to implement against any backend.

### HTTP (Whisper, custom REST)

```ts
import { createHttpEngine } from '@djangocfg/ui-tools/speech-recognition';

const engine = createHttpEngine({
  url: '/api/stt/transcribe',
  headers: async () => ({ Authorization: `Bearer ${token}` }),
  chunkMs: 750,
  parse: async (resp) => {
    const { text, final } = await resp.json();
    return { text, isFinal: final };
  },
});

const rec = useSpeechRecognition({ engine });
```

Captures audio with `MediaRecorder` (Opus/WebM by default), POSTs each chunk as the request body, runs your `parse` callback on the response.

### External (Wails / Tauri / native sidecar)

When the host owns the entire pipeline — capture happens outside the browser, transcription runs on the backend, the frontend just commands "start" / "stop" — use `createExternalEngine`. Perfect for cmdop's Wails whisper.cpp integration.

```ts
import { createExternalEngine } from '@djangocfg/ui-tools/speech-recognition';
import { EventsOn } from '@runtime';
import * as VoiceService from '@bindings/desktop/services/voice/service';

const wailsEngine = createExternalEngine({
  id: 'wails-whisper',
  onStart: () => VoiceService.StartRecordingForChat(),
  onStop: () => VoiceService.StopRecordingForChat(),
  subscribe: (handle) => {
    const offText = EventsOn('voice:chat-text', (p) => {
      if (p?.error) handle.emitError({ code: 'engine', message: p.error });
      else if (p?.text) handle.emitFinal(p.text);
      else handle.emitError({ code: 'no-speech', message: '' });
    });
    const offState = EventsOn('voice:state', (s) => {
      if (s.state === 'recording' || s.state === 'streaming') handle.markListening();
      if (s.partial) handle.emitPartial(s.partial);
    });
    return () => { offText(); offState(); };
  },
});

<VoiceComposerSlot engine={wailsEngine} value={composer.value} onChange={composer.setValue} />
```

No `MediaRecorder` / `getUserMedia` — the engine is purely a translator between the chat UI and your event bus. `emitFinal` automatically closes the session, so the composer reset / autosend logic fires the moment the backend posts a result.

### WebSocket (Deepgram / AssemblyAI / custom realtime)

```ts
import { createWebSocketEngine } from '@djangocfg/ui-tools/speech-recognition';

const engine = createWebSocketEngine({
  url: async () => {
    const { token } = await fetch('/api/stt/ticket').then((r) => r.json());
    return `wss://stt.example.com/listen?token=${token}`;
  },
  chunkMs: 250,
  parseMessage: (data) => {
    if (typeof data !== 'string') return { kind: 'ignore' };
    const msg = JSON.parse(data);
    if (msg.type === 'Results') {
      return msg.is_final
        ? { kind: 'final', text: msg.channel.alternatives[0].transcript }
        : { kind: 'partial', text: msg.channel.alternatives[0].transcript };
    }
    return { kind: 'ignore' };
  },
});
```

Reconnect with exponential backoff (250 ms → 5 s) is built in. Tokens go through a `url()` callback so they can be minted server-side and rotated per session.

### Anything else

Implement `RecognitionEngine` directly — on-device Whisper WASM, Picovoice, native bridges from Tauri / Electron, mocked engines for tests. The interface:

```ts
interface RecognitionEngine {
  id: string;
  isSupported: boolean;
  start(opts: EngineStartOptions): Promise<void>;
  stop(): Promise<void>;
  abort(): void;
  on(event, cb): Unsub;            // 'partial' | 'final' | 'error' | 'state'
  getStream?(): MediaStream | null; // optional — for VU meters
}
```

`createEngineBus()` gives you the listener bookkeeping in three lines.

---

## Voice inside the Chat composer

Two drop-ins, designed to live together:

```tsx
import { ChatRoot } from '@djangocfg/ui-tools/chat';
import {
  ChatHeaderLanguageButton,
  VoiceComposerSlot,
} from '@djangocfg/ui-tools/speech-recognition';

<ChatRoot
  transport={transport}
  composerBlockStart={<VoiceComposerSlot />}
/>

// Header flag-picker is added via ChatLauncher dock slot:
<ChatLauncher dock={{ headerActions: <ChatHeaderLanguageButton /> }}>
```

That's it. No props, no refs. The slot reads / writes the composer through the `ComposerHandle` registered in `ChatProvider` (`focus / moveCursorToEnd / getValue / setValue`), so the built-in `<Composer>` and a TipTap-backed `MarkdownEditor` work the same way — host implements `useRegisterComposer({...})` once and voice flows in.

What you get without writing it yourself:

- **Anchored merge.** The text typed before pressing the mic is preserved; dictation is appended to that anchor.
- **Live focus + cursor pinning.** On start, the composer is focused and the caret jumps to end; every partial / final repins the caret so the live transcript visibly grows where the user expects.
- **Auto-hide.** `useVoiceSupport()` checks `engine.isSupported` + `getUserMedia` + browser type (Firefox / Instagram / TikTok WebViews → renders `null`).
- **Countdown chip + tooltip.** A `useCountdownFromSeconds()` ticker (max 90 s default) sits next to the mic button.
- **Silence stop.** Auto-stop after 2.5 s of quiet (configurable via `silenceMs`).
- **Esc / Enter hotkeys while listening.** Esc cancels (and `stopPropagation` so the chat doesn't close), Enter finishes recording (and **does not** submit the chat — avoids accidental sends mid-sentence).
- **Earcons.** Bundled start (low chime) + stop (short tick) reused from chat sounds, both at deliberately quiet volumes. Override via `sounds={{ start, stop }}` or disable with `sounds={false}`.

The explicit `value` / `onChange` form is still supported for standalone usage outside a `<ChatProvider>`:

```tsx
<VoiceComposerSlot value={value} onChange={setValue} />
```

### Language picker — flag button in the chat header

```tsx
<ChatHeader actions={<ChatHeaderLanguageButton />} />
```

Compact 28×28 flag button. Shows the currently-resolved language's country flag (🇷🇺 for `ru-RU`, 🇺🇸 for `en-US`). Clicking opens a searchable `<Combobox>` with **66 BCP-47 tags from the official Chrome Web Speech demo** (`WEB_SPEECH_LANGUAGES` catalogue) — language name + region + tag, every row with a country flag, search across all three fields. The choice is the one shared with every chat on the page (`useSpeechLanguage`).

### Shared state across the tree

Need to react to listening state elsewhere (dim textarea, header indicator)? Wrap the chat in `<SpeechRecognitionProvider>` and read `useSpeechRecognitionContext()` from any descendant.

### Reading the active language from elsewhere

Speech language is **one value for the whole product**, independent of the app's i18n locale: `cfg.chat.speech_language` in localStorage, read through `useLocalStorage`, so a change in a chat, a field or another tab reaches all of them at once. It lives in `@djangocfg/ui-core/lib/speech-language` (`useSpeechLanguage`, the catalogue `WEB_SPEECH_LANGUAGES`, `toSpeechTag`, `resolveLanguage`), not in this package. Read it from any component:

```tsx
import {
  useSpeechPrefs,            // raw user choice — `string | null`
  useResolvedLanguage,       // resolved BCP-47 with full fallback chain
  useSpeechLanguageInfo,     // combo: { tag, iso, country, name, englishName, region, hasUserChoice }
} from '@djangocfg/ui-tools/speech-recognition';

function HeaderBadge() {
  const { tag, name, country, hasUserChoice } = useSpeechLanguageInfo();
  return (
    <Badge>
      <Flag countryCode={country} />
      {name ?? tag}
      {hasUserChoice && <span className="ml-1">★</span>}
    </Badge>
  );
}
```

Push to backend on every change:

```tsx
const { tag, hasUserChoice } = useSpeechLanguageInfo();
useEffect(() => {
  if (!hasUserChoice) return;
  void api.user.update({ speechLanguage: tag });
}, [tag, hasUserChoice]);
```

Outside React (event handlers, util functions, non-component code):

```ts
import { useSpeechPrefs } from '@djangocfg/ui-tools/speech-recognition';
const current = useSpeechPrefs.getState().language;          // 'ru-RU' | null
const unsubscribe = useSpeechPrefs.subscribe((state) => {
  console.log('language changed', state.language);
});
```

---

## What you get for free

- **Zero-setup default** — `useSpeechRecognition()` works with no engine, no config.
- **Permission-aware UX** — `permission-denied` / `no-microphone` / `no-speech` surface as typed errors; `<ErrorBanner>` translates them.
- **Persisted prefs** — mic device, engine choice live in zustand+localStorage (`cfg.forms.speech_prefs`).
- **Auto-stop** — `autoStop: { silenceMs, maxMs, silenceThreshold }` based on RMS analyser; opt-in.
- **Push-to-talk** — `usePushToTalk({ key: 'mod+alt' })` with smart input-field bypass.
- **VU meter** — `useMicLevel(stream)` + `<MicMeter />` for level visualisation.
- **Mic enumeration** — `useMicDevices()` returns `audioinput` list, refreshes on `devicechange`.
- **Interim+final UI** — `<TranscriptView>` dims the trailing interim chunk so users see the model "thinking".

---

## Debug logger

Scoped, namespaced [consola](https://github.com/unjs/consola) wrapper that silences itself in production by default. Mirrors `getChatLogger()` in the Chat tool so both surfaces feel the same in DevTools.

```ts
import { getSpeechLogger } from '@djangocfg/ui-tools/speech-recognition';

const log = getSpeechLogger();
log.dictation.info('final merged', { len: 42 });
log.engine.debug('state', 'listening');
log.error.error('engine threw', err);
```

Sub-loggers: `engine`, `dictation`, `slot`, `composer`, `mic`, `push`, `error`. `error` always emits; everything else is gated.

**Opt-in (any one is enough):**

1. **Dev mode** — `NODE_ENV === 'development'` auto-enables everything.
2. **Runtime toggle** — paste this in DevTools to enable without a rebuild:
   ```js
   localStorage.setItem('cfg.forms.speech_debug', '1');
   location.reload();
   ```
   `'0'` (or `removeItem`) turns it back off.
3. **Explicit** — `getSpeechLogger(true)` from a host component (analogous to `<ChatRoot debug />`).

**What you'll see when on**, in order of a typical dictation session:

```
[speech][slot] mount { supported: true, hasComposerHandle: true, … }
[speech][engine] subscribe { engineId: 'webspeech' }
[speech][engine] state 'listening'
[speech][engine] partial { len: 6, segmentId: 's1' }
[speech][composer] setValue → composer handle { len: 12 }
[speech][engine] final { len: 42, confidence: 0.91 }
[speech][dictation] final merged { len: 42, totalLen: 54 }
[speech][engine] autoStop silence detected
[speech][engine] state 'closed'
```

If text never appears in your composer, look for:

- `[speech][slot] mount { hasComposerHandle: false, … }` → `<VoiceComposerSlot>` is outside a `<ChatProvider>` and no `value`/`onChange` props were given — text is going nowhere.
- `[speech][composer] warn setValue called but no composer handle is registered …` → the composer never called `useRegisterComposer(...)`. Built-in `<Composer>` and `MarkdownEditor` do this automatically; custom composers must opt in.
- `[speech][engine] final` arrives but no `[speech][dictation] final merged` follows → check `normaliseFinal` filtered the text (empty / whitespace only).

---

## Public surface

### Hooks
`useSpeechRecognition`, `useDictation`, `usePushToTalk`, `useMicDevices`, `useMicLevel`, `useEnginePrefs`, `useSpeechPrefs`, `useVoiceSupport`, `useResolvedLanguage`, `useSpeechLanguageInfo`.

### Context
`SpeechRecognitionProvider`, `useSpeechRecognitionContext`, `useSpeechRecognitionContextOptional` — lift a single engine instance so any descendant (composer slot, header badge, transcript overlay) sees the same `status` / `transcript` / `level`.

### Components
`DictationButton`, `MicMeter`, `TranscriptView`, `LanguagePicker`, `DevicePicker`, `EngineBadge`, `ErrorBanner`, `PushToTalkHint`. Chat header: `ChatHeaderLanguageButton` (re-exported from chat launcher).

### Widgets
`DictationField`, `VoiceMessageRecorder`, `VoiceComposerSlot`, `LazyDictationField`.

### Engines
`createWebSpeechEngine`, `createHttpEngine`, `createWebSocketEngine`, `createExternalEngine`, `createEngineBus`, `startMicCapture`, `pickMime`.

### Language utilities
`DEFAULT_VOICE_SOUNDS`. The language catalogue and rule (`WEB_SPEECH_LANGUAGES`, `findSpeechLanguage`, `toSpeechTag`, `resolveLanguage`, `useSpeechLanguage`) moved to `@djangocfg/ui-core/lib/speech-language` and are no longer exported here.

### Types
`RecognitionEngine`, `RecognitionStatus`, `RecognitionError`, `RecognitionErrorCode`, `Segment`, `Transcript`, `EngineState`, `EngineStartOptions`, `EngineEventMap`, `Unsub`, `AutoStopOptions`, `VoiceSupport`, `VoiceUnsupportedReason`.

---

## Tests

```bash
pnpm test         # one-shot
pnpm test:watch   # vitest watch mode
```

Covered (12 cases, all pure-function): reducer state machine (`__tests__/reducer.test.ts`), transcript merge + `normaliseFinal` (`__tests__/transcript.test.ts`), `newSegmentId` (`__tests__/ids.test.ts`). Engine adapters and UI parts rely on stories — `MediaRecorder` / `getUserMedia` / `WebSocket` are mock-engine-driven in the playground.

---

## Stories

`Tools/SpeechRecognition/{Basic, DictationField, PushToTalk, MicMeter, CustomEngine: HTTP, CustomEngine: WebSocket, Language & Device, Errors}` plus `Tools/Chat/Voice composer` for the chat-slot integration — all driven by a deterministic mock engine so the playground never asks for microphone permission.

```bash
pnpm playground
```

---

## Browser support

| Browser | Default engine | Notes |
|---|---|---|
| Chrome / Edge desktop | ✅ Web Speech | Best — continuous + interim results. |
| Safari 16+ desktop | ✅ Web Speech | Continuous works; some locales partial only. |
| Firefox desktop | ❌ Web Speech | `isSupported === false`. Pass a custom engine (HTTP/WS). |
| Mobile WebViews | ⚠️ varies | Always pair with a fallback engine in production. |

For Firefox / WebView consumers: pass `engine: createHttpEngine(...)` and you're streaming again.
