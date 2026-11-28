import type { Meta, StoryObj } from "@storybook/react-vite";
import { File, Globe, Image, Mic, Terminal } from "lucide-react";
import type { ReactNode } from "react";
import { expect, userEvent, waitFor, within } from "storybook/test";

import type { ChatCapabilities, ToolCatalogEntry } from "../../core";
import { ChatProvider } from "../../store";
import { mockAdapter, MOCK_TOOL_CATALOGUE, MOCK_TOOL_CATALOGUE_NO_STT } from "../../testing";
import { ChatComposer } from "../../ui/chat/composer";

/**
 * The `+` arsenal, in the composer that ships it.
 *
 * Through `ChatComposer` rather than the workbench: the control's job is to sit
 * at the start of the real row, and the harness styles a row of its own.
 */
const meta = {
  title: "Widgets/Chat/Composer/Tools",
  component: ChatComposer,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ChatComposer>;

export default meta;
type Story = StoryObj<typeof meta>;

const GLYPHS: Record<string, ReactNode> = {
  mic: <Mic className="size-4" aria-hidden />,
  image: <Image className="size-4" aria-hidden />,
  globe: <Globe className="size-4" aria-hidden />,
  file: <File className="size-4" aria-hidden />,
  terminal: <Terminal className="size-4" aria-hidden />,
};

const CATEGORIES: Record<string, string> = {
  stt: "Speech",
  image: "Images",
  web: "Web",
  documents: "Documents",
  generation: "Generation",
  code: "Code",
};

const toolIcon = (key: string): ReactNode => GLYPHS[key] ?? null;
const toolCategoryLabel = (category: string): string => CATEGORIES[category] ?? category;

/**
 * Recents persist, so without this each story inherits whatever the previous
 * one picked: the recents group appears where a story never asked for it, and
 * the run order decides what a story sees.
 */
function forgetRecents(): void {
  localStorage.removeItem("djc:chat:recent-tools");
}

/** The composer with an arsenal, and nothing else — picks stage on its draft. */
function ToolsDemo({
  entries,
  ...rest
}: {
  readonly entries: readonly ToolCatalogEntry[];
} & Partial<Parameters<typeof ChatComposer>[0]>) {
  // No `onPick`: staging is the package's own, so a host that supplies only a
  // catalogue still gets the whole behaviour.
  const capabilities: ChatCapabilities = { tools: { entries } };

  return (
    <ChatProvider adapter={mockAdapter({ script: [] })} capabilities={capabilities}>
      <ChatComposer {...rest} toolIcon={toolIcon} toolCategoryLabel={toolCategoryLabel} />
    </ChatProvider>
  );
}

/**
 * The whole arsenal on a host that has everything. Press `+`: ten tools in
 * six categories, grouped by the registry's own key, with the filter shown.
 *
 * Opened in `play`, so the a11y gate reads the SHEET rather than the collapsed
 * trigger — a closed menu passes axe while saying nothing about its rows.
 */
export const FullArsenal: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await waitFor(async () => {
      await expect(screen.getByRole("menu", { name: "Tools" })).toBeVisible();
      // Grouped by the registry's key, mapped through the host's label.
      await expect(screen.getByRole("group", { name: "Speech" })).toBeVisible();
    });
  },
};

/**
 * Picking STAGES a chip and does NOT send.
 *
 * The claim the unit gate can only assert by absence, shown here as behaviour:
 * a chip appears, the typed text is untouched, and the sheet closes so it does
 * not cover the chip it just produced.
 */
export const PickStagesAChip: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    const row = await screen.findByRole("menuitemcheckbox", { name: /Transcribe audio/ });
    await userEvent.click(row);

    await waitFor(async () => {
      // Scoped to the chip row: the same label is also on the menu row behind
      // it, so a page-wide query matches two nodes and proves neither.
      const staged = within(screen.getByRole("list", { name: "Picked tools" }));
      await expect(staged.getByText("Transcribe audio")).toBeVisible();
      // The marker is composed at SEND, so nothing reaches the field.
      await expect(screen.getByRole("textbox")).toHaveValue("");
      // CLOSED: picking is the common act, and the sheet covers the chip it
      // just produced. The way back is the chip's own control, below.
      await expect(screen.queryByRole("menu")).not.toBeInTheDocument();
      // The caret waits in the field: a pick names an ACT, and the object it
      // acts on is the sentence the user types next. A closing dialog that
      // returns focus nowhere loses that keystroke.
      await expect(screen.getByRole("textbox")).toHaveFocus();
      // And the field now asks for what the sentence cannot carry. This tool
      // reads a FILE, so the standing "Ask anything" is replaced rather than
      // added to — one box, one instruction.
      await expect(screen.getByRole("textbox")).toHaveAttribute(
        "placeholder",
        "Attach the file",
      );
    });
  },
};

/**
 * The chip takes it back — the sheet is not the only way to unstage.
 *
 * This is what makes closing on a pick safe: the tray below the field carries
 * every staged tool with its own control, so a mis-pick costs one click and no
 * reopen.
 *
 * MUTANT: make `toggleTool` ignore an id it already holds → the chip survives
 * and this dies.
 */
export const TheChipUnstages: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.click(
      await screen.findByRole("menuitemcheckbox", { name: /Transcribe audio/ }),
    );

    const staged = await screen.findByRole("list", { name: "Picked tools" });
    await userEvent.click(within(staged).getByRole("button"));

    await waitFor(async () => {
      // The row itself is gone, not merely emptied: nothing staged renders no
      // list at all, so a host laying out the controls gets no stray gap.
      await expect(screen.queryByRole("list", { name: "Picked tools" })).not.toBeInTheDocument();
    });
  },
};

/**
 * The same host with no speech engine. Transcription is not registered, so
 * the menu must not offer it — the case a hardcoded list would get wrong.
 */
export const NoSpeechEngine: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE_NO_STT} />,
};

/**
 * Type "voice". `transcribe_audio` matches on its registration keywords, which
 * is why they travel with the entry — a user types what they have.
 */
export const FilterByKeyword: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
};

/** Type "zzz". The sheet says so; a menu that goes blank reads as broken. */
export const NoMatches: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
};

/**
 * A short catalogue: no filter. Below eight rows the box has nothing to narrow
 * and its autofocus would swallow the first keystroke.
 */
export const ShortCatalogue: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE.slice(0, 3)} />,
};

/** The capability absent: no `+` at all, not a disabled one. */
export const NoCapability: Story = {
  render: () => (
    <ChatProvider adapter={mockAdapter({ script: [] })}>
      <ChatComposer />
    </ChatProvider>
  ),
};

/**
 * The layout the user forgot to switch.
 *
 * "ыуфкср" is what "search" types on a Russian keyboard. The catalogue is
 * English, so without this the sheet answers "no such tool" and the user
 * concludes the capability is missing rather than that they mistyped.
 */
export const WrongKeyboardLayout: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.type(await screen.findByRole("searchbox"), "ыуфкср");

    await waitFor(async () => {
      await expect(
        screen.getByRole("menuitemcheckbox", { name: /Search the web/ }),
      ).toBeVisible();
    });
  },
};

/**
 * Ranking, not filtering.
 *
 * "web" hits two rows — one in a NAME, one in an ID. The name wins: an
 * unranked filter left the answer below rows that merely mention the word.
 */
export const TheAnswerComesFirst: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.type(await screen.findByRole("searchbox"), "web");

    await waitFor(async () => {
      const rows = screen.getAllByRole("menuitemcheckbox");
      await expect(rows[0]).toHaveAccessibleName(/Search the web/);
    });
  },
};

/**
 * Arrow keys walk the rows the eye reads, across groups rather than within one.
 *
 * Down from the filter opens on the first row; Enter commits it. The whole
 * point is reaching a tool without leaving the keyboard.
 */
export const KeyboardPick: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    const filter = await screen.findByRole("searchbox");
    await userEvent.type(filter, "web");
    await userEvent.keyboard("{ArrowDown}{Enter}");

    await waitFor(async () => {
      const staged = within(screen.getByRole("list", { name: "Picked tools" }));
      await expect(staged.getByText("Search the web")).toBeVisible();
    });
  },
};

/**
 * What you reached for last, at the top.
 *
 * A picked tool is lifted OUT of its category rather than repeated: two rows
 * for one tool are two the keyboard must walk, and their trailing columns
 * disagree — the recent one offers forget, the catalogue one a check.
 */
export const RecentComesFirst: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);

    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.click(
      await screen.findByRole("menuitemcheckbox", { name: /Search the web/ }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));

    await waitFor(async () => {
      const rows = screen.getAllByRole("menuitemcheckbox");
      await expect(rows[0]).toHaveAccessibleName(/Search the web/);
      // Once, not twice: lifted from "Web" rather than copied above it.
      await expect(screen.getAllByRole("menuitemcheckbox", { name: /Search the web/ })).toHaveLength(
        1,
      );
    });
  },
};

/** The history is the user's to prune: one row, one control, no dialog. */
export const ForgetARecentTool: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);

    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.click(
      await screen.findByRole("menuitemcheckbox", { name: /Search the web/ }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.click(await screen.findByRole("menuitem", { name: "Remove from recent" }));

    await waitFor(async () => {
      await expect(
        screen.queryByRole("menuitem", { name: "Remove from recent" }),
      ).not.toBeInTheDocument();
      // Back in its own category — forgotten from the history, not from the
      // catalogue.
      await expect(screen.getByRole("group", { name: "Web" })).toBeVisible();
    });
  },
};

/**
 * The server has not answered yet.
 *
 * The trigger holds its place, disabled. Before this, "still loading" and "no
 * tools" rendered the same — the `+` vanished until the reply landed, so the
 * same room showed it or not depending on whether a 60s cache was warm, and
 * the whole control row shifted when it appeared.
 */
export const WaitingForTheServer: Story = {
  render: () => (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      capabilities={{ tools: { entries: [], loading: true } }}
    >
      <ChatComposer toolIcon={toolIcon} toolCategoryLabel={toolCategoryLabel} />
    </ChatProvider>
  ),
  play: async ({ canvasElement }) => {
    const screen = within(canvasElement);
    await expect(screen.getByRole("button", { name: "Tools" })).toBeDisabled();
  },
};

/**
 * Pasting a sent turn restores its chips.
 *
 * `buildOutbound` writes a pick as `[label](app://tool/id)`, so copying a
 * turn and pasting it back used to return raw markdown to the box: a URL the
 * user never typed, and a tool nothing staged. The marker is read instead, and
 * only for tools this host offers — an unknown id stays in the text rather
 * than losing the request.
 */
export const PastingRestoresTheChip: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);
    const field = screen.getByRole("textbox");

    await userEvent.click(field);
    await userEvent.paste("draw a cat [Search the web](app://tool/web_search)");

    await waitFor(async () => {
      const staged = within(screen.getByRole("list", { name: "Picked tools" }));
      await expect(staged.getByText("Search the web")).toBeVisible();
      // The marker is gone from the box — the chip carries it now.
      await expect(field).toHaveValue("draw a cat");
    });
  },
};

/** One chip per tool, whatever route staged it. */
export const PastingCannotDuplicateAChip: Story = {
  render: () => <ToolsDemo entries={MOCK_TOOL_CATALOGUE} />,
  play: async ({ canvasElement }) => {
    forgetRecents();
    const screen = within(canvasElement);

    await userEvent.click(screen.getByRole("button", { name: "Tools" }));
    await userEvent.click(await screen.findByRole("menuitemcheckbox", { name: /Search the web/ }));

    await userEvent.click(screen.getByRole("textbox"));
    await userEvent.paste("again [Search the web](app://tool/web_search)");

    await waitFor(async () => {
      const staged = within(screen.getByRole("list", { name: "Picked tools" }));
      await expect(staged.getAllByText("Search the web")).toHaveLength(1);
    });
  },
};
