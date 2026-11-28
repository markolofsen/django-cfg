import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, screen, userEvent, waitFor, within } from "storybook/test";
import type { MediaTrack } from "../domain";

import { MediaElement } from "../element";
import { PlayerDock } from "./player-dock";

/**
 * The footer dock.
 *
 * Every story is named by the user-visible STATE, not by the props that produce
 * it (`@rules/general/executable-ui-specifications.md`). The component is pure — state
 * in as props, intents out as callbacks — so each state is reachable without a
 * store, a transport or a relay.
 */

const SONG: MediaTrack = {
  id: "mac-studio:/Users/me/Sanya.mp3",
  kind: "audio",
  src: "blob:mock-audio",
  title: "Sanya.mp3",
  machineId: "mac-studio",
  path: "~/Music",
};

const CLIP: MediaTrack = {
  id: "mac-studio:/Users/me/demo.mp4",
  kind: "video",
  src: "blob:mock-video",
  title: "demo.mp4",
  machineId: "mac-studio",
  path: "~/Movies",
};

/**
 * Artwork a story can assert on without a network.
 *
 * A data URL rather than a path: the cover route is same-origin and answers
 * nothing in Storybook, so a real URL would exercise `TrackCover`'s error
 * fallback and the story would pass by rendering the placeholder it is there to
 * rule out.
 */
const COVER_SRC =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='96'%3E%3Crect width='96' height='96' fill='%23c2410c'/%3E%3C/svg%3E";

const noop = () => undefined;

/**
 * The element the host would mount. A story supplies it because the dock never
 * BUILDS one — that is the invariant the whole package rests on, and a story
 * that constructed its own element would be testing a different component.
 */
const AUDIO_ELEMENT = <MediaElement kind="audio" src={SONG.src} data-testid="element" />;
const VIDEO_ELEMENT = (
  <MediaElement
    kind="video"
    src={CLIP.src}
    data-testid="element"
    className="size-full object-cover"
  />
);

const meta = {
  title: "Widgets/Player/Player dock",
  component: PlayerDock,
  parameters: { layout: "padded" },
  args: {
    track: SONG,
    playing: false,
    position: 64,
    duration: 220,
    // Ahead of the playhead but short of the end — the state a streamed file is
    // in for most of its life, and the only one in which the buffered range is
    // distinguishable from both an empty bar and a full one.
    buffered: 130,
    onPlay: noop,
    onPause: noop,
    onDismiss: noop,
    onScrubStart: noop,
    onScrubMove: noop,
    onScrubEnd: noop,
    volume: 0.8,
    muted: false,
    onVolumeChange: noop,
    onToggleMuted: noop,
    element: AUDIO_ELEMENT,
  },
} satisfies Meta<typeof PlayerDock>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Audio, loaded and waiting — the state the dock FIRST appears in, always.
 *
 * Autoplay is not attempted: browsers refuse sound without a user gesture, so a
 * dock that rendered as already-playing would be lying on the first track of
 * every session.
 */
export const AudioPaused: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("button", { name: "Play" })).toBeVisible();
    await expect(canvas.getByText("Sanya.mp3")).toBeVisible();
    // No machine NAME was supplied, so the subtitle names no machine at all —
    // rather than falling back to the id, which is what it used to print.
    await expect(canvas.queryByText(/mac-studio/)).toBeNull();
    await expect(canvas.getByText("1:04 / 3:40")).toBeVisible();

    // Audio has nothing to look at, so the stage is not offered. ABSENT, not
    // disabled: a door that goes nowhere is worse than no door.
    await expect(canvas.queryByRole("button", { name: "Open player" })).toBeNull();
  },
};

/**
 * The element is in the tree even for audio, and even though nothing shows it.
 *
 * This is the invariant that makes the dock the element's home: it is the thing
 * that is PLAYING. A layout that dropped it when there was no picture would stop
 * the music, and would do it silently.
 */
export const AudioKeepsTheElementMounted: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = await canvas.findByTestId("element");
    await expect(element.tagName).toBe("AUDIO");
    // Inside the dock's own frame, not floating somewhere else in the document.
    await expect(canvas.getByTestId("player-dock-frame")).toContainElement(element);
  },
};

/**
 * A track WITH artwork shows it on the row.
 *
 * The row is where the reader is looking. Before this, the only surface that
 * rendered `track.poster` was the detail panel, which is shut by default — so a
 * file whose cover the transcript had already shown on hover played behind a
 * generic glyph, and the picture was reachable only by opening a drawer.
 *
 * MUTANT: put a `<Music>` glyph back in the picture slot → this fails on the
 * image, while every other story in the file stays green.
 */
export const AudioShowsItsCover: Story = {
  args: { track: { ...SONG, poster: COVER_SRC } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const cover = await canvas.findByRole("presentation");
    await expect(cover).toHaveAttribute("src", COVER_SRC);
    // The placeholder is what a track without art gets; both must not render.
    await expect(canvas.queryByTestId("track-cover-placeholder")).toBeNull();
  },
};

/**
 * A track without artwork keeps the row's SHAPE.
 *
 * Most files carry no embedded cover, so this is the ordinary case and not an
 * error state: a tile of the same size holds the row's geometry, and the row
 * does not reflow between one track and the next.
 */
export const AudioWithoutCoverKeepsTheShape: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByTestId("track-cover-placeholder")).toBeVisible();
  },
};

/** Sound is coming out: the control offers the opposite action, as a toggle must. */
export const AudioPlaying: Story = {
  args: { playing: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("button", { name: "Pause" })).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Play" })).toBeNull();
  },
};

/**
 * Video: the dock shows the picture, and the picture is the way into the stage.
 *
 * The frame is a real `<video>`, not a poster image. It is the same element that
 * will fill the stage — one element for the life of a track is what lets opening
 * the stage cost nothing and lose nothing.
 */
export const VideoShowsAThumbnail: Story = {
  args: { track: CLIP, element: VIDEO_ELEMENT, onOpenStage: noop },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = await canvas.findByTestId("element");
    await expect(element.tagName).toBe("VIDEO");
    await expect(canvas.getByTestId("player-dock-frame")).toContainElement(element);
    // ONE way to the stage: the explicit control. The picture plays instead —
    // the same act audio's artwork performs, so one square in one row cannot
    // mean two different things depending on the file.
    await expect(canvas.getAllByRole("button", { name: "Open player" })).toHaveLength(1);
    await expect(canvas.getByRole("button", { name: "Play this track" })).toBeVisible();
  },
};

/**
 * The video tile is SQUARE, and the same edge as audio's artwork.
 *
 * It was 16:9 — geometrically right, measured at 71x40, and still read as a
 * black rectangle: `object-contain` fills whatever the source does not cover
 * with the tile's background, so any clip that is not exactly 16:9 showed bars.
 * A square paired with `object-cover` crops instead, and the row keeps one
 * shape whichever kind is playing.
 *
 * Asserted against the AUDIO tile rather than against 36, so the two cannot
 * drift apart without this failing.
 *
 * MUTANT: restore `h-10 aspect-video` → the squareness assertion fails.
 */
export const TheVideoTileIsSquare: Story = {
  // BOTH kinds in one DOM, so the audio tile's edge is read rather than written
  // down: a literal 36 would keep passing while the two tiles drifted apart.
  render: (args) => (
    <>
      <PlayerDock {...args} track={CLIP} element={VIDEO_ELEMENT} />
      <PlayerDock {...args} track={SONG} element={AUDIO_ELEMENT} />
    </>
  ),
  args: { onOpenStage: noop },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // Both docks render a frame; the video one is first.
    const frames = await canvas.findAllByTestId("player-dock-frame");
    const frame = frames[0];
    // Assert rather than destructure: an empty result would otherwise read as
    // `undefined` and fail later with a message about a property, not about the
    // frame that never rendered.
    await expect(frame).toBeDefined();
    const { width, height } = frame!.getBoundingClientRect();

    await expect(height).toBeGreaterThan(0);
    await expect(Math.abs(width - height)).toBeLessThan(1);

    const audio = canvas.getByTestId("track-cover-placeholder");
    await expect(Math.abs(audio.getBoundingClientRect().width - width)).toBeLessThan(1);
  },
};

/**
 * Clicking the thumbnail asks for the stage — an intent, never a URL.
 *
 * The picture is a real button, so the click is the same event a keyboard press
 * produces. Asserting the CALLBACK rather than a navigation is the point: this
 * package must never learn that a player route exists.
 */
export const ClickingThePictureOpensTheStage: Story = {
  args: { track: CLIP, element: VIDEO_ELEMENT, onOpenStage: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const [picture] = await canvas.findAllByRole("button", { name: "Open player" });
    if (picture) await userEvent.click(picture);
    await expect(args.onOpenStage).toHaveBeenCalledTimes(1);
  },
};

/**
 * The machine went away mid-track.
 *
 * The cause REPLACES the location line and the clock, and the meter turns red
 * rather than continuing to creep forward. A bar still advancing under "the
 * machine went offline" is the looks-healthy-while-silent shape this package
 * exists to remove.
 */
export const MachineWentOffline: Story = {
  args: {
    playing: false,
    failure: { reason: "machine-unreachable", machineId: "mac-studio" },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(
      await canvas.findByText("mac-studio went offline — playback stopped"),
    ).toBeVisible();
    // The clock is GONE, not merely styled differently.
    await expect(canvas.queryByText("1:04 / 3:40")).toBeNull();
  },
};

/**
 * The browser wants a gesture — the one failure that is not a fault.
 *
 * It must read as an instruction. Every other failure string ends "playback
 * stopped"; this one asks for a click, because the file is fine.
 */
export const BrowserWantsAClick: Story = {
  args: { failure: { reason: "blocked" } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const message = await canvas.findByText(/browser needs a click/);
    await expect(message).toBeVisible();
    await expect(message.textContent).not.toContain("stopped");
  },
};

/**
 * The track reached its end.
 *
 * "Finished" replaces the clock rather than leaving `3:40 / 3:40` on screen,
 * which reads as still playing — the same shape as an unexplained failure, just
 * milder.
 */
export const Finished: Story = {
  args: { ended: true, position: 220 },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Finished")).toBeVisible();
    await expect(canvas.queryByText("3:40 / 3:40")).toBeNull();
  },
};

/**
 * On the stage: the frame leaves the row and fills the screen.
 *
 * The element does NOT change parent — it is still inside the dock's own frame,
 * which is the whole design. Only the box moved, which is why opening the stage
 * cannot interrupt playback.
 */
export const StagedVideoFillsTheScreen: Story = {
  args: { track: CLIP, element: VIDEO_ELEMENT, staged: true, onLeaveStage: noop, onOpenStage: noop },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = await canvas.findByTestId("element");
    // Same parent as when docked. This is the assertion that matters.
    await expect(canvas.getByTestId("player-dock-frame")).toContainElement(element);
    // The full-screen picture PLAYS, which is what clicking a video does
    // everywhere. It used to be an inert wrapper here, because it was a door to
    // the stage and the reader was already on it — now it carries the same act
    // the docked row's artwork does, so the frame is never a dead target.
    await expect(canvas.getByRole("button", { name: "Play this track" })).toBeEnabled();
    // And the way back exists, because the frame covers everything above the row.
    await expect(canvas.getByRole("button", { name: "Minimize to footer" })).toBeVisible();
  },
};

/**
 * **The load-bearing story: crossing between dock and stage never recreates the
 * element.**
 *
 * A single staged render cannot show this — it would pass against a component
 * that remounts on every transition, because there would be no transition. So
 * this drives the toggle and holds the node across it.
 *
 * Verified by mutation: putting `key={staged ? "s" : "d"}` on the frame makes
 * this fail and leaves every other story green, which is exactly the failure a
 * static story misses.
 */
export const CrossingSurfacesKeepsTheSameElement: Story = {
  render: function StageToggle(args) {
    const [staged, setStaged] = useState(false);
    return (
      <>
        <button type="button" onClick={() => setStaged((s) => !s)}>Toggle</button>
        <PlayerDock {...args} staged={staged} onLeaveStage={noop} onOpenStage={noop} />
      </>
    );
  },
  args: { track: CLIP, element: VIDEO_ELEMENT },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = await canvas.findByTestId("element");
    const toggle = canvas.getByRole("button", { name: "Toggle" });

    // Dock → stage → dock. The node must be the SAME object every time, and its
    // parent must stay the dock's own frame — the element never changes owner.
    for (let i = 0; i < 2; i += 1) {
      await userEvent.click(toggle);
      await expect(canvas.getByTestId("element")).toBe(element);
      await expect(element.parentElement).toBe(canvas.getByTestId("player-dock-frame"));
    }
  },
};

/** Leaving the stage is an intent, like entering it. */
export const LeavingTheStageAsksTheHost: Story = {
  args: { track: CLIP, element: VIDEO_ELEMENT, staged: true, onLeaveStage: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: "Minimize to footer" }));
    await expect(args.onLeaveStage).toHaveBeenCalledTimes(1);
  },
};

/**
 * A track with no machine and no path.
 *
 * The subtitle is absent rather than rendering an empty line or a stray
 * separator — a track can arrive without a location and the row must still read.
 */
export const WithoutALocation: Story = {
  args: { track: { id: "x", kind: "audio", src: "blob:x", title: "clip.wav" } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("clip.wav")).toBeVisible();
    await expect(canvas.queryByText(/·/)).toBeNull();
  },
};

/**
 * ⓘ opens the metadata, for BOTH kinds.
 *
 * The panel this replaces existed only because audio had no stage — it was the
 * audio half of one question, so a video's detail had nowhere to go and its
 * path stayed on the row competing with the title. A popover costs no layout,
 * so both kinds get the same answer and the exception disappears.
 */
export const InfoIsOfferedForAudio: Story = {
  args: { track: SONG, element: AUDIO_ELEMENT, onExpandedChange: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    // Audio has nothing to watch, so the stage is still not offered.
    await expect(canvas.queryByRole("button", { name: "Open player" })).toBeNull();

    await userEvent.click(await canvas.findByRole("button", { name: SONG.title }));
    await expect(args.onExpandedChange).toHaveBeenCalledWith(true);
  },
};

/**
 * **Audio's ARTWORK plays the track.** It does not open the card.
 *
 * Starting playback is the most-used act in the row, and the cover is its
 * largest target — putting it there beats a 32px glyph at the far end, and it
 * is what every music player does. The metadata is reached from the NAME
 * instead, so neither control answers two questions.
 *
 * The label tracks the transport button rather than naming the picture: two
 * controls for one act must not announce themselves differently.
 *
 * MUTANT: make the cover a `PopoverTrigger` again → the play assertion fails.
 */
export const TheCoverPlaysTheTrack: Story = {
  args: {
    track: SONG,
    element: AUDIO_ELEMENT,
    machineName: "mac-studio",
    onPlay: fn(),
    onExpandedChange: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    // A NAME of its own, so a screen reader can tell it from the transport
    // button that drives the same act.
    const cover = canvas.getByRole("button", { name: "Play this track" });

    // It IS the artwork, not an icon button sitting beside the controls: the
    // cover is the row's leftmost element.
    await expect(cover.querySelector("img, [data-testid='track-cover-placeholder']")).not.toBeNull();

    await userEvent.click(cover);

    await expect(args.onPlay).toHaveBeenCalled();
    // The card stays shut — the cover answers one question only.
    await expect(args.onExpandedChange).not.toHaveBeenCalled();
  },
};

/** Playing, the same control offers the opposite act — as a toggle must. */
export const TheCoverPausesWhilePlaying: Story = {
  args: { track: SONG, element: AUDIO_ELEMENT, playing: true, onPause: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const cover = canvas.getByRole("button", { name: "Pause this track" });

    await userEvent.click(cover);

    await expect(args.onPause).toHaveBeenCalled();
  },
};

/**
 * Video keeps the stage AND reaches the same card — through its NAME.
 *
 * Its picture cannot carry the card, because the picture is already a door to
 * the stage and one click cannot mean two things. The name is what both kinds
 * share, which is why there is no ⓘ button on the row for either.
 *
 * MUTANT: gate the card on `!canOpenStage(track)` — the rule the old drawer
 * followed — and this fails: a video's path then has nowhere to live but the
 * row, which is what put a full absolute path under the title.
 */
export const InfoIsOfferedForVideoToo: Story = {
  render: function Render(args) {
    const [expanded, setExpanded] = useState(false);
    return <PlayerDock {...args} expanded={expanded} onExpandedChange={setExpanded} />;
  },
  args: { track: CLIP, element: VIDEO_ELEMENT, onOpenStage: fn() },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.click(await canvas.findByRole("button", { name: CLIP.title }));
    await expect(await screen.findByTestId("player-info")).toBeInTheDocument();

    // The picture still opens the stage — the two acts stay separate.
    await expect(canvas.getAllByRole("button", { name: "Open player" }).length).toBeGreaterThan(0);
  },
};

/**
 * The row shows the machine's NAME, and never its id.
 *
 * Before this the subtitle printed `b2aacd578a11b4fb477e7721bd46f912` — correct,
 * and useless. The path is gone from the row too: it has the popover now, and a
 * long path cost the machine its width and still ended in an ellipsis.
 */
export const TheRowNamesTheMachineNotItsId: Story = {
  args: { track: SONG, element: AUDIO_ELEMENT, machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("mac-studio")).toBeVisible();
    // The id and the path both belong in the popover, not on the row.
    await expect(canvas.queryByText(/Users\/me/)).toBeNull();
  },
};

/**
 * Open, the popover states what the row cannot: the path, in full on hover, and
 * whatever the file description carries.
 */
export const TheInfoPopoverStatesTheDetail: Story = {
  // Opened by CLICKING, not by mounting with `expanded: true`. Radix animates
  // the content in from a closed state, so a popover forced open at mount has
  // laid nothing out yet and its rows measure zero — which asserts nothing.
  // Driving the real control also specifies the real act.
  render: function Render(args) {
    const [expanded, setExpanded] = useState(false);
    return <PlayerDock {...args} expanded={expanded} onExpandedChange={setExpanded} />;
  },
  args: {
    track: SONG,
    element: AUDIO_ELEMENT,
    machineName: "mac-studio",
    detail: { artist: "Dikanda", album: "Muzyka Podrozna", sizeBytes: 8_400_000, codec: "mp3" },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: SONG.title }));

    // `screen`, not `canvas`: Radix renders the popover in a PORTAL, so its
    // content is outside the story's own canvas element.
    // `waitFor` around the ASSERTION, not just the query: the popover animates
    // in, so the rows are in the document before they have been laid out, and
    // only retrying the visibility check waits for that.
    const info = within(await screen.findByTestId("player-info"));
    await waitFor(async () => {
      await expect(info.getByText("Dikanda")).toBeVisible();
      await expect(info.getByText("mac-studio")).toBeVisible();
    });
  },
};

/**
 * A machine the roster no longer knows is NAMED as such, not printed as a hash.
 *
 * A track outlives the fleet it came from, so this is an ordinary state.
 */
export const AnUnknownMachineIsNamedNotHashed: Story = {
  render: function Render(args) {
    const [expanded, setExpanded] = useState(false);
    return <PlayerDock {...args} expanded={expanded} onExpandedChange={setExpanded} />;
  },
  args: { track: SONG, element: AUDIO_ELEMENT },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button", { name: SONG.title }));

    // `waitFor` around the ASSERTION, not just the query: the popover animates
    // in, so the row is in the document before it has been laid out, and only
    // retrying the visibility check waits for that.
    const info = within(await screen.findByTestId("player-info"));
    await waitFor(async () => {
      await expect(info.getByText("Unknown machine")).toBeVisible();
    });
    await expect(info.queryByText("mac-studio")).toBeNull();
  },
};

/**
 * **The load-bearing one, and the condition O6's reversal rests on:** opening
 * and closing the POPOVER must not recreate the element.
 *
 * The original design refused a popover on exactly this ground — Radix unmounts
 * a closed subtree, and taking the `<audio>` with it restarts the track. That
 * argument is about the ELEMENT, and it only bites if the popover CONTAINS it.
 * It does not: the element lives in the row's frame and nothing here moves it.
 *
 * This story is what keeps that distinction honest rather than convenient.
 * MUTANT: render the element inside `PopoverContent` → the node changes on the
 * first close and this fails.
 */
export const TogglingTheInfoPopoverKeepsTheSameElement: Story = {
  render: function Render(args) {
    const [expanded, setExpanded] = useState(false);
    return <PlayerDock {...args} expanded={expanded} onExpandedChange={setExpanded} />;
  },
  args: { track: SONG, element: AUDIO_ELEMENT },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = await canvas.findByTestId("element");
    const frame = canvas.getByTestId("player-dock-frame");
    const info = canvas.getByRole("button", { name: SONG.title });

    for (let pass = 0; pass < 3; pass += 1) {
      await userEvent.click(info);
      await expect(canvas.getByTestId("element")).toBe(element);
      await expect(element.parentElement).toBe(frame);
    }
  },
};

/**
 * The transport leads the RIGHT-hand cluster, after the title.
 *
 * Owner decision. Asserted on ORDER rather than on presence, because presence
 * is what every other story here already checks — and a move that no story can
 * see is a move nothing stops from being undone.
 *
 * MUTANT: put the transport back before `pictureNode` → this fails, while every
 * other story in the file stays green.
 */
export const TheTransportLeadsTheRightCluster: Story = {
  args: { track: SONG, element: AUDIO_ELEMENT, onExpandedChange: fn() },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const play = await canvas.findByRole("button", { name: "Play" });
    const title = canvas.getByText("Sanya.mp3");
    const mute = canvas.getByRole("button", { name: "Mute" });

    // DOCUMENT_POSITION_FOLLOWING === 4: the node argument comes after `this`.
    await expect(title.compareDocumentPosition(play) & 4).toBe(4);
    // ...and it LEADS the cluster rather than trailing it.
    await expect(play.compareDocumentPosition(mute) & 4).toBe(4);
  },
};

/**
 * The scrubber is a CONTROL, not a read-out.
 *
 * Before this the row drew a bar it never let anyone touch: a forty-minute
 * recording could be started and stopped but not moved through. The bar states
 * the position as a TIME rather than as a count of seconds — a screen reader
 * reading "sixty-four" for a track is a number with no unit.
 */
export const TheBarCanBeSeeked: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const bar = await canvas.findByRole("slider", { name: "Seek" });

    // NOT `toBeVisible`: the thumb is transparent until the row is hovered, by
    // design — an idle dock shows a hairline, not a handle. What must hold is
    // that it is in the accessibility tree and states its position as a TIME.
    await expect(bar).toBeInTheDocument();
    await expect(bar).toBeEnabled();
    await expect(bar).toHaveAttribute("aria-valuetext", "1:04 / 3:40");
  },
};

/**
 * Keyboard reaches the bar. This is what a shared primitive buys, and it is
 * asserted rather than assumed because "free with Radix" is a claim about a
 * version, not a property of the design.
 */
export const TheBarTakesTheKeyboard: Story = {
  args: {
    onScrubStart: fn(),
    onScrubEnd: fn(),
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const bar = await canvas.findByRole("slider", { name: "Seek" });

    bar.focus();
    await userEvent.keyboard("{ArrowRight}");

    // A key press is a complete gesture: it opens and commits in one act, so
    // the store gets a start and an end rather than a drag left hanging open.
    await expect(args.onScrubStart).toHaveBeenCalled();
    await expect(args.onScrubEnd).toHaveBeenCalled();
  },
};

/**
 * **The drag must not fight the clock.**
 *
 * The element keeps playing while a finger is on the thumb, so `timeupdate` and
 * the pointer are two writers of one number. This story puts the dock in the
 * mid-drag state — `scrubbing`, with the finger at 3:00 — and moves the
 * element's own clock underneath it. The bar must show the FINGER.
 *
 * Mutation check: make `SeekBar` render `position` instead of `scrubPosition`
 * while scrubbing, and this fails — which is exactly the defect the guard
 * exists to prevent, and the one the reference that omits it ships.
 */
export const DraggingDoesNotFightTheClock: Story = {
  args: {
    playing: true,
    scrubbing: true,
    scrubPosition: 180,
    // The element's clock, still advancing under the drag.
    position: 65,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const bar = await canvas.findByRole("slider", { name: "Seek" });

    // The FINGER's position, not the playhead's.
    await expect(bar).toHaveAttribute("aria-valuenow", "180");
    // And the clock beside it agrees, so the row states one position rather
    // than two that disagree.
    await expect(canvas.getByText("3:00 / 3:40")).toBeVisible();
  },
};

/**
 * A file whose length is unknown cannot be moved through, so the bar says so
 * rather than offering a control that silently does nothing.
 */
export const AnUnmeasuredFileCannotBeSeeked: Story = {
  args: { duration: 0, position: 0 },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const bar = await canvas.findByRole("slider", { name: "Seek" });

    await expect(bar).toHaveAttribute("data-disabled");
  },
};

/**
 * Volume is a control the console needs and the dock argued for years it did
 * not: OS volume is not per-tab, so turning a recording down means turning down
 * the call it plays over.
 *
 * Behind an icon rather than on the row — it is the least-used of the three
 * controls and would cost the title its width at every viewport.
 */
export const VolumeIsOneGlyphUntilItIsAsked: Story = {
  args: { onToggleMuted: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const mute = await canvas.findByRole("button", { name: "Mute" });

    // No slider on the row itself: the only slider here is the scrubber.
    await expect(canvas.getAllByRole("slider")).toHaveLength(1);

    await userEvent.click(mute);
    await expect(args.onToggleMuted).toHaveBeenCalled();
  },
};

/**
 * Muted, the glyph states the act the next press performs — not the state it is
 * in. A button labelled with its own state leaves the reader deducing what
 * pressing it will do.
 */
export const MutedOffersToRestoreTheSound: Story = {
  args: { muted: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await expect(await canvas.findByRole("button", { name: "Unmute" })).toBeVisible();
  },
};

/**
 * Where the platform will not let script set the volume — iOS, where it is
 * read-only — the slider is ABSENT and mute remains. Not a disabled slider: a
 * control that cannot work is worse than one that is not offered, and it is the
 * same rule the stage button already follows.
 */
export const WithoutVolumeControlOnlyMuteRemains: Story = {
  args: { canChangeVolume: false },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await expect(await canvas.findByRole("button", { name: "Mute" })).toBeVisible();
    await expect(canvas.getAllByRole("slider")).toHaveLength(1);
  },
};


/**
 * The NAME opens the card. It does not navigate.
 *
 * It used to jump straight to the file tree on the track's machine, which
 * leaves the page the reader was on to answer a question they had not asked.
 * The card states the same path and offers the folder as an explicit button, so
 * the act that moves you costs a deliberate second press.
 *
 * Asserting that `onOpenInFiles` is NOT called is the load-bearing half: the
 * card opening is easy to keep while the navigation quietly fires too.
 *
 * MUTANT: put `onClick={onOpenInFiles}` back on the title → this fails.
 */
export const TheTitleOpensTheCardRatherThanNavigating: Story = {
  render: function Render(args) {
    const [expanded, setExpanded] = useState(false);
    return <PlayerDock {...args} expanded={expanded} onExpandedChange={setExpanded} />;
  },
  args: { track: SONG, element: AUDIO_ELEMENT, onOpenInFiles: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.click(await canvas.findByRole("button", { name: SONG.title }));

    await expect(await screen.findByTestId("player-info")).toBeInTheDocument();
    await expect(args.onOpenInFiles).not.toHaveBeenCalled();
  },
};
