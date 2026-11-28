import { describe, expect, it, vi } from "vitest";

import { VoiceSession, type VoiceSnapshot } from "./session";

/**
 * The two rules that are invisible when broken: an interim REPLACES, a final
 * COMMITS. Getting the first wrong duplicates the user's sentence in front of
 * them while they are still speaking.
 */

function voice(options: { readonly earconThrows?: boolean } = {}) {
  let emit: (text: string, final: boolean) => void = () => {};
  let settle: () => void = () => {};
  let fail: (error: Error) => void = () => {};
  const stop = vi.fn();
  const seen: VoiceSnapshot[] = [];
  // Tones AND engine calls in ONE log, because the ordering between them is the
  // thing under test: a tone inside the live window is transcribed as a word,
  // and only an interleaved record can show which side of it a tone fell on.
  const trace: string[] = [];

  const session = new VoiceSession({
    capability: {
      start: (onText) =>
        new Promise<void>((resolve, reject) => {
          trace.push("engine:start");
          emit = onText;
          settle = resolve;
          fail = reject;
        }),
      stop: () => {
        trace.push("engine:stop");
        stop();
      },
    },
    onChange: (snapshot) => seen.push(snapshot),
    playEarcon: (kind) => {
      trace.push(`tone:${kind}`);
      if (options.earconThrows) throw new Error("no audio device");
    },
  });

  return {
    session,
    stop,
    seen,
    trace,
    emit: (text: string, final = false) => emit(text, final),
    settle: () => settle(),
    fail: (message: string) => fail(new Error(message)),
  };
}

const flush = () => new Promise((resolve) => setTimeout(resolve, 0));

describe("interim results", () => {
  it("REPLACE rather than append", () => {
    // The defect this exists for: the engine re-sends its whole current guess
    // as it refines, so appending shows "hello wor hello world".
    const { session, emit } = voice();
    session.start();

    emit("hello wor");
    emit("hello world");

    expect(session.state.text).toBe("hello world");
    expect(session.state.interim).toBe("hello world");
  });
});

describe("final results", () => {
  it("commit and reset the interim", () => {
    const { session, emit } = voice();
    session.start();

    emit("hello", true);
    expect(session.state.committed).toBe("hello");
    expect(session.state.interim).toBe("");

    emit("wor");
    expect(session.state.text).toBe("hello wor");
  });

  it("join committed phrases with a space", () => {
    // The engine emits phrases, not a continuous stream; joining without a
    // separator runs sentences together.
    const { session, emit } = voice();
    session.start();

    emit("hello", true);
    emit("world", true);

    expect(session.state.text).toBe("hello world");
  });
});

describe("stopping", () => {
  it("commits the in-flight interim rather than losing the last words", () => {
    const { session, emit, stop } = voice();
    session.start();
    emit("hello", true);
    emit("world");

    session.stop();

    expect(stop).toHaveBeenCalled();
    expect(session.state.recording).toBe(false);
    expect(session.state.text).toBe("hello world");
    // The interim must have been MOVED into committed, not merely blanked.
    //
    // A mutant that writes the snapshot directly — skipping the emit() that
    // recomputes `text` — passes the two assertions above. It
    // left `committed: "hello"`, `interim: ""` and a STALE `text: "hello
    // world"`, which happens to equal the right answer. Asserting the derived
    // field alone cannot distinguish "committed correctly" from "text never
    // recomputed", so the source fields are asserted too.
    expect(session.state.committed).toBe("hello world");
    expect(session.state.interim).toBe("");
  });

  it("keeps text consistent with its source fields after every transition", () => {
    // The general form of the trap above: `text` is derived, so any writer that
    // bypasses the one place computing it leaves a snapshot that contradicts
    // itself. Cheap to assert, and it catches the whole class.
    const { session, emit } = voice();
    const consistent = () => {
      const { committed, interim, text } = session.state;
      const expected =
        interim === "" ? committed : committed === "" ? interim : `${committed} ${interim}`;
      expect(text).toBe(expected);
    };

    session.start();
    consistent();
    emit("a", true);
    consistent();
    emit("b");
    consistent();
    session.stop();
    consistent();
  });

  it("cancel() DISCARDS, because after a send the draft is already cleared", () => {
    // Committing here would resurrect the message the user just sent.
    const { session, emit } = voice();
    session.start();
    emit("hello", true);

    session.cancel();

    expect(session.state.text).toBe("");
    expect(session.state.recording).toBe(false);
  });

  it("take() returns the text and resets", () => {
    const { session, emit } = voice();
    session.start();
    emit("hello world", true);

    expect(session.take()).toBe("hello world");
    expect(session.state.text).toBe("");
  });

  it("ignores results that arrive after stop", () => {
    // Words from an ended session would append to a draft already sent.
    const { session, emit } = voice();
    session.start();
    session.stop();

    emit("late words", true);

    expect(session.state.text).toBe("");
  });

  it("ignores results that arrive after CANCEL, not only after stop", () => {
    // The send race, and the reason the sibling above is not enough. A send
    // cancels mid-sentence, so the engine is still mid-phrase when the draft is
    // cleared — a result accepted here lands in the message the user is about to
    // type NEXT, having said none of it.
    //
    // MUTANT: drop `this.controller = null` from cancel() → this dies.
    const { session, emit } = voice();
    session.start();
    emit("half a sen", false);

    session.cancel();
    emit("half a sentence", true);

    expect(session.state.text).toBe("");
  });

  it("commits the interim when the engine ends on its own", async () => {
    // A pause or a time limit ends recognition; the last guess is still the
    // user's words.
    const { session, emit, settle } = voice();
    session.start();
    emit("hello");

    settle();
    await flush();

    expect(session.state.recording).toBe(false);
    expect(session.state.text).toBe("hello");
  });
});

describe("failure", () => {
  it("settles the error on the snapshot rather than throwing", async () => {
    // A rejection here would be an unhandled rejection mid-sentence.
    const { session, fail } = voice();
    session.start();

    fail("no microphone");
    await flush();

    expect(session.state.recording).toBe(false);
    expect(session.state.error).toBe("no microphone");
  });
});

describe("the derived text", () => {
  it("is never assigned, only computed", () => {
    // Two writers for one value is how the snapshot and the draft drift apart.
    const { session, emit } = voice();
    session.start();
    emit("a", true);
    emit("b");

    expect(session.state.text).toBe(`${session.state.committed} ${session.state.interim}`);
  });

  it("does not start with a stray space when nothing is committed yet", () => {
    const { session, emit } = voice();
    session.start();
    emit("hello");

    expect(session.state.text).toBe("hello");
  });
});

describe("the control", () => {
  it("emits on start, so the assertions are not reading a frozen snapshot", () => {
    const { session, seen } = voice();
    session.start();

    expect(seen.length).toBeGreaterThan(0);
    expect(session.state.recording).toBe(true);
  });

  it("start() is idempotent while recording", () => {
    const { session, seen } = voice();
    session.start();
    const after = seen.length;
    session.start();

    expect(seen.length).toBe(after);
  });
});

/**
 * The earcons, and the one property that makes them safe: a tone never plays
 * while the microphone is open, or the engine transcribes it as a word.
 */
describe("earcons", () => {
  it("plays the start tone BEFORE the engine opens the microphone", () => {
    // MUTANT: move `this.earcon("start")` below `capability.start(...)` → this
    // dies. Nothing else can see it: dictation still works and the transcript
    // merely gains a phantom syllable.
    const { session, trace } = voice();
    session.start();

    expect(trace).toEqual(["tone:start", "engine:start"]);
  });

  it("plays the stop tone AFTER the engine is told to stop", () => {
    // MUTANT: move `this.earcon("stop")` above `capability.stop()` in `stop()`
    // → this dies. Same window, closing edge.
    const { session, trace } = voice();
    session.start();
    trace.length = 0;

    session.stop();

    expect(trace).toEqual(["engine:stop", "tone:stop"]);
  });

  it("plays the stop tone when the engine ends on its own", async () => {
    // A silence timeout is a stop the user did not ask for, so it is exactly
    // when they need telling.
    const { session, trace, settle } = voice();
    session.start();
    trace.length = 0;

    settle();
    await flush();

    expect(trace).toEqual(["tone:stop"]);
  });

  it("closes the pair on failure, so a denied microphone does not hang open", async () => {
    // MUTANT: drop the `earcon("stop")` from the catch → this dies. The start
    // tone has already played (it must, before the microphone opens), so
    // silence here leaves a session the user heard begin and never end.
    const { session, trace, fail } = voice();
    session.start();

    fail("Microphone permission denied");
    await flush();

    expect(trace).toEqual(["tone:start", "engine:start", "tone:stop"]);
  });

  it("is SILENT on cancel, because the send plays its own chime", () => {
    // MUTANT: add `earcon("stop")` to cancel() → this dies. Two sounds for one
    // action, and the user pressed send, not stop.
    const { session, trace } = voice();
    session.start();
    trace.length = 0;

    session.cancel();

    expect(trace).toEqual(["engine:stop"]);
  });

  it("survives a throwing player — audio is decoration, recognition is not", () => {
    // MUTANT: call `options.playEarcon` directly instead of through
    // `safeEarcon` → this dies with the thrown error. A host with no audio
    // device must cost the user a tone, never their sentence.
    const { session, seen } = voice({ earconThrows: true });

    expect(() => session.start()).not.toThrow();
    expect(seen.at(-1)?.recording).toBe(true);
  });

  it("needs no player at all", () => {
    // Absent ⇒ silent dictation, a legitimate configuration. The session must
    // hold one shape rather than null-checking at each call site.
    const session = new VoiceSession({
      capability: { start: () => new Promise<void>(() => {}), stop: () => {} },
      onChange: () => {},
    });

    expect(() => {
      session.start();
      session.stop();
    }).not.toThrow();
  });
});
