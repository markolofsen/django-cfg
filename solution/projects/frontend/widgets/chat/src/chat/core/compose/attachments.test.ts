import { describe, expect, it } from "vitest";

import {
  DEFAULT_MAX_FILE_BYTES,
  DEFAULT_MAX_FILES,
  formatBytes,
  kindOf,
  rejectionFor,
  resolveAttachments,
  type AttachmentsCapability,
} from "./attachments";

const upload: AttachmentsCapability["upload"] = async () => ({ url: "u" });
const f = (name: string, type: string, size = 100) => ({ name, type, size });

describe("resolveAttachments", () => {
  it("fills the documented defaults", () => {
    const r = resolveAttachments({ upload });
    expect(r.kinds).toEqual(["image", "audio", "text", "document"]);
    expect(r.maxFileSize).toBe(DEFAULT_MAX_FILE_BYTES);
    expect(r.maxFiles).toBe(DEFAULT_MAX_FILES);
  });

  it("builds accept from kinds plus the host's extras, without duplicates", () => {
    const r = resolveAttachments({ upload, kinds: ["image"], accept: [".zip", "image/*"] });
    expect(r.accept).toEqual(["image/*", ".zip"]);
  });
});

describe("kindOf", () => {
  it("reads MIME first", () => {
    expect(kindOf(f("a.bin", "image/webp"))).toBe("image");
    expect(kindOf(f("a.bin", "audio/ogg"))).toBe("audio");
    expect(kindOf(f("a.bin", "video/mp4"))).toBe("video");
  });
  it("falls back to the extension for an empty type (.md)", () => {
    expect(kindOf(f("notes.md", ""))).toBe("text");
  });
  it("calls the rest a document", () => {
    expect(kindOf(f("a.pdf", "application/pdf"))).toBe("document");
  });
});

describe("rejectionFor", () => {
  const r = resolveAttachments({ upload, kinds: ["image", "text"], maxFileSize: 1000, maxFiles: 2 });
  it("accepts a matching file", () => {
    expect(rejectionFor(f("a.png", "image/png"), 0, r)).toBeNull();
    expect(rejectionFor(f("a.md", ""), 0, r)).toBeNull();
  });
  it("refuses a kind that was not enabled", () => {
    expect(rejectionFor(f("a.mp3", "audio/mpeg"), 0, r)).toBe("type");
  });
  it("refuses an oversize file and a full turn", () => {
    expect(rejectionFor(f("a.png", "image/png", 2000), 0, r)).toBe("size");
    expect(rejectionFor(f("a.png", "image/png"), 2, r)).toBe("count");
  });
  it("reports the type before the count", () => {
    expect(rejectionFor(f("a.mp3", "audio/mpeg"), 2, r)).toBe("type");
  });
});

describe("formatBytes", () => {
  it("scales", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(10 * 1024 * 1024)).toBe("10 MB");
  });
});
