import { describe, expect, it } from "vitest";

import { trackFromLink } from "./link-track";

const PLAYLIST = "/api/admin/machines/m1/media/playlist?path=%2Fa%2Fclip.mp4&pin=1234";

describe("trackFromLink", () => {
  it("names the file by machine+path, not by the URL that plays it", () => {
    // MUTANT: key the id on `src` → the same file reaches the store as two
    // different tracks, because video plays from a playlist URL and the same
    // file downloads from another.
    const fromPlaylist = trackFromLink("m1", "/a/clip.mp4", {
      kind: "video",
      src: PLAYLIST,
    });
    const fromDownload = trackFromLink("m1", "/a/clip.mp4", {
      kind: "video",
      src: "/api/admin/machines/m1/files/download?path=%2Fa%2Fclip.mp4",
    });
    expect(fromPlaylist?.id).toBe(fromDownload?.id);
    expect(fromPlaylist?.id).toBe("m1:/a/clip.mp4");
  });

  it("carries the pair for display and navigation, and titles from the path", () => {
    const track = trackFromLink("m1", "/var/music/song.mp3", {
      kind: "audio",
      src: "/dl",
      poster: "/cover?path=%2Fvar%2Fmusic%2Fsong.mp3",
    });
    expect(track).toEqual({
      id: "m1:/var/music/song.mp3",
      kind: "audio",
      src: "/dl",
      title: "song.mp3",
      machineId: "m1",
      path: "/var/music/song.mp3",
      // Supplied, not derived: this module names no routes. A track opened
      // cold from an address has no description in hand, so the caller's cover
      // route is the only thing that can put artwork on the row. A file without
      // artwork answers 204 and `TrackCover` falls back — an absent picture is
      // not an error.
      poster: "/cover?path=%2Fvar%2Fmusic%2Fsong.mp3",
    });
  });

  it("resolves to nothing when the file is not playable", () => {
    // A pasted link to a `.txt` is an address with no track behind it, not an
    // error — the stage renders that as its empty state.
    expect(trackFromLink("m1", "/a/notes.txt", { kind: undefined, src: "/dl" })).toBeNull();
  });

  it("never puts the credential-carrying URL anywhere but `src`", () => {
    // MUTANT: build the id or the title from `src` → the credential lands in a
    // value the store persists and the dock renders.
    const track = trackFromLink("m1", "/a/clip.mp4", { kind: "video", src: PLAYLIST });
    expect(track?.id).not.toContain("pin");
    expect(track?.title).not.toContain("pin");
    expect(track?.path).not.toContain("pin");
    // The poster must not be reachable from `src` either: rewriting the
    // playable URL to reach artwork would carry the credential into an `<img>`
    // URL, which lands in the DOM and in the network log. It is absent here
    // because the caller did not supply one — never inferred.
    expect(track?.poster).toBeUndefined();
  });
});
