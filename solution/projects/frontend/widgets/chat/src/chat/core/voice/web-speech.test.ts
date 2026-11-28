import { afterEach, describe, expect, it } from "vitest";

import { createWebSpeechCapability, isWebSpeechAvailable } from "./web-speech";

/**
 * A stand-in for the browser's engine.
 *
 * The package has no jsdom, so `window` is installed on `globalThis` for the
 * duration of a test. That is honest here: this file is an ADAPTER over two
 * global constructor spellings, and the thing worth testing is what it does
 * with the events it is handed — not the DOM.
 */
class FakeRecognition {
  static last: FakeRecognition | null = null;

  continuous = false;
  interimResults = false;
  lang = "";
  started = 0;
  stopped = 0;
  aborted = 0;
  onresult: ((event: unknown) => void) | null = null;
  onerror: ((event: { readonly error?: string }) => void) | null = null;
  onend: (() => void) | null = null;

  constructor() {
    FakeRecognition.last = this;
  }

  start(): void {
    this.started += 1;
  }

  stop(): void {
    this.stopped += 1;
  }

  abort(): void {
    this.aborted += 1;
  }

  /** One `result` event carrying a single alternative. */
  emit(transcript: string, isFinal: boolean, resultIndex = 0): void {
    this.onresult?.({
      resultIndex,
      results: { length: resultIndex + 1, [resultIndex]: { isFinal, length: 1, 0: { transcript } } },
    });
  }
}

function install(ctor?: unknown): void {
  (globalThis as { window?: unknown }).window =
    ctor === undefined ? {} : { SpeechRecognition: ctor };
}

afterEach(() => {
  delete (globalThis as { window?: unknown }).window;
  FakeRecognition.last = null;
});

describe("availability", () => {
  it("is false when the browser has no engine", () => {
    install();
    expect(isWebSpeechAvailable()).toBe(false);
    expect(createWebSpeechCapability({ language: () => "en-US" })).toBeUndefined();
  });

  it("is true when a constructor is present", () => {
    install(FakeRecognition);
    // The control for every test below: without this the capability is
    // undefined and each assertion would be measuring nothing.
    expect(isWebSpeechAvailable()).toBe(true);
    expect(createWebSpeechCapability({ language: () => "en-US" })).toBeDefined();
  });

  it("accepts the webkit spelling", () => {
    (globalThis as { window?: unknown }).window = { webkitSpeechRecognition: FakeRecognition };
    expect(isWebSpeechAvailable()).toBe(true);
  });
});

describe("a dictation session", () => {
  it("reads the language at START, so a change applies to the next one", () => {
    install(FakeRecognition);
    let language = "en-US";
    const capability = createWebSpeechCapability({ language: () => language })!;

    void capability.start(() => undefined, new AbortController().signal);
    expect(FakeRecognition.last?.lang).toBe("en-US");

    language = "ru-RU";
    void capability.start(() => undefined, new AbortController().signal);
    expect(FakeRecognition.last?.lang).toBe("ru-RU");
  });

  it("asks for continuous, interim results", () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    void capability.start(() => undefined, new AbortController().signal);

    // Interim results are the half Vercel's reference DISCARDS. Without them a
    // user sees nothing until a whole phrase completes, and `VoiceSession`'s
    // replace-never-append rule has nothing to act on.
    expect(FakeRecognition.last?.continuous).toBe(true);
    expect(FakeRecognition.last?.interimResults).toBe(true);
  });

  it("passes interim and final results through with their flag", () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const seen: Array<readonly [string, boolean]> = [];
    void capability.start((text, final) => seen.push([text, final]), new AbortController().signal);

    FakeRecognition.last?.emit("hello wor", false);
    FakeRecognition.last?.emit("hello world", true);

    expect(seen).toEqual([
      ["hello wor", false],
      ["hello world", true],
    ]);
  });

  it("reads from resultIndex, not from zero", async () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const seen: string[] = [];
    void capability.start((text) => seen.push(text), new AbortController().signal);

    // The engine re-sends its whole results list. Replaying from zero would
    // re-deliver a phrase already committed and the sentence duplicates itself.
    FakeRecognition.last?.emit("second phrase", true, 1);

    expect(seen).toEqual(["second phrase"]);
  });

  it("treats an empty room as an ending, not a failure", async () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const turn = capability.start(() => undefined, new AbortController().signal);

    FakeRecognition.last?.onerror?.({ error: "no-speech" });

    // A red error under the composer for saying nothing is a promise broken for
    // no reason. Same for `aborted`, which is the user pressing stop.
    await expect(turn).resolves.toBeUndefined();
  });

  it("surfaces a real failure", async () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const turn = capability.start(() => undefined, new AbortController().signal);

    FakeRecognition.last?.onerror?.({ error: "not-allowed" });

    await expect(turn).rejects.toThrow("not-allowed");
  });

  it("stops rather than aborts, so the last phrase still arrives", () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    void capability.start(() => undefined, new AbortController().signal);

    capability.stop();

    expect(FakeRecognition.last?.stopped).toBe(1);
    expect(FakeRecognition.last?.aborted).toBe(0);
  });

  it("aborts on the signal and resolves", async () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const controller = new AbortController();
    const turn = capability.start(() => undefined, controller.signal);

    controller.abort();

    expect(FakeRecognition.last?.aborted).toBe(1);
    await expect(turn).resolves.toBeUndefined();
  });

  it("does nothing when handed an already-aborted signal", async () => {
    install(FakeRecognition);
    const capability = createWebSpeechCapability({ language: () => "en-US" })!;
    const controller = new AbortController();
    controller.abort();

    await expect(capability.start(() => undefined, controller.signal)).resolves.toBeUndefined();
    expect(FakeRecognition.last).toBeNull();
  });
});
