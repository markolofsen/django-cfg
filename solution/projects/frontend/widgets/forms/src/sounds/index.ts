/**
 * Bundled notification earcons, inlined as base64 data URLs so a consumer
 * needs no `.mp3` loader or ambient type shim.
 *
 * These live in `common/` rather than in the chat package because two
 * surfaces play them — chat notifications AND SpeechRecognition's dictation
 * earcons, which deliberately reuse the same tonal palette. Keeping them here
 * means the dictation widget does not have to import from chat, which was one
 * of the cycles the package split removed.
 *
 * To replace one: drop the mp3 next to this file, `base64 -i <file>.mp3`, and
 * paste the result into the matching module.
 */
export { default as sent } from './sent';
export { default as received } from './received';
export { default as start } from './start';
export { default as error } from './error';
export { default as mention } from './mention';
export { default as notification } from './notification';
