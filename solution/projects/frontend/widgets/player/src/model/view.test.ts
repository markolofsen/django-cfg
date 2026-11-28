import { describe, expect, it } from "vitest";
import type { MediaTrack } from "../domain";

import { canOpenStage, playedFraction } from "./view";
import { failureText } from "./failure-text";
import { en } from "../i18n/locales/en";

const AUDIO: MediaTrack = { id: "a", kind: "audio", src: "s", title: "t" };
const VIDEO: MediaTrack = { ...AUDIO, kind: "video" };

describe("playedFraction", () => {
  it("reports the fraction played", () => {
    expect(playedFraction(30, 120)).toBe(0.25);
  });

  it("reports zero before the duration is known", () => {
    // The real pre-metadata value. A bare division would render `Infinity`.
    expect(playedFraction(0, 0)).toBe(0);
    expect(playedFraction(5, 0)).toBe(0);
  });

  it("reports zero for a stream of unknown length", () => {
    // MUTANT: drop the `isFinite` guard → this returns NaN, and a bar styled
    // with `width: NaN%` silently keeps its previous width.
    expect(playedFraction(5, Number.NaN)).toBe(0);
    expect(playedFraction(5, Number.POSITIVE_INFINITY)).toBe(0);
  });

  it("clamps a position past the end", () => {
    // Media elements report a currentTime a hair past duration at the end.
    expect(playedFraction(121, 120)).toBe(1);
    expect(playedFraction(-1, 120)).toBe(0);
  });
});

describe("canOpenStage", () => {
  it("offers the stage for something with a picture", () => {
    expect(canOpenStage(VIDEO)).toBe(true);
  });

  it("does not offer it for audio", () => {
    // A full screen of audio is a worse view of what the dock already shows.
    expect(canOpenStage(AUDIO)).toBe(false);
  });
});

describe("failureText", () => {
  it("names the machine when the track carries one", () => {
    expect(failureText({ reason: "machine-unreachable", machineId: "srv" }, en.failure))
      .toBe("srv went offline — playback stopped");
  });

  it("says the same thing without a name when there is none", () => {
    // The placeholder must not survive as literal `{{machine}}` on screen.
    const text = failureText({ reason: "machine-unreachable" }, en.failure);
    expect(text).not.toContain("{{");
    expect(text).toBe(en.failure.machineUnreachableUnnamed);
  });

  it("asks for a click rather than reporting a fault when blocked", () => {
    // The one failure that is not a fault. It must not read like the others.
    const text = failureText({ reason: "blocked" }, en.failure);
    expect(text).toBe(en.failure.blocked);
    expect(text).not.toBe(en.failure.unknown);
  });

  it("renders every reason as its own sentence", () => {
    // No two reasons may collapse onto one string: the vocabulary exists to
    // NAME a cause, and two causes sharing wording is the silence it removes.
    const texts = [
      failureText({ reason: "machine-unreachable" }, en.failure),
      failureText({ reason: "refused" }, en.failure),
      failureText({ reason: "blocked" }, en.failure),
      failureText({ reason: "unknown" }, en.failure),
    ];
    expect(new Set(texts).size).toBe(texts.length);
  });
});
