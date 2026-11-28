import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The consumer ratchet: voice logic must reach a screen.
 *
 * This guards a defect no other rung could see. `core/voice` shipped a 168-line
 * state machine with 228 lines of passing tests, exported from the package root
 * — and NO component mounted it and no story rendered it. Types were clean,
 * every test was green, and the feature did not exist for a user: `voice`
 * appears in zero `.tsx` files, against six wired
 * neighbours (mentions 25, media 8, attachments 5, focus 3, paste 2) which are
 * the control proving the probe can see a wired subsystem.
 *
 * Same class as the Go side's extracted-then-dropped cover art: the missing
 * piece was a CONSUMER, not an implementation. A unit test cannot fail on it,
 * because the unit was never the problem.
 */

const read = (name: string) =>
  readFileSync(new URL(name, import.meta.url), "utf8")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\/\/.*$/gm, "");

const BUTTON = read("./voice.tsx");
/**
 * The one assembly every surface mounts.
 *
 * `ui/chat/chat.tsx` renders it and so does a host shell — which is the point: while
 * a host could compose the parts by hand, "the shipped assembly" was whichever
 * file that host happened to write, and a control it forgot was invisible here.
 * The queue shipped unrendered for exactly that reason.
 */
const CHAT = read("../../ui/chat/composer.tsx");
const HARNESS = read("../stories/harness.tsx");
const STORIES = read("../stories/composer.stories.tsx");
/** The draft owns the send, so the seam that ends dictation is read from there. */
const DRAFT = read("../../store/composing/use-draft.ts");
/** Recording APPEARANCE lives in CSS, because a utility loses to hover. */
const STYLES = read("../../../styles/composer.css");

describe("the ratchet reads real code (control)", () => {
  it("every source read has content after stripping comments", () => {
    // Every assertion below would pass vacuously on "".
    for (const [name, code] of [
      ["voice", BUTTON],
      ["ui/chat/composer", CHAT],
      ["harness", HARNESS],
      ["stories", STORIES],
      ["store/composing/use-draft", DRAFT],
      ["styles/composer.css", STYLES],
    ] as const) {
      expect(code.length, `${name} read as empty`).toBeGreaterThan(200);
    }
  });
});

describe("dictation reaches a screen", () => {
  it("is mounted by the SHIPPED assembly, not only by the workbench", () => {
    // MUTANT: delete <ComposerVoice> from ui/chat/composer.tsx → this dies.
    // The workbench alone is not enough: a story can render a component the
    // product never mounts, which is a demo, not a feature.
    expect(CHAT).toContain("<ComposerVoice");
    expect(CHAT).toContain("ComposerVoice");
  });

  it("is mounted by the workbench, so a story can exercise it", () => {
    expect(HARNESS).toContain("<ComposerVoice");
  });

  it("has at least one story passing a voice capability", () => {
    // MUTANT: remove `voice:` from the stories → this dies. A story that
    // renders the harness without the capability renders no button at all.
    expect(STORIES).toMatch(/voice:\s*mockVoice\(/);
  });
});

describe("the button obeys the absent-not-stubbed rule", () => {
  it("renders nothing when the capability is absent", () => {
    // MUTANT: change to a `disabled` prop → this dies. A greyed-out mic on a
    // browser without speech support is a promise the product cannot keep.
    expect(BUTTON).toMatch(/if\s*\(!available \|\| touch\)\s*return null/);
  });

  it("is absent on a touch device, where the keyboard already dictates", () => {
    // MUTANT: drop `touch` from the guard → this dies. The mic and its language picker are a duplicate tile on a phone.
    expect(BUTTON).toMatch(/const touch = useIsTouch\(\)/);
  });

  it("takes its glyph as a function of `recording`", () => {
    // A static node cannot express a glyph that must change with state — the
    // same reason ComposerSend's children are a function. And an omitted
    // children is how Send renders a blank blue pill, so both
    // assemblies must pass one.
    expect(BUTTON).toContain("children?.(recording)");
    expect(CHAT).toMatch(/\(recording\)\s*=>/);
    expect(HARNESS).toMatch(/\(recording\)\s*=>/);
  });

  it("names itself for a screen reader, and announces its toggle state", () => {
    // The one control whose meaning cannot be read off its icon. Asserted as
    // the derivation PLUS the binding, not one literal: the label is prepared
    // before JSX because the tooltip renders the same string.
    expect(BUTTON).toContain("const micLabel = recording ? copy.stop : copy.start");
    expect(BUTTON).toContain("aria-label={micLabel}");
    expect(BUTTON).toContain("aria-pressed={recording}");
  });

  it("anchors the transcript onto text already typed", () => {
    // MUTANT: `setText(text)` → this dies. Without the anchor, dictating into a
    // half-written message replaces it.
    expect(BUTTON).toContain("anchor.current");
    expect(BUTTON).toMatch(/setText\(anchor\.current === ""/);
  });

  it("gates the write on an explicit arm, never on the text being non-empty", () => {
    // MUTANT: `if (text === "") return;` → this dies.
    //
    // The two guards look equivalent and are not. `start()` emits an EMPTY
    // snapshot, so an empty-text gate cannot distinguish "nothing dictated yet"
    // from "this session is over" — which lets a settled transcript be
    // re-applied by a later render, on top of what the user has typed since.
    //
    // Deliberately NOT guarded against: a second dictation appending to the
    // first. That is correct — pressing the mic twice means dictating twice.
    expect(BUTTON).toMatch(/if\s*\(!armed\.current\)\s*return/);
    expect(BUTTON).not.toMatch(/if\s*\(text === ""\)\s*return/);
  });

  it("dismisses its panel on an outside press and on Escape", () => {
    // MUTANT: delete the useDismiss call → this dies.
    //
    // The regression it guards shipped as MARKUP that looked right. The panel
    // was a plain element with no document-level listener, so nothing but its
    // own trigger could close it — clicking away left it open over the
    // transcript. Both refs are named because the trigger must count as inside;
    // see use-dismiss.test.ts for why.
    expect(BUTTON).toMatch(/useDismiss\(\{[\s\S]*?refs: \[panelRef, triggerRef\]/);
    expect(BUTTON).toContain("ref={panelRef}");
    expect(BUTTON).toContain("ref={triggerRef}");
  });

  it("puts the options trigger LEFT of the mic", () => {
    // MUTANT: swap the two → this dies. The mic is the control the user aims
    // for and the one that must stay adjacent to Send; an options button
    // between them makes the action bar read as two competing primary buttons.
    // Asserted by ORDER of appearance, which is what the eye reads.
    const trigger = BUTTON.indexOf("aria-haspopup=\"dialog\"");
    const micLast = BUTTON.lastIndexOf("{mic}");
    expect(trigger).toBeGreaterThan(-1);
    expect(micLast).toBeGreaterThan(trigger);
  });

  it("switches views inside ONE panel rather than opening a second popover", () => {
    // Nesting one floating surface inside another makes both fight over the
    // same outside-press, and a search box inside the inner one loses keys to
    // the outer. The reference this was ported from records the same finding.
    expect(BUTTON).toMatch(/useState<"main" \| "language">/);
    expect(BUTTON).toMatch(/view === "language"/);
  });

  it("shows the current language WITHOUT opening the list", () => {
    // The state that breaks dictation must be readable at the point where it
    // fails: a user whose transcript is nonsense has to see what it listened
    // for. `languageLabel` resolves the tag to a name on the main view.
    expect(BUTTON).toContain("languageLabel(language.value)");
  });

  it("ends dictation when the draft is sent, through the DRAFT's seam", () => {
    // MUTANT: delete the `onSend(...)` effect → this dies, and the reported
    // defect returns: the engine keeps listening after the message goes out.
    //
    // Read from `use-draft` rather than from the send BUTTON on purpose. There
    // are three send doors — the button, the form's submit, and Enter, which
    // `field/input.tsx` handles itself after preventing the submit — and they
    // share only `useDraft.send`. A hook on the button alone leaves Enter
    // dictating on, which is the door people actually use while speaking.
    expect(DRAFT).toMatch(/onSend: \(listener: \(\) => void\) => \(\) => void/);
    expect(DRAFT).toMatch(/for \(const listener of sendListeners\.current\) listener\(\)/);
    expect(BUTTON).toMatch(/onSend\(\(\) => \{/);
  });

  it("CANCELS on send rather than stopping, so the sent words do not come back", () => {
    // MUTANT: swap `cancel()` for `stop()` → this dies, and the second half of
    // the report returns. `stop` COMMITS the in-flight interim, and the draft it
    // commits into was just cleared by the send — so the message the user
    // already sent reappears in the empty field as if retyped.
    //
    // Asserted on the listener body, not on the file: `stop` legitimately
    // appears elsewhere here as the mic button's own toggle.
    const listener = /onSend\(\(\) => \{([\s\S]*?)\}\)/.exec(BUTTON)?.[1] ?? "";
    expect(listener, "the onSend listener was not found").not.toBe("");
    expect(listener).toContain("cancel()");
    expect(listener).not.toContain("stop()");
  });

  it("disarms the write gate on send, since `armed` is not the session's", () => {
    // MUTANT: drop `armed.current = false` → this dies. `cancel` emits one last
    // empty snapshot, and an effect still armed writes it straight into the
    // fresh draft.
    const listener = /onSend\(\(\) => \{([\s\S]*?)\}\)/.exec(BUTTON)?.[1] ?? "";
    expect(listener).toContain("armed.current = false");
  });

  it("fires the listeners BEFORE the send and the clear", () => {
    // MUTANT: move the loop below the `setDraft(` clear → this dies. Order is
    // the whole point: a listener runs while the draft it is ending against is
    // still the one the user sent.
    const body = /const send = useCallback\(\(\) => \{([\s\S]*?)\}, \[/.exec(DRAFT)?.[1] ?? "";
    expect(body, "send() body was not found").not.toBe("");
    const fired = body.indexOf("listener()");
    const sent = body.indexOf("store.send(");
    // The clear keeps a private recipient, so it is `setDraft(recipient === … ? emptyDraft : { …emptyDraft, to })`.
    const cleared = body.indexOf("setDraft(");
    expect(fired).toBeGreaterThan(-1);
    expect(fired).toBeLessThan(sent);
    expect(fired).toBeLessThan(cleared);
  });

  it("marks the recording state as DATA, so the stylesheet can own it", () => {
    // MUTANT: drop `data-recording` → this dies, and the glyph neither turns
    // nor keeps its ring. `aria-pressed` cannot carry it: as a Tailwind variant
    // it ties with the button's own `hover:text-foreground` on specificity, so
    // source order decides and the icon goes white under the pointer — which is
    // where the pointer is, since the user just clicked to start.
    expect(BUTTON).toContain("data-recording={recording || undefined}");
    expect(STYLES).toMatch(/\.composer-mic\[data-recording\][\s\S]*?:hover/);
  });

  it("keeps the recording colour out of the assembly's class list", () => {
    // MUTANT: put `aria-pressed:text-destructive` back on the mic → this dies.
    // Two owners for one appearance, and the utility is the one that loses to
    // hover, so the bug returns while the CSS still looks correct.
    expect(CHAT).toContain("composer-mic");
    expect(CHAT).not.toContain("aria-pressed:text-destructive");
  });

  it("disarms once the session has settled", () => {
    // Left armed, a later unrelated render re-applies the same transcript on
    // top of whatever the user has typed since.
    expect(BUTTON).toMatch(/armed\.current = false/);
    expect(BUTTON).toMatch(/armed\.current = true/);
  });
});
