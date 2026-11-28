import { describe, expect, it } from "vitest";

import { machineTrack, mediaTitleFromPath, mediaTrackId } from "./types";

/**
 * `machineTrack` exists because a track used to be assembled by hand at every
 * entry point, and an optional field added to the type reached one of them. The
 * tests that earn their keep here are the ones that would have caught that:
 * what the constructor puts in WITHOUT being asked, and what it refuses to
 * invent.
 */

const INPUT = {
  kind: "audio",
  src: "/dl",
  machineId: "m1",
  path: "/var/music/song.mp3",
} as const;

describe("machineTrack", () => {
  it("keys identity on the pair, never on the URL that plays it", () => {
    // MUTANT: key on `src` → one file reaches the store as two tracks, because
    // video plays from a playlist URL and the same file downloads from another.
    const download = machineTrack(INPUT);
    const playlist = machineTrack({ ...INPUT, src: "/media/playlist?pin=1234" });
    expect(download.id).toBe(playlist.id);
    expect(download.id).toBe(mediaTrackId("m1", "/var/music/song.mp3"));
  });

  it("titles from the path when the caller has no better name", () => {
    expect(machineTrack(INPUT).title).toBe(mediaTitleFromPath("/var/music/song.mp3"));
  });

  it("prefers the caller's title, which is the file's own", () => {
    // An ID3 title is what the file calls itself; a basename is what a
    // downloader called it. The row shows the former when it exists.
    expect(machineTrack({ ...INPUT, title: "Ederlezi" }).title).toBe("Ederlezi");
  });

  it("falls back to the path for an empty title rather than rendering blank", () => {
    // A stripped tag arrives as "", which is falsy but not absent — a naive
    // `title ?? basename` would put an empty string on the row.
    expect(machineTrack({ ...INPUT, title: "" }).title).toBe("song.mp3");
  });

  it("omits the poster key entirely when there is no artwork", () => {
    // Not `poster: undefined`: the store persists tracks and compares them, and
    // a present-but-undefined key is a difference that reads as a change.
    expect("poster" in machineTrack(INPUT)).toBe(false);
    expect("poster" in machineTrack({ ...INPUT, poster: undefined })).toBe(false);
  });

  it("carries the poster the caller supplies", () => {
    const track = machineTrack({ ...INPUT, poster: "/cover.jpg" });
    expect(track.poster).toBe("/cover.jpg");
  });

  it("always carries the pair, so a surface can name where a track came from", () => {
    // The dock's subtitle and "open in files" both read these. A constructor
    // that dropped them would leave a playing track with no origin.
    const track = machineTrack(INPUT);
    expect(track.machineId).toBe("m1");
    expect(track.path).toBe("/var/music/song.mp3");
  });
});
