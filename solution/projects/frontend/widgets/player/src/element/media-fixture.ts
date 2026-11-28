/**
 * A real, playable media file built in memory, for stories that must PLAY.
 *
 * Stories cannot reach the network and a mock `src` never fires `timeupdate`,
 * so the one property this package is built on — that a portal move does not
 * interrupt playback — is unprovable against a fake. These bytes are a genuine
 * RIFF/WAVE file the browser decodes and plays.
 *
 * Silence, not a tone: the assertion is about the clock advancing, and a story
 * suite that makes noise on every run is one nobody runs twice.
 *
 * ## It does not play in every browser, and that is NOT this file's fault
 *
 * Measured: in some Chrome builds — automation and headless profiles among them
 * — a media element never leaves `readyState` 0 for ANY source, and reports
 * nothing while doing it: no `error` event, no rejected `play()`. The stories
 * then fail on the clock with no stated cause.
 *
 * Before changing these bytes, run the control that separates the two cases:
 *
 *   await new AudioContext().decodeAudioData(buffer)   // WebAudio, same bytes
 *
 * If WebAudio decodes them, the file is correct and the ELEMENT pipeline is the
 * problem — a different `bits`, `rate` or container will not help. That control
 * was run here: WebAudio accepted this exact WAV while every `<audio>` element,
 * a Blob URL, and a known-good MP3 all stalled identically. The suite's own
 * Playwright Chromium plays it.
 */

/** Seconds of audio. Long enough that a move lands mid-playback, not at the end. */
const SECONDS = 30;
const SAMPLE_RATE = 8000;

function writeAscii(view: DataView, offset: number, text: string): void {
  for (let i = 0; i < text.length; i += 1) view.setUint8(offset + i, text.charCodeAt(i));
}

/**
 * An 8-bit mono PCM WAV as a `data:` URL.
 *
 * 8-bit unsigned PCM puts silence at 128, not 0 — the buffer is zero-filled by
 * default, so the samples are written explicitly rather than left alone.
 */
export function silentWavDataUrl(seconds: number = SECONDS): string {
  const samples = SAMPLE_RATE * seconds;
  const buffer = new ArrayBuffer(44 + samples);
  const view = new DataView(buffer);

  writeAscii(view, 0, "RIFF");
  view.setUint32(4, 36 + samples, true);
  writeAscii(view, 8, "WAVE");
  writeAscii(view, 12, "fmt ");
  view.setUint32(16, 16, true); // PCM header size
  view.setUint16(20, 1, true); // format: PCM
  view.setUint16(22, 1, true); // channels: mono
  view.setUint32(24, SAMPLE_RATE, true);
  view.setUint32(28, SAMPLE_RATE, true); // byte rate = rate * channels * bytes
  view.setUint16(32, 1, true); // block align
  view.setUint16(34, 8, true); // bits per sample
  writeAscii(view, 36, "data");
  view.setUint32(40, samples, true);
  for (let i = 0; i < samples; i += 1) view.setUint8(44 + i, 128);

  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) binary += String.fromCharCode(bytes[i] as number);
  return `data:audio/wav;base64,${btoa(binary)}`;
}
