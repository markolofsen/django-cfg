import type { Meta, StoryObj } from "@storybook/react-vite";

import { draftStorageKey } from "../../core";
import { ComposerHarness } from "./harness";

/**
 * An unsent draft, kept across a reload.
 *
 * The rules are pure and tested (`core/compose/draft-storage.ts`); what an assertion
 * cannot reach is whether a restored draft actually arrives in the field, since
 * this workspace has no jsdom. These stories are that rung.
 *
 * Each story owns its OWN room key. A shared one would let the text typed in
 * one story reappear in the next, which looks like the feature working and is
 * actually two stories sharing state.
 */
const meta = {
  title: "Widgets/Chat/Composer/Draft persistence",
  component: ComposerHarness,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ComposerHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Seed storage the way a previous session would have left it.
 *
 * At module scope, so the value is already there when the story mounts — a
 * write inside the render would race the restore effect that reads it.
 * Guarded because Storybook also builds these files where storage may throw.
 */
function seed(room: string, text: string): string {
  try {
    globalThis.sessionStorage?.setItem(draftStorageKey(room), text);
  } catch {
    // Without storage the story shows an empty composer, which is the honest
    // rendering of "nothing was restored" rather than a broken frame.
  }
  return room;
}

const RESTORED = seed(
  "story-restored",
  "the half-written question I had before the tab reloaded",
);

/**
 * Restored.
 *
 * The field carries text nobody typed in this session — it came back from
 * `sessionStorage`, exactly as it would after an accidental reload. Send it,
 * and the entry is removed: the draft is gone because it is no longer a draft.
 */
export const Restored: Story = {
  args: { draftRoom: RESTORED },
};

/**
 * A room with nothing stored.
 *
 * The empty composer, and the point is that it is empty: an absent entry and an
 * entry holding `""` must both leave the field alone. Type here, then switch to
 * `Restored` and back — what you typed returns.
 */
export const NothingStored: Story = {
  args: { draftRoom: "story-empty" },
};

/**
 * Persistence off.
 *
 * No room, so nothing is read or written and the draft dies with the mount.
 * This is every other composer story, and the default for a host that does not
 * opt in.
 */
export const NotPersisted: Story = {
  args: {},
};
