import { describe, expect, it } from "vitest";

import { planRuns } from "../../../core/run/segment";
import { selectRun } from "../../../core/run/view";
import { chunksOf, messageOf } from "../scenario/harness";
import { storedTurn } from "../scenario/stored";
import { fromStoredThread } from "../../../../assistant/session";
import { SCENARIOS, TURNS } from "./index";

describe("the scenario library", () => {
  it("holds unique ids and fills every group the overview shows", () => {
    const ids = SCENARIOS.map((scenario) => scenario.id);
    expect(new Set(ids).size).toBe(ids.length);
    expect(new Set(SCENARIOS.map((scenario) => scenario.group))).toEqual(new Set(["messages", "run", "tools", "blocks", "failures", "history", "attachments", "privacy"]));
  });

  it("reduces every turn to one assistant message without throwing", () => {
    for (const scenario of TURNS) expect(messageOf(chunksOf(scenario)).role, scenario.id).toBe("assistant");
  });

  it("is deterministic: building twice gives the same chunks", () => {
    for (const scenario of TURNS) expect(chunksOf(scenario)).toEqual(chunksOf(scenario));
  });

  it("settles the turns that have a verdict, and leaves the open ones open", () => {
    const state = (id: string) => messageOf(chunksOf(SCENARIOS.find((s) => s.id === id)!)).status.state;
    expect(state("plain-answer")).toBe("complete");
    expect(state("error-after-partial")).toBe("failed");
    expect(state("interrupted")).toBe("interrupted");
    expect(state("tool-cancelled")).toBe("interrupted");
  });

  it("closes a call that was still open when the stream ended as stopped, not failed", () => {
    const tool = messageOf(chunksOf(SCENARIOS.find((s) => s.id === "tool-cancelled")!)).parts.find((part) => part.type === "tool");
    expect(tool?.type === "tool" ? tool.meta?.status : null).toBe("cancelled");
  });

  it("reads each run's verdict and counts (the data the collapsed line is made of)", () => {
    const read = (id: string) => {
      const item = planRuns(messageOf(chunksOf(SCENARIOS.find((candidate) => candidate.id === id)!)).parts).find((entry) => entry.kind === "run");
      if (item === undefined || item.kind !== "run") return null;
      const { status, counts } = selectRun(item.part.parts);
      return `${status}: ${counts.tools} tools, ${counts.failed} failed, ${counts.cancelled} stopped`;
    };
    expect(Object.fromEntries(["hidden-thought", "tool-run", "tool-error", "tool-timeout", "tool-cancelled", "parallel-batch", "retry-chain", "long-run", "privacy", "plain-answer"].map((id) => [id, read(id)]))).toEqual({
      "hidden-thought": "ok: 0 tools, 0 failed, 0 stopped",
      "tool-run": "ok: 2 tools, 0 failed, 0 stopped",
      "tool-error": "error: 1 tools, 1 failed, 0 stopped",
      "tool-timeout": "error: 1 tools, 1 failed, 0 stopped",
      "tool-cancelled": "cancelled: 1 tools, 0 failed, 1 stopped",
      "parallel-batch": "ok: 4 tools, 0 failed, 0 stopped",
      "retry-chain": "error: 3 tools, 2 failed, 0 stopped",
      "long-run": "error: 60 tools, 1 failed, 0 stopped",
      privacy: "ok: 3 tools, 0 failed, 0 stopped",
      "plain-answer": null,
    });
  });

  it("restores a finished turn from the server's stored form, trace first, as a reload shows it", () => {
    const scenario = SCENARIOS.find((s) => s.id === "tool-run")!;
    const [user, answer] = fromStoredThread(storedTurn(scenario), "failed");
    expect(user?.role).toBe("user");
    expect(answer?.status).toEqual({ state: "complete" });
    expect(answer?.parts.map((part) => part.type)).toEqual(["tool", "tool", "data", "text"]);
  });
});

describe("the scenarios that restore a thread", () => {
  it("hold history and play no turn", () => {
    for (const id of ["restored-session", "attachments"]) {
      const scenario = SCENARIOS.find((candidate) => candidate.id === id)!;
      expect(scenario.beats, id).toEqual([]);
      expect(scenario.history?.length, id).toBeGreaterThan(0);
    }
  });

  it("keeps every attachment the conversation shows, including the expired one", () => {
    const files = SCENARIOS.find((candidate) => candidate.id === "attachments")!.history!.flatMap((message) => message.parts.filter((part) => part.type === "attachment"));
    expect(files.map((part) => (part.type === "attachment" ? part.attachment.url === "" : null))).toEqual([false, false, true]);
  });
});
