import type { Meta, StoryObj } from "@storybook/react-vite";

import { SeededAvatar } from "./seeded-avatar";

/**
 * A face derived from a seed, drawn in a style the same seed chooses.
 *
 * The variety is the product claim, and it is the one thing a unit test cannot
 * check — six art styles either read as six different hands or they do not. That
 * is what these grids are for: look at them, do not count them.
 *
 * The predecessor pinned a single art style, so a roster column was one drawing
 * repeated with different hair. `Roster` below is the before/after: every tile
 * is a different seed, and no two adjacent ones should look like the same
 * illustrator.
 */
const meta = {
  title: "Widgets/Avatar/Seeded",
  component: SeededAvatar,
  parameters: { a11y: { test: "error" } },
} satisfies Meta<typeof SeededAvatar>;

export default meta;
type Story = StoryObj<typeof meta>;

function Grid({ seeds, kind, size }: { seeds: string[]; kind?: "person" | "room"; size: number }) {
  return (
    <div className="flex flex-wrap gap-2">
      {seeds.map((seed) => (
        <span key={seed} className="overflow-hidden rounded-full" title={seed}>
          <SeededAvatar seed={seed} kind={kind} size={size} />
        </span>
      ))}
    </div>
  );
}

const AGENTS = Array.from({ length: 36 }, (_, i) => `cid_agent_${i}`);
const ROOMS = Array.from({ length: 18 }, (_, i) => `room_${i}`);

/** What a rail actually looks like: three dozen agents, at the size a row uses. */
export const Roster: Story = {
  args: { seed: "cid_agent_0" },
  render: () => <Grid seeds={AGENTS} size={36} />,
};

/**
 * Rooms, drawn from the abstract corpus.
 *
 * The point is the SILHOUETTE: set beside `Roster`, these must read as places
 * rather than as people, before any glyph or label is involved.
 */
export const Rooms: Story = {
  args: { seed: "room_0" },
  render: () => <Grid seeds={ROOMS} kind="room" size={36} />,
};

/**
 * A mixed column — the real test of the two corpora.
 *
 * A reader should be able to say which rows are rooms without reading a word.
 */
export const RoomsAmongAgents: Story = {
  args: { seed: "cid_agent_0" },
  render: () => (
    <div className="flex flex-col gap-1">
      {["cid_agent_1", "room_a", "cid_agent_2", "cid_agent_3", "room_b", "cid_agent_4"].map((seed) => (
        <span key={seed} className="flex items-center gap-2">
          <span className="overflow-hidden rounded-full">
            <SeededAvatar seed={seed} kind={seed.startsWith("room") ? "room" : "person"} size={36} />
          </span>
          <span className="text-sm text-muted-foreground">{seed}</span>
        </span>
      ))}
    </div>
  ),
};

/** At the sizes a host actually uses, smallest first. A style that only
 *  works large is not usable here — the roster row is 36px and the group
 *  member picker is 24px. */
export const Sizes: Story = {
  args: { seed: "cid_size_demo" },
  render: () => (
    <div className="flex items-end gap-3">
      {[24, 28, 32, 36, 80, 96].map((size) => (
        <span key={size} className="overflow-hidden rounded-full">
          <SeededAvatar seed="cid_size_demo" size={size} />
        </span>
      ))}
    </div>
  ),
};
