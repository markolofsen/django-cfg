import type { Segment, Transcript } from '../types';

export const EMPTY_TRANSCRIPT: Transcript = {
  interim: '',
  final: '',
  segments: [],
};

export function joinFinal(segments: Segment[]): string {
  let out = '';
  for (const seg of segments) {
    if (!seg.isFinal) continue;
    const text = seg.text.trim();
    if (!text) continue;
    out = out ? `${out} ${text}` : text;
  }
  return out;
}

export function buildTranscript(segments: Segment[]): Transcript {
  const last = segments[segments.length - 1];
  const interim = last && !last.isFinal ? last.text : '';
  return {
    interim,
    final: joinFinal(segments),
    segments,
  };
}

/**
 * Polite text normalisation between concatenated finals — strips double
 * spaces / leading punctuation that some engines emit when the user pauses.
 */
export function normaliseFinal(text: string): string {
  return text.replace(/\s+/g, ' ').replace(/\s+([,.!?])/g, '$1').trim();
}
