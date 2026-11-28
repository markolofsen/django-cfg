import type { ChatMessage } from "../../../core/conversation/parts";
import { rng, tokens, type Beat, type RawStep, type Scenario, type ScenarioGroup, type StreamErrorCode } from "./model";

export interface ToolOptions {
  readonly label?: string;
  readonly summary?: string;
  readonly purpose?: string;
  readonly query?: string;
  readonly args?: Readonly<Record<string, unknown>>;
  readonly argsSize?: number;
  readonly result?: { readonly preview: string; readonly size?: number; readonly truncated?: boolean };
  readonly refs?: readonly { readonly kind: string; readonly id: string; readonly title?: string }[];
  /** How long the call takes. Default: seeded, 80 to 2500 ms. */
  readonly ms?: number;
  /** How the call ends. Default `ok`. */
  readonly status?: "ok" | "error" | "timeout" | "cancelled" | "skipped" | "denied";
  /** What the server removed from the detail. Default `none`. */
  readonly redaction?: "none" | "masked" | "omitted";
  readonly parent?: string;
  readonly error?: { readonly code: string; readonly retryable?: boolean };
  /** Another step kind than `tool`: `usage`, `note`, `handoff`. */
  readonly kind?: string;
  readonly model?: string;
  readonly tokens?: Readonly<Record<string, number>>;
  readonly costUsd?: number;
}

export interface Meta {
  readonly id: string;
  readonly title: string;
  readonly note: string;
  readonly group: ScenarioGroup;
  readonly prompt: string;
  readonly seed?: number;
}

/**
 * Builds a scenario in the order things happen. The cursor moves forward by what each beat takes;
 * gaps come from a seeded generator (tool latency 80 to 2500 ms, token cadence 20 to 60 ms), so the
 * run looks real and is the same every time.
 */
export class ScenarioBuilder {
  private readonly beats: Beat[] = [];
  private readonly random: () => number;
  private readonly seed: number;
  private cursor = 120;
  private steps = 0;
  private past: readonly ChatMessage[] | undefined;

  constructor(private readonly meta: Meta) {
    this.seed = meta.seed ?? 7;
    this.random = rng(this.seed);
  }

  /** A pause with nothing on screen changing. */
  wait(ms: number): this {
    this.cursor += ms;
    return this;
  }

  private between(low: number, high: number): number {
    return Math.round(low + this.random() * (high - low));
  }

  say(text: string): this {
    const pieces = tokens(text);
    const ms = pieces.reduce((total) => total + this.between(20, 60), 0);
    this.beats.push({ kind: "say", at: this.cursor, text, ms });
    this.cursor += ms;
    return this;
  }

  think(text: string, options: { readonly tokens?: number; readonly ms?: number } = {}): this {
    const pieces = tokens(text);
    const ms = options.ms ?? pieces.reduce((total) => total + this.between(25, 70), 0);
    this.beats.push({ kind: "think", at: this.cursor, text, ms, ...(options.tokens === undefined ? {} : { tokens: options.tokens }) });
    this.cursor += ms;
    return this;
  }

  /** One call: a running frame now, the settled frame when it ends. Returns the step id. */
  tool(name: string, options: ToolOptions = {}): this {
    this.emitTool(name, options, this.cursor);
    this.cursor += this.lastDuration;
    return this;
  }

  /** Calls that start together and end on their own clocks. The run waits for the longest. */
  parallel(calls: readonly (readonly [string, ToolOptions])[]): this {
    const start = this.cursor;
    let longest = 0;
    for (const [name, options] of calls) {
      this.emitTool(name, options, start);
      longest = Math.max(longest, this.lastDuration);
    }
    this.cursor = start + longest;
    return this;
  }

  private lastDuration = 0;

  private emitTool(name: string, options: ToolOptions, start: number): void {
    this.steps += 1;
    const id = `s${this.steps}`;
    const ms = options.ms ?? this.between(80, 2500);
    this.lastDuration = ms;
    const kind = options.kind ?? "tool";
    const redaction = options.redaction ?? "none";
    const common: Record<string, unknown> = {
      v: 1,
      step_id: id,
      seq: this.steps,
      kind,
      name,
      redaction,
      ...(options.label === undefined ? {} : { label: options.label }),
      started_ms: start,
      ...(options.parent === undefined ? {} : { parent_id: options.parent }),
      ...(options.purpose === undefined ? {} : { purpose: options.purpose }),
      ...(options.query === undefined ? {} : { query: options.query }),
      ...(options.args === undefined ? {} : { args: options.args }),
      ...(options.argsSize === undefined ? {} : { args_size: options.argsSize }),
      ...(options.refs === undefined ? {} : { refs: options.refs }),
    };
    this.pushStep({ ...common, status: "running" }, start);
    const status = options.status ?? "ok";
    const settled: Record<string, unknown> = {
      ...common,
      status,
      duration_ms: ms,
      ...(options.summary === undefined ? {} : { summary: options.summary }),
      ...(options.result === undefined ? {} : { result: options.result }),
      ...(options.error === undefined ? {} : { error: options.error }),
      ...(options.tokens === undefined ? {} : { tokens: options.tokens }),
      ...(options.costUsd === undefined ? {} : { cost_usd: options.costUsd }),
      ...(options.model === undefined ? {} : { model: options.model }),
    };
    this.pushStep(settled, start + ms);
  }

  /** A single frame of a step the caller wrote by hand (a thought the server kept hidden, a note). */
  step(raw: RawStep, at = this.cursor): this {
    this.pushStep(raw, at);
    return this;
  }

  private pushStep(step: RawStep, at: number): void {
    this.beats.push({ kind: "step", at, step, eventSeq: 0 });
  }

  payload(name: string, data: unknown): this {
    this.beats.push({ kind: "payload", at: this.cursor, name, data });
    this.cursor += 40;
    return this;
  }

  finish(): this {
    this.beats.push({ kind: "finish", at: this.cursor + 60 });
    return this;
  }

  fail(code: StreamErrorCode, message: string): this {
    this.beats.push({ kind: "fail", at: this.cursor + 60, code, message });
    return this;
  }

  lost(): this {
    this.beats.push({ kind: "lost", at: this.cursor + 400 });
    return this;
  }

  offline(): this {
    this.beats.push({ kind: "offline", at: 400 });
    return this;
  }

  history(messages: readonly ChatMessage[]): this {
    this.past = messages;
    return this;
  }

  build(): Scenario {
    // Stable by time: a parallel batch interleaves its frames, and equal times keep authoring order.
    const sorted = this.beats.map((beat, index) => ({ beat, index })).sort((a, b) => a.beat.at - b.beat.at || a.index - b.index).map(({ beat }) => beat);
    // The server numbers frames in the order it sends them, so the sequence follows time, not authoring order.
    let sequence = 0;
    const beats = sorted.map((beat): Beat => (beat.kind === "step" ? { ...beat, eventSeq: (sequence += 1) } : beat));
    return {
      id: this.meta.id,
      title: this.meta.title,
      note: this.meta.note,
      group: this.meta.group,
      prompt: this.meta.prompt,
      messageId: `m-${this.meta.id}`,
      beats,
      seed: this.seed,
      ...(this.past === undefined ? {} : { history: this.past }),
    };
  }
}

export const scenario = (meta: Meta): ScenarioBuilder => new ScenarioBuilder(meta);
