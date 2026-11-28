import { describe, expect, it } from "vitest";

import { dayHeadingFor } from "./day-heading";

/** Local midnight-based instants, so every case reads as a wall clock. */
const at = (y: number, m: number, d: number, h = 12): number =>
  new Date(y, m - 1, d, h).getTime();

const NOW = at(2026, 8, 29, 14);

describe("dayHeadingFor", () => {
  it("says nothing when the first row is TODAY", () => {
    // A fresh chat opened and answered today: the divider separates nothing and
    // names the day the reader is already in.
    // MUTANT: drop the `previous === undefined` guard → this dies.
    expect(dayHeadingFor(at(2026, 8, 29), undefined, NOW)).toBeUndefined();
  });

  it("still opens the first row when it is NOT today", () => {
    // The other half, and the reason the guard is narrow. Here the label is the
    // only thing telling the reader when this conversation happened, so
    // suppressing it would hide a fact rather than a redundancy.
    // MUTANT: return undefined for every `previous === undefined` → this dies.
    expect(dayHeadingFor(at(2026, 8, 28), undefined, NOW)).toBe("yesterday");
    expect(dayHeadingFor(at(2026, 8, 14), undefined, NOW)).toBe("absolute");
  });

  it("still names today after an older row", () => {
    // Only the FIRST row is exempt. A transcript that resumes today after a gap
    // needs the boundary marked, which is the divider's whole job.
    expect(dayHeadingFor(at(2026, 8, 29), at(2026, 8, 14), NOW)).toBe("today");
  });

  it("stays silent while the day continues", () => {
    expect(dayHeadingFor(at(2026, 8, 29, 18), at(2026, 8, 29, 9), NOW)).toBeUndefined();
  });

  it("names today, yesterday, and anything older by its date", () => {
    const prev = at(2026, 8, 20);
    expect(dayHeadingFor(at(2026, 8, 29), prev, NOW)).toBe("today");
    expect(dayHeadingFor(at(2026, 8, 28), prev, NOW)).toBe("yesterday");
    expect(dayHeadingFor(at(2026, 8, 27), prev, NOW)).toBe("absolute");
  });

  it("measures yesterday from NOW, not from the row", () => {
    // A row two days old, read on a day when the row before it was older still.
    // Reading "one day before `at`" instead of before `now` would call this
    // "yesterday" — MUTANT: shift `at` rather than `now` → this dies.
    expect(dayHeadingFor(at(2026, 8, 27), at(2026, 8, 1), NOW)).toBe("absolute");
  });

  it("crosses a month boundary", () => {
    const now = at(2026, 9, 1, 10);
    expect(dayHeadingFor(at(2026, 8, 31), at(2026, 8, 20), now)).toBe("yesterday");
  });

  it("crosses a year boundary", () => {
    const now = at(2027, 1, 1, 10);
    expect(dayHeadingFor(at(2026, 12, 31), at(2026, 12, 20), now)).toBe("yesterday");
    // Same day-of-month one year back must NOT read as the same day.
    expect(dayHeadingFor(at(2026, 1, 1), at(2025, 12, 30), now)).toBe("absolute");
  });

  it("labels a row that is one calendar day back but under 24h away", () => {
    // 23:30 yesterday, read at 00:30 today — an hour apart, two days.
    const now = at(2026, 8, 29, 0) + 30 * 60_000;
    const row = at(2026, 8, 28, 23) + 30 * 60_000;
    // MUTANT: compare by elapsed millis instead of calendar date → this dies.
    expect(dayHeadingFor(row, at(2026, 8, 20), now)).toBe("yesterday");
  });
});
