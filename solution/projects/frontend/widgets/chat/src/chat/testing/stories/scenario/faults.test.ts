import { describe, expect, it } from "vitest";

import type { ToolPart } from "../../../core/conversation/parts";
import { chunksOf, messageOf } from "./harness";
import { withFault } from "./faults";
import { scenarioById } from "../library";

const parts = (id: string, fault: Parameters<typeof withFault>[1]) => messageOf(chunksOf(withFault(scenarioById(id), fault))).parts;
const toolsOf = (id: string, fault: Parameters<typeof withFault>[1]) => parts(id, fault).filter((part): part is ToolPart => part.type === "tool");

describe("what each fault does to the transcript", () => {
  it("a duplicate step frame does not add a second row", () => {
    expect(parts("tool-run", "duplicate")).toHaveLength(parts("tool-run", "none").length);
  });

  it("a step that settles before it starts is not reopened by the late older frame", () => {
    const [first] = toolsOf("tool-run", "out-of-order");
    expect(first?.meta?.status).toBe("ok");
    expect(first?.toolState.state).toBe("output-available");
  });

  it("a dropped final frame leaves the turn without a verdict for the store to read as interrupted", () => {
    const message = messageOf(chunksOf(withFault(scenarioById("plain-answer"), "drop-terminal")));
    expect(message.status).toEqual({ state: "streaming" });
  });

  it("a timeout settles the first call as a timeout with the server's words", () => {
    const [first] = toolsOf("tool-run", "tool-timeout");
    expect(first?.meta).toMatchObject({ status: "timeout", errorCode: "timeout", retryable: true });
    expect(first?.toolState.state).toBe("output-error");
  });

  it("offline is one failed turn", () => {
    const message = messageOf(chunksOf(withFault(scenarioById("plain-answer"), "offline")));
    expect(message.parts).toEqual([]);
    expect(message.status.state).toBe("failed");
  });

  it("a fault that needs the host leaves the beats alone", () => {
    const clean = scenarioById("tool-run");
    expect(withFault(clean, "abort")).toBe(clean);
    expect(withFault(clean, "none")).toBe(clean);
  });
});
