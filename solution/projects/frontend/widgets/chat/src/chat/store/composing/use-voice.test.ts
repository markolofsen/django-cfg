import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * `useVoice` stability, ratcheted in the source.
 *
 * A sibling of `use-mentions.test.ts`, which is NOT enough on its own: it reads
 * only its own module, so the identical defect in this one goes unguarded. A
 * mutant putting `snapshot` back into the actions memo of `use-voice.ts`
 * survives the whole suite otherwise.
 *
 * The rule both hooks obey: **memoise the ACTIONS on the session alone.** A
 * caller may put `stop` in an effect's dependency array — stopping dictation
 * when a turn is sent is exactly that shape — and if the actions were rebuilt
 * on every snapshot, that effect would fire on each interim result and re-run
 * forever: "Maximum update depth exceeded". That is not hypothetical; it
 * happened in the composer workbench and wedged a story run for 460 seconds.
 *
 * No jsdom in this package, so a source read is not the weaker option — it is
 * the only one. Replace with a render test the moment jsdom lands.
 */

const CODE = readFileSync(join(__dirname, "use-voice.ts"), "utf8")
  .replace(/\/\*[\s\S]*?\*\//g, "")
  .replace(/\/\/.*$/gm, "");

describe("useVoice session stability", () => {
  it("memoises the ACTIONS on the session alone, never on the snapshot", () => {
    // MUTANT: add `snapshot` to the actions dep array → this dies.
    // Anchored on `}),` — the END of the factory object — not the first `[...]`
    // a lazy scan reaches: the actions body contains `?? ""`, and the sibling
    // ratchet was once fooled into reading the NEXT memo's dep array instead.
    const actionsMemo = CODE.match(/const actions = useMemo\([\s\S]*?\}\),\s*\[([^\]]*)\]/);
    expect(actionsMemo, "the actions are no longer a memo of their own").not.toBeNull();

    const deps = (actionsMemo?.[1] ?? "")
      .split(",")
      .map((d) => d.trim())
      .filter(Boolean);
    expect(deps, "an action does not change because a word was transcribed").toEqual(["session"]);
  });

  it("never keys the session memo on the capability OBJECT", () => {
    // The capability is an object literal at every realistic call site, so a
    // fresh reference on each parent render would rebuild the session
    // MID-SENTENCE and drop the words already dictated.
    const memoDeps = /useMemo\([\s\S]*?,\s*\[([^\]]*)\]\s*\)/g;
    const offenders: string[] = [];
    for (const [, deps = ""] of CODE.matchAll(memoDeps)) {
      offenders.push(
        ...deps
          .split(",")
          .map((d) => d.trim())
          .filter((d) => d === "capability" || d === "capabilities"),
      );
    }
    expect(offenders).toEqual([]);
  });

  it("reads the host's engine through a ref, so a new literal still routes", () => {
    // The direct consequence of the rule above: keying only on presence means
    // the memo does NOT rebuild when the host passes new functions, so without
    // a ref the session would call the FIRST render's engine forever.
    expect(CODE).toContain("latest.current");
    // The EFFECTIVE engine — the host's capability, or the package's Web Speech
    // default when it supplied none. Reffing `capability` alone would leave a
    // late-arriving host engine unreachable behind the browser's.
    expect(CODE).toMatch(/useRef\(effective\)/);
  });

  it("disposes the session on unmount", () => {
    // A live microphone that outlives its component is the worst leak here.
    expect(CODE).toMatch(/useEffect\(\(\)\s*=>\s*\(\)\s*=>\s*session\?\.dispose\(\)/);
  });

  it("the ratchet reads real code, not an empty string", () => {
    // The control: every assertion above would pass vacuously on "".
    expect(CODE.length).toBeGreaterThan(200);
    expect(CODE).toContain("VoiceSession");
  });
});
