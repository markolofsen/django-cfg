import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { TimelinePlayer } from "./player";

const items = [0, 100, 300, 300, 1000].map((at, i) => ({ at, item: `e${i}` }));

function setup(options: { speed?: number; autoplay?: boolean } = {}) {
  const player = new TimelinePlayer(items, options);
  const seen: string[] = [];
  const ended = vi.fn();
  player.attach((item) => seen.push(item), ended);
  return { player, seen, ended };
}

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe("the timeline player", () => {
  it("waits until played", () => {
    const { seen } = setup();
    vi.advanceTimersByTime(5000);
    expect(seen).toEqual([]);
  });

  it("plays items at the gaps between their times", () => {
    const { player, seen, ended } = setup();
    player.play();
    vi.advanceTimersByTime(0);
    expect(seen).toEqual(["e0"]);
    vi.advanceTimersByTime(100);
    expect(seen).toEqual(["e0", "e1"]);
    vi.advanceTimersByTime(200);
    expect(seen).toEqual(["e0", "e1", "e2", "e3"]);
    expect(ended).not.toHaveBeenCalled();
    vi.advanceTimersByTime(700);
    expect(seen).toHaveLength(5);
    expect(ended).toHaveBeenCalledTimes(1);
    expect(player.getState()).toMatchObject({ finished: true, playing: false, index: 5, total: 5 });
  });

  it("pauses and resumes without losing its place", () => {
    const { player, seen } = setup();
    player.play();
    vi.advanceTimersByTime(100);
    player.pause();
    vi.advanceTimersByTime(10_000);
    expect(seen).toEqual(["e0", "e1"]);
    player.play();
    vi.advanceTimersByTime(200);
    expect(seen).toEqual(["e0", "e1", "e2", "e3"]);
  });

  it("steps one event and stays paused", () => {
    const { player, seen } = setup();
    player.step();
    player.step();
    expect(seen).toEqual(["e0", "e1"]);
    vi.advanceTimersByTime(5000);
    expect(seen).toEqual(["e0", "e1"]);
    expect(player.getState().playing).toBe(false);
  });

  it("runs to the end at once and closes the stream", () => {
    const { player, seen, ended } = setup();
    player.toEnd();
    expect(seen).toHaveLength(5);
    expect(ended).toHaveBeenCalledTimes(1);
  });

  it("scales gaps by speed, and instant delivers everything", () => {
    const fast = setup({ speed: 4, autoplay: true });
    vi.advanceTimersByTime(0);
    vi.advanceTimersByTime(25);
    expect(fast.seen).toEqual(["e0", "e1"]);
    const instant = setup();
    instant.player.setSpeed(Number.POSITIVE_INFINITY);
    instant.player.play();
    expect(instant.seen).toHaveLength(5);
  });

  it("changes speed while playing", () => {
    const { player, seen } = setup();
    player.play();
    vi.advanceTimersByTime(0);
    player.setSpeed(0.5);
    vi.advanceTimersByTime(199);
    expect(seen).toEqual(["e0"]);
    vi.advanceTimersByTime(1);
    expect(seen).toEqual(["e0", "e1"]);
  });

  it("stops delivering once detached (Stop)", () => {
    const { player, seen } = setup();
    player.play();
    vi.advanceTimersByTime(100);
    player.detach();
    vi.advanceTimersByTime(5000);
    expect(seen).toEqual(["e0", "e1"]);
  });

  it("tells subscribers about each change with a new snapshot", () => {
    const { player } = setup();
    const listener = vi.fn();
    player.subscribe(listener);
    const before = player.getState();
    player.step();
    expect(listener).toHaveBeenCalled();
    expect(player.getState()).not.toBe(before);
    expect(player.getState().index).toBe(1);
  });
});
