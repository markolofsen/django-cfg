import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";

import { fitDescription, ogFooter } from "./card";
import { titleSizeFor } from "./render";

/**
 * The text budget behind every Open Graph card.
 *
 * The cards themselves are drawn on the server (`next/og`, satori) and returned
 * as a 1200x630 PNG, so there is nothing to mount here. What can be seen in a
 * browser is the part a card's author controls: how the title length steps the
 * type size, how much description is left after that, and how the footer joins
 * the facts that exist. The frame never clips, so these three numbers are the
 * only thing keeping text out of the footer.
 */
function Budget({ title, description, footer }: { title: string; description: string; footer: string }) {
  const [t, setT] = useState(title);
  const [d, setD] = useState(description);
  const [f, setF] = useState(footer);
  const fitted = fitDescription(t, d);
  const line = ogFooter(...f.split("|"));
  return (
    <div className="grid max-w-3xl gap-6">
      <label className="grid gap-1 text-sm">
        Title
        <input className="rounded-md border border-border bg-background px-3 py-2" value={t} onChange={(e) => setT(e.target.value)} />
      </label>
      <label className="grid gap-1 text-sm">
        Description
        <textarea className="rounded-md border border-border bg-background px-3 py-2" rows={3} value={d} onChange={(e) => setD(e.target.value)} />
      </label>
      <label className="grid gap-1 text-sm">
        Footer facts, separated by |
        <input className="rounded-md border border-border bg-background px-3 py-2" value={f} onChange={(e) => setF(e.target.value)} />
      </label>
      <dl className="grid grid-cols-[10rem_1fr] gap-x-4 gap-y-2 text-sm">
        <dt className="text-muted-foreground">Title size</dt>
        <dd>{titleSizeFor(t)} px ({t.length} characters)</dd>
        <dt className="text-muted-foreground">Description on card</dt>
        <dd>{fitted ?? "none: the title takes the space"}</dd>
        <dt className="text-muted-foreground">Footer</dt>
        <dd>{line ?? "none: no facts"}</dd>
      </dl>
    </div>
  );
}

const meta = {
  title: "Widgets/Ogimage/Card budget",
  component: Budget,
  args: {
    title: "The Spirit of the Bahamas",
    description: "A short film about a family sailing between islands, shot on one camera over a single summer.",
    footer: "Film|1998|Bahamas",
  },
} satisfies Meta<typeof Budget>;

export default meta;
type Story = StoryObj<typeof meta>;

/** A short title: the largest type, and room for a full description. */
export const Short: Story = {};

/** From 35 characters the type steps down to 66 px and the description budget shrinks to 92. */
export const Medium: Story = {
  args: { title: "A very long title for a short film at sea" },
};

/** Past 44 characters the title owns the card, so the description is dropped, never overflowed. */
export const Long: Story = {
  args: { title: "An exceptionally long title that would wrap onto a third line of the card" },
};

/** Absent facts leave no stray separator. */
export const MissingFacts: Story = {
  args: { footer: "Film||Bahamas" },
};
