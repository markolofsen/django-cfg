import { describe, expect, it } from "vitest";

import { formatBytes, formatClock } from "./values";

/**
 * These pin the two facts a call site relies on and neither could previously
 * fail on: the BASE (1024, so a 36 GiB host reads "36 GB" and not "38.7 GB"),
 * and the digit rule at its boundary.
 */
describe("formatBytes", () => {
  it("uses binary steps, not decimal", () => {
    expect(formatBytes(1024)).toBe("1 KB");
    // Below the 1024 step this is still BYTES — a decimal formatter would have
    // switched units here. The separator is `Intl` digit grouping, not a bug.
    expect(formatBytes(1000)).toBe("1,000 B");
    expect(formatBytes(1024 ** 3)).toBe("1 GB");
    expect(formatBytes(36 * 1024 ** 3)).toBe("36 GB");
  });

  it("keeps one decimal below 10 and whole numbers at or above it", () => {
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(1.4 * 1024 ** 3)).toBe("1.4 GB");
    expect(formatBytes(15 * 1024)).toBe("15 KB");
    // The threshold sits AT 10, and both sides of it are pinned: a mutation
    // moving it to 5 changes only values in between.
    expect(formatBytes(9.5 * 1024)).toBe("9.5 KB");
    expect(formatBytes(6.2 * 1024 ** 2)).toBe("6.2 MB");
    expect(formatBytes(10 * 1024)).toBe("10 KB");
  });

  it("never leaves the unit table, however large the input", () => {
    expect(formatBytes(5 * 1024 ** 6)).toBe("5,242,880 TB");
  });

  it("prints raw bytes whole and collapses unusable input", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(-1)).toBe("0 B");
    expect(formatBytes(Number.NaN)).toBe("0 B");
  });
});

describe("formatClock", () => {
  it("spells a track position, not a duration", () => {
    expect(formatClock(214)).toBe("3:34");
    expect(formatClock(59)).toBe("0:59");
  });

  it("adds an hours field only once there are hours", () => {
    expect(formatClock(3599)).toBe("59:59");
    expect(formatClock(3600)).toBe("1:00:00");
    expect(formatClock(3661)).toBe("1:01:01");
  });

  it("treats zero as a real reading, not as absent", () => {
    // A track at its start. Collapsing this to an empty string is what makes a
    // playing clock vanish at 0:00.
    expect(formatClock(0)).toBe("0:00");
  });

  it("collapses unusable input rather than printing NaN", () => {
    expect(formatClock(-1)).toBe("0:00");
    expect(formatClock(Number.NaN)).toBe("0:00");
    expect(formatClock(Number.POSITIVE_INFINITY)).toBe("0:00");
  });

  it("floors a fractional position instead of rounding up", () => {
    // A clock that reads 3:35 while the element says 3:34.9 is a clock that
    // reaches the end before the audio does.
    expect(formatClock(214.9)).toBe("3:34");
  });
});
