/**
 * Default earcons for speech sessions. We reuse two of the bundled
 * shared notification sounds rather than ship new MP3s — same lazy chunk
 * already pays for them, and the tonal palette stays consistent across
 * the chat + dictation UI.
 *
 *  - `start` → the chat "stream start" chime (calm low-key tone).
 *  - `stop`  → the chat "sent" tick (2KB, very short — feels like
 *              "captured" rather than a notification ping).
 *    Previously used `notification.mp3` (30KB, long, loud) which was
 *    too attention-grabbing for a self-initiated action.
 *
 * Inlined as base64 data URLs in `common/sounds`, so consumers
 * get working audio with zero loader / ambient-type setup.
 */
import { start, sent } from '../../../sounds';

export type VoiceSoundEvent = 'start' | 'stop';

export const DEFAULT_VOICE_SOUNDS: Record<VoiceSoundEvent, string> = {
  start,
  stop: sent,
};
