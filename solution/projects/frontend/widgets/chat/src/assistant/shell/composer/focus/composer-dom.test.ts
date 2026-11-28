import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The shell's composer behaviour finds the chat's composer by two DOM facts:
 * the `.composer-box` frame and the `.composer-mic` button with its
 * `data-recording` attribute. In one package that is a coupling between two
 * folders, and a rename on either side breaks dictation, focus and the caret
 * with no error: the selector just matches nothing.
 *
 * Reads sources as strings, like `voice.test.ts`, because the point is that
 * both sides name the same strings, not what either renders.
 */
const SRC = join(import.meta.dirname, "../../../..");
const read = (path: string) => readFileSync(join(SRC, path), "utf8");

describe("the shell reads the composer's DOM", () => {
  const nodes = read("assistant/shell/composer/focus/use-composer-nodes.ts");
  const recording = read("assistant/shell/composer/dictation/use-recording.ts");
  const chatComposer = read("chat/ui/chat/composer.tsx");
  const voice = read("chat/composer/controls/voice.tsx");

  it("the frame class the shell closes over is the one the chat draws", () => {
    expect(nodes).toContain(".composer-box");
    expect(chatComposer).toContain("composer-box ");
  });

  it("the microphone class and the recording attribute are the ones the chat draws", () => {
    expect(nodes).toContain(".composer-mic");
    expect(chatComposer).toContain('className="composer-mic"');
    expect(recording).toContain("data-recording");
    expect(voice).toContain("data-recording={recording || undefined}");
  });
});
