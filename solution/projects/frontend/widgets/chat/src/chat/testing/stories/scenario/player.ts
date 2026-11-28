import type { Timed } from "./compile";

/** `Infinity` is "instant": every remaining item is delivered at once. */
export const SPEEDS = [0.5, 1, 4, Number.POSITIVE_INFINITY] as const;
export type Speed = (typeof SPEEDS)[number];

export interface PlayerState {
  /** How many items have been delivered. */
  readonly index: number;
  readonly total: number;
  readonly playing: boolean;
  readonly speed: number;
  readonly finished: boolean;
}

/**
 * A timeline you can hold: play, pause, step one event, run to the end, change speed.
 *
 * Headless and generic, so the same player drives a chunk stream and a frame stream and a test can drive
 * it with fake timers. Delivery goes to one sink; the transport adapters close their stream from `onEnd`.
 * Gaps come from the items' own times (seeded jitter lives in the builder), divided by the speed.
 */
export class TimelinePlayer<T> {
  private index = 0;
  private playing = false;
  private speed = 1;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private sink: ((item: T, index: number) => void) | null = null;
  private end: (() => void) | null = null;
  private ended = false;
  private snapshot: PlayerState;
  private readonly listeners = new Set<() => void>();

  constructor(private readonly items: readonly Timed<T>[], options: { readonly speed?: number; readonly autoplay?: boolean } = {}) {
    this.speed = options.speed ?? 1;
    this.playing = options.autoplay ?? false;
    this.snapshot = this.read();
  }

  /** Where delivered items go. Items wait until a sink is attached. */
  attach(sink: (item: T, index: number) => void, onEnd: () => void): void {
    this.sink = sink;
    this.end = onEnd;
    if (this.playing) this.schedule();
  }

  /** The stream was cancelled from outside (Stop): nothing more is delivered. */
  detach(): void {
    this.clear();
    this.sink = null;
    this.playing = false;
    this.publish();
  }

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getState = (): PlayerState => this.snapshot;

  play(): void {
    if (this.finished) return;
    this.playing = true;
    this.publish();
    if (this.speed === Number.POSITIVE_INFINITY) this.toEnd();
    else this.schedule();
  }

  pause(): void {
    this.playing = false;
    this.clear();
    this.publish();
  }

  /** Deliver exactly one more item and stay paused. */
  step(): void {
    this.playing = false;
    this.clear();
    this.deliver();
    this.publish();
  }

  /** Deliver everything that is left, now. */
  toEnd(): void {
    this.clear();
    while (!this.finished && this.sink !== null) this.deliver();
    this.playing = false;
    this.publish();
  }

  setSpeed(speed: number): void {
    this.speed = speed;
    if (this.playing) {
      this.clear();
      if (speed === Number.POSITIVE_INFINITY) this.toEnd();
      else this.schedule();
    }
    this.publish();
  }

  private get finished(): boolean {
    return this.index >= this.items.length;
  }

  private read(): PlayerState {
    return { index: this.index, total: this.items.length, playing: this.playing, speed: this.speed, finished: this.finished };
  }

  private publish(): void {
    this.snapshot = this.read();
    for (const listener of this.listeners) listener();
  }

  private clear(): void {
    if (this.timer !== null) clearTimeout(this.timer);
    this.timer = null;
  }

  private gap(): number {
    const next = this.items[this.index];
    if (next === undefined) return 0;
    const before = this.items[this.index - 1]?.at ?? 0;
    return Math.max(0, next.at - before) / this.speed;
  }

  private schedule(): void {
    this.clear();
    if (!this.playing || this.sink === null) return;
    if (this.finished) {
      this.close();
      return;
    }
    this.timer = setTimeout(() => {
      this.deliver();
      // Items at the same instant arrive together, as the server sent them.
      while (this.playing && this.sink !== null && !this.finished && this.gap() === 0) this.deliver();
      this.publish();
      this.schedule();
    }, this.gap());
  }

  private deliver(): void {
    const next = this.items[this.index];
    if (next !== undefined && this.sink !== null) {
      const at = this.index;
      this.index += 1;
      this.sink(next.item, at);
    }
    if (this.finished) this.close();
  }

  private close(): void {
    if (this.ended) return;
    this.ended = true;
    this.playing = false;
    this.end?.();
  }
}
