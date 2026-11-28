// Dictation: a state machine and ONE default engine. The language rule and its
// catalogue are shared with every other dictation surface: `@djangocfg/ui-core/lib/speech-language`.
//
// The package ships Web Speech as a default so a consumer gets a working
// microphone without wiring an external toolkit — audio never leaves the
// engine there. `VoiceCapability` remains the seam, so a host with a server
// transcriber, Whisper or a native bridge supplies its own and the default
// steps aside. Neither available means NO button, never a disabled one.
//
// This inverts the absent-is-absent rule for this one capability, deliberately:
// absent `voice` falls back to the browser rather than to nothing.
//
// MediaRecorder is NOT a fallback. It only produces audio, and turning that
// into text needs an endpoint — audio leaving the device, which is exactly the
// decision the seam exists to leave to the host.

export { createWebSpeechCapability, isWebSpeechAvailable } from "./web-speech";
export type { WebSpeechOptions } from "./web-speech";
export { VoiceSession } from "./session";
export type { VoiceSnapshot, VoiceSessionOptions } from "./session";
export { safeEarcon } from "./earcons";
export type { EarconKind, PlayEarcon, VoiceSoundsCapability } from "./earcons";
