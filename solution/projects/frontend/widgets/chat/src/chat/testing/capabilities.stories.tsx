import type { Meta, StoryObj } from "@storybook/react-vite";

import "../../styles/index.css";

import { CHAT_DICTIONARIES } from "../../i18n";
import { TURNS } from "./stories/library";
import { Capabilities } from "./stories/capabilities";
import { FAULTS, SPEEDS } from "./stories/scenario";

/**
 * Everything the chat can do, at a glance, each state drawn by the code the product ships.
 *
 * Scenarios are typed, seeded scripts of what a server sends (`testing/stories/library`). One scenario drives both
 * transports: the chunk stream a mock adapter replays and the frames the assistant's own adapter reads
 * (`parity.test.ts` holds them together). The player holds the turn: play, pause, step, jump to the end, change speed.
 * The fault injector rewrites what arrives. Light and dark come from the toolbar; the viewport from Storybook's own.
 *
 * Not drawn, because the product has no code for them: handoff cards, the "Why this answer?" sheet, a usage line,
 * streaming partial tool arguments. A cell with no code is left out, never faked.
 */
const meta = {
  title: "Widgets/Chat/Capabilities",
  component: Capabilities,
  parameters: { layout: "fullscreen", a11y: { test: "error" } },
  args: {
    mode: "player",
    scenario: "tool-run",
    transport: "frames",
    fault: "none",
    speed: 1,
    autoplay: false,
    runBlock: true,
    privacy: "default",
    argsMode: "default",
    resultMode: "default",
    labelsOnly: false,
    showReasoningText: false,
    defaultOpen: false,
    dir: "ltr",
    locale: "en",
  },
  argTypes: {
    mode: { control: "inline-radio", options: ["overview", "player"] },
    scenario: { control: "select", options: TURNS.map((scenario) => scenario.id) },
    transport: { control: "inline-radio", options: ["frames", "chunks"], description: "frames: through the assistant's own adapter. chunks: straight to the transcript." },
    fault: { control: "select", options: [...FAULTS] },
    speed: { control: "select", options: [...SPEEDS], description: "Infinity plays it all at once." },
    privacy: { control: "inline-radio", options: ["default", "public", "admin"] },
    argsMode: { control: "select", options: ["default", "hidden", "keys", "masked", "full"] },
    resultMode: { control: "select", options: ["default", "hidden", "preview", "full"] },
    dir: { control: "inline-radio", options: ["ltr", "rtl"] },
    locale: { control: "select", options: Object.keys(CHAT_DICTIONARIES), description: "The widget's own words. What the scenarios say is the server's, in English." },
  },
} satisfies Meta<typeof Capabilities>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Every state on one page, settled. Replay any cell to watch it arrive. */
export const Overview: Story = { args: { mode: "overview" } };

/**
 * One scenario, held in your hand. Pick it, press Play, Step through it, break it with a fault,
 * change what a reader may see, flip to right-to-left or another language.
 */
export const Player: Story = {};

/** A public chat: titles, statuses and one-line summaries. Nothing else leaves the Run block. */
export const PublicVisitor: Story = { args: { scenario: "privacy", privacy: "public", autoplay: true, speed: Number.POSITIVE_INFINITY } };

/** A signed-in admin: arguments and results in full, masked where the server masked, absent where it kept them back. */
export const Admin: Story = { args: { scenario: "privacy", privacy: "admin", defaultOpen: true, autoplay: true, speed: Number.POSITIVE_INFINITY } };

/** The reader's language and direction: the widget's own words and its mirrored layout. */
export const Arabic: Story = { args: { scenario: "tool-error", locale: "ar", dir: "rtl", autoplay: true, speed: Number.POSITIVE_INFINITY } };

/** The stream is cut, then the stored answer is loaded from the server and replaces the partial one. */
export const Reconnect: Story = { args: { scenario: "plain-answer", fault: "reconnect", autoplay: true, speed: 4 } };
