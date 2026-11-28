import type { VoiceSoundsCapability } from '../../../../chat/core';

/**
 * The dictation tones, made with the Web Audio API: a rising pair when the microphone opens, a falling pair when it closes. No audio files ship and none
 * are fetched. A tone is quiet and short; a browser that has no `AudioContext`, or has not been unlocked by a gesture, plays nothing (the dictation starts from a click, so it is unlocked).
 */
const TONES: Readonly<Record<'start' | 'stop', readonly [number, number]>> = {
  start: [660, 880],
  stop: [880, 560],
};

const STEP = 0.07;
const GAIN = 0.06;

let context: AudioContext | null | undefined;

function audio(): AudioContext | null {
  if (context !== undefined) return context;
  const Ctor = typeof window === 'undefined' ? undefined : (window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext);
  context = Ctor ? new Ctor() : null;
  return context;
}

/** The bundled tones. Never throws: the session runs this on the path that opens the microphone. */
export const bundledEarcons: VoiceSoundsCapability = {
  play: (kind) => {
    try {
      const ctx = audio();
      if (!ctx) return;
      if (ctx.state === 'suspended') void ctx.resume();
      const [first, second] = TONES[kind];
      const now = ctx.currentTime;
      [first, second].forEach((frequency, index) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const at = now + index * STEP;
        osc.frequency.value = frequency;
        gain.gain.setValueAtTime(0, at);
        gain.gain.linearRampToValueAtTime(GAIN, at + 0.01);
        gain.gain.linearRampToValueAtTime(0, at + STEP);
        osc.connect(gain).connect(ctx.destination);
        osc.start(at);
        osc.stop(at + STEP + 0.02);
      });
    } catch {
      // A tone is a convenience.
    }
  },
};
