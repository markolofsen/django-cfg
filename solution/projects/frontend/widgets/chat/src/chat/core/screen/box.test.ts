import { describe, expect, it } from "vitest";

import { pushLayer, reconcileLayers, releaseLayer, settleLayers } from "./index";
import { boxVars, readViewportBox } from "./box";

const vv = (height: number, offsetTop = 0, width = 390, offsetLeft = 0) => ({ width, height, offsetTop, offsetLeft });

describe("readViewportBox", () => {
  it("no keyboard: the box is the window", () => {
    const b = readViewportBox(vv(800), 800, 800);
    expect(b).toMatchObject({ height: 800, width: 390, top: 0, left: 0, kb: 0, keyboard: false });
  });

  it("iOS keyboard: the layout viewport stays tall, the box is the visible part", () => {
    const b = readViewportBox(vv(480), 800, 800);
    expect(b.kb).toBe(320);
    expect(b.height).toBe(480);
    expect(b.keyboard).toBe(true);
  });

  it("iOS pans the page: the offset moves the box, and is not counted as keyboard", () => {
    const b = readViewportBox(vv(480, 60), 800, 800);
    expect(b.top).toBe(60);
    expect(b.kb).toBe(260);
  });

  it("Android resizes the layout viewport: the shrink against the baseline is the signal", () => {
    const b = readViewportBox(vv(480), 480, 800);
    expect(b.kb).toBe(0);
    expect(b.keyboard).toBe(true);
  });

  it("a collapsing URL bar is not a keyboard", () => {
    expect(readViewportBox(vv(740), 740, 800).keyboard).toBe(false);
  });

  it("never reports negative offsets (rubber-banding past the top)", () => {
    const b = readViewportBox(vv(800, -12, 390, -4), 800, 800);
    expect(b.top).toBe(0);
    expect(b.left).toBe(0);
  });

  it("carries pinch-zoom width and left offset", () => {
    const b = readViewportBox(vv(800, 0, 200, 50), 800, 800);
    expect(b).toMatchObject({ width: 200, left: 50 });
  });
});

describe("boxVars", () => {
  it("names every property the stylesheet reads", () => {
    const vars = boxVars(readViewportBox(vv(480, 10), 800, 800));
    expect(Object.keys(vars).sort()).toEqual(["--kb", "--vv-left", "--vv-top", "--vvh", "--vvw"]);
    expect(vars["--vvh"]).toBe("480px");
    expect(vars["--vv-top"]).toBe("10px");
  });
});

describe("the layer stack", () => {
  it("Back closes the top layer, and only the live ones above the new depth", () => {
    let e = pushLayer([], "a");
    e = pushLayer(e, "b");
    const r = reconcileLayers(e, 1);
    expect(r.closed).toEqual(["b"]);
    expect(r.entries.map((x) => x.id)).toEqual(["a"]);
  });

  it("a layer closed from inside leaves a dead entry that settles away", () => {
    let e = pushLayer([], "a");
    e = releaseLayer(e, "a");
    expect(settleLayers(e)).toEqual({ entries: [], pop: 1 });
  });

  it("a layer closed from inside pops its entry while the page is still on it", () => {
    const e = releaseLayer(pushLayer([], "a"), "a");
    expect(settleLayers(e, 1)).toEqual({ entries: [], pop: 1 });
  });

  it("a navigation over the layer's entry is not undone when the layer unmounts (sign-in button, link)", () => {
    // The page is on an entry of its own now (depth 0): going back would return the reader to the page they left.
    const e = releaseLayer(pushLayer([], "a"), "a");
    expect(settleLayers(e, 0)).toEqual({ entries: [], pop: 0 });
  });

  it("a dead entry under a live layer waits for it", () => {
    let e = pushLayer(pushLayer([], "a"), "b");
    e = releaseLayer(e, "a");
    expect(settleLayers(e).pop).toBe(0);
  });
});
