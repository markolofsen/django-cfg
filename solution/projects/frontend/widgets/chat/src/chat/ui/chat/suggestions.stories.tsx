import type { Meta, StoryObj } from "@storybook/react-vite";
import { Activity, Folder, Globe, HelpCircle, History, Monitor, Server } from "lucide-react";
import type { ReactNode } from "react";

import type { ChatCapabilities, ChatSuggestion } from "../../core/capabilities";
import { ChatProvider, createChatStore } from "../../store";
import { mockAdapter } from "../../testing";
import { ChatSuggestions } from "./suggestions";

/**
 * The starter rows an empty room offers.
 *
 * They mount in the composer's `above` slot, so they are rendered here on their
 * own rather than inside a transcript — what a story can check and a unit test
 * cannot is how the rows read as a group: one shared left edge, a row height
 * that is a comfortable target, and a title that truncates rather than wraps.
 *
 * Every story seeds `historyLoaded`. The primitive shows nothing unless the room
 * is genuinely empty, and an unanswered history fetch is not an empty room — so
 * a store left at the default renders nothing and the file would look broken.
 */
const meta = {
  title: "Widgets/Chat/Suggestions",
  component: ChatSuggestions,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ChatSuggestions>;

export default meta;
type Story = StoryObj<typeof meta>;

const ICONS: Readonly<Record<string, ReactNode>> = {
  help: <HelpCircle className="size-4 shrink-0" aria-hidden />,
  folder: <Folder className="size-4 shrink-0" aria-hidden />,
  history: <History className="size-4 shrink-0" aria-hidden />,
  activity: <Activity className="size-4 shrink-0" aria-hidden />,
  server: <Server className="size-4 shrink-0" aria-hidden />,
  screen: <Monitor className="size-4 shrink-0" aria-hidden />,
  browser: <Globe className="size-4 shrink-0" aria-hidden />,
};

// English literals rather than the dictionary: a workbench is not a locale
// surface, and reading copy here would make a story depend on which language is
// active. The SHAPE is what must match the product — a title short enough to
// scan, a prompt long enough to produce a good first turn.
const ITEMS: readonly ChatSuggestion[] = [
  {
    id: "orient",
    title: "What can you do here?",
    prompt: "What can you help me with here?",
    icon: "help",
  },
  {
    id: "project_tour",
    title: "Explain this project",
    prompt: "Give me a short tour of the project in this folder.",
    icon: "folder",
  },
  {
    id: "recent_changes",
    title: "What changed recently?",
    prompt: "Summarise the recent work in this project.",
    icon: "history",
  },
  {
    id: "service_health",
    title: "Check service health",
    prompt: "Check the health of this service.",
    icon: "activity",
  },
];

/** An empty room with history already loaded — the state these rows render in. */
function emptyStore() {
  const store = createChatStore({
    adapter: mockAdapter({ script: [] }),
    makeId: () => "id",
    now: () => 0,
  });
  store.setHistoryLoaded(true);
  return store;
}

function Room({
  items,
  icons = true,
}: {
  readonly items: readonly ChatSuggestion[];
  readonly icons?: boolean;
}) {
  const capabilities: ChatCapabilities = { suggestions: { items } };
  return (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      store={emptyStore()}
      capabilities={capabilities}
    >
      <ChatSuggestions icon={icons ? (key: string) => ICONS[key] ?? null : undefined} />
    </ChatProvider>
  );
}

export const FourItems: Story = {
  render: () => <Room items={ITEMS} />,
};

/**
 * One row is a legitimate list, not a degraded four.
 *
 * The Codex lane reaches none of the host's tools, so its room really can come
 * down to the single engine-neutral opener — and a lone row must still read as
 * an offer rather than as something that failed to load.
 */
export const OneItem: Story = {
  render: () => <Room items={ITEMS.slice(0, 1)} />,
};

/**
 * No rows at all ⇒ nothing renders.
 *
 * The capability is present and its list is empty, which is what a host reaches
 * when all three filters exclude everything. `<Suggestions>` must render NOTHING
 * — not an empty container, which would still spend the composer stack's gap and
 * push the field down for no reason.
 */
export const NoItems: Story = {
  render: () => <Room items={[]} />,
};

/**
 * A title longer than the pane.
 *
 * `sm:` reads the WINDOW, not the surface, so the chat column is often narrow
 * on a wide screen. The row truncates rather than wrapping to three lines or
 * pushing the icon out of alignment.
 */
export const LongTitleInANarrowPane: Story = {
  render: () => (
    <div className="max-w-[260px] border border-border">
      <Room
        items={[
          {
            id: "long",
            title: "Summarise everything that changed across this repository since last Tuesday",
            prompt: "Summarise everything that changed since last Tuesday.",
            icon: "history",
          },
          ...ITEMS.slice(0, 2),
        ]}
      />
    </div>
  ),
};

/**
 * Right-to-left.
 *
 * The glyph must lead on the RIGHT and the text align to it. Nothing here sets
 * a side explicitly — the row uses flex order and logical padding — so this
 * story is what proves that claim rather than restating it.
 */
export const RightToLeft: Story = {
  render: () => (
    <div dir="rtl">
      <Room
        items={[
          {
            id: "orient",
            title: "بماذا يمكنك مساعدتي؟",
            prompt: "What can you help me with here?",
            icon: "help",
          },
          {
            id: "project_tour",
            title: "اشرح لي هذا المشروع",
            prompt: "Give me a short tour of the project in this folder.",
            icon: "folder",
          },
        ]}
      />
    </div>
  ),
};

/**
 * No icons at all.
 *
 * The catalogue names glyphs as KEYS and this package ships no icon library, so
 * an unmapped key is the normal way a row ships ahead of its picture. The glyph
 * collapses rather than reserving a gap — a list where only some rows have icons
 * must not indent the rest to match.
 */
export const NoIcons: Story = {
  render: () => <Room items={ITEMS} icons={false} />,
};
