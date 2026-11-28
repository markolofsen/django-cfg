import type { Meta, StoryObj } from "@storybook/react-vite";
import { useEffect, useState, type ComponentProps, type ReactNode } from "react";

import { StoryAuth, type StorySession } from "../stories/auth";
import { McpConnect } from "./McpConnect";
import type { McpKeyLoader } from "./access/useMcpKey";

/** A host with its own key system passes `loadKey`; the stories below that omit it use the django-cfg key. */
const loadKey: McpKeyLoader = async () => "example-host-mcp-key-not-a-credential";

/** One session state around the widget, at the width a settings card gives it. */
function Connect({ session, ...props }: ComponentProps<typeof McpConnect> & { session: StorySession }) {
  return (
    <StoryAuth session={session}>
      <div className="max-w-md">
        <McpConnect {...props} />
      </div>
    </StoryAuth>
  );
}

/**
 * "Connect your AI assistant": the key on top, then one list of every way to connect.
 *
 * Everyone can look; only a signed-in user can connect, and the local clients
 * (Claude Code, Codex, Cursor, VS Code) get that user's own key in the command.
 * Each story fixes one session state, because that state decides which actions
 * are live and which bar sits above the list.
 */
const meta = {
  title: "Widgets/Mcp/Connect",
  component: McpConnect,
  args: {
    server: { url: "https://mcp.example.com/mcp/", alias: "example", name: "Example" },
    loadKey,
    keysUrl: "https://my.example.com/api-keys",
  },
} satisfies Meta<typeof McpConnect>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Every option is visible but disabled: the dialog itself opens only for a signed-in user. */
export const SignedOut: Story = {
  render: (args) => <Connect session="signedOut" {...args} />,
};

/** Home: one tile per app and nothing else. No key, no list, no scrolling. */
export const SignedIn: Story = {
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** The account has no key yet: on a key-based client's screen, a link to create one. */
export const NoKey: Story = {
  args: { loadKey: async () => null, initialView: { kind: "brand", id: "claude" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** The host's `loadKey` threw: the bar offers Retry. */
export const KeyError: Story = {
  args: {
    loadKey: async () => {
      throw new Error("503");
    },
    initialView: { kind: "brand", id: "claude" },
  },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** The session is still resolving: no bar, so nothing moves when it lands. */
export const Checking: Story = {
  render: (args) => <Connect session="checking" {...args} />,
};

/** The product's own lede replaces the bundled one; every other string stays. */
export const OwnLede: Story = {
  args: { copy: { lede: "Search the catalogue from your assistant." } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** `bare`: the host (a Settings dialog) shows the title; the lede stays. */
export const InSettings: Story = {
  args: { bare: true },
  render: (args) => (
    <StoryAuth session="signedIn">
      <div className="mx-auto max-w-2xl rounded-lg border border-border p-6">
        <h2 className="mb-4 text-lg font-semibold">MCP</h2>
        <McpConnect {...args} />
      </div>
    </StoryAuth>
  ),
};

/** The home screen in Russian, from the `locale` prop (a host passes the provider's locale instead). */
export const HomeRussian: Story = {
  args: { locale: "ru" },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** An OAuth app: one primary action and three steps; never a key. */
export const ClientOAuth: Story = {
  args: { initialView: { kind: "brand", id: "notion" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** An app with two ways (Claude: web connector and Claude Code): a section each. */
export const ClientConnector: Story = {
  args: { initialView: { kind: "brand", id: "claude" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** A terminal client: the command carries the key, shown masked with its own Copy. */
export const ClientCommand: Story = {
  args: { initialView: { kind: "brand", id: "codex" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** An editor deeplink. */
export const ClientEditor: Story = {
  args: { initialView: { kind: "brand", id: "cursor" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** "Other app" with the Quick connect card: the agent request and `curl | sh` always work; the key row appears once the key is ready. */
export const QuickConnect: Story = {
  args: { initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** Quick connect signed out: the keyless Copy buttons are still live, there is no key row. */
export const QuickConnectSignedOut: Story = {
  args: { initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedOut" {...args} />,
};

/** The client screen in Russian. */
export const ClientRussian: Story = {
  args: { locale: "ru", initialView: { kind: "brand", id: "chatgpt" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** Any other app: a stepper card with each value where its step needs it, then the AI prompt and the whole JSON. */
export const Manual: Story = {
  args: { initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** The manual screen in Russian. */
export const ManualRussian: Story = {
  args: { locale: "ru", initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedIn" {...args} />,
};

/** The same stepper on a phone: values truncate, Copy stays in reach. */
export const ManualMobile: Story = {
  args: { initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedIn" {...args} />,
  globals: { viewport: { value: "mobile1", isRotated: false } },
};

/** Home on a phone: two columns of tiles. */
export const HomeMobile: Story = {
  render: (args) => <Connect session="signedIn" {...args} />,
  globals: { viewport: { value: "mobile1", isRotated: false } },
};

/** Signed out: every screen opens, every action is disabled. */
export const ManualSignedOut: Story = {
  args: { initialView: { kind: "manual" } },
  render: (args) => <Connect session="signedOut" {...args} />,
};

const API_KEY_PATH = "/cfg/accounts/api-key/";

/**
 * Answers the generated `cfg/accounts/api-key` requests (retrieve, reveal, regenerate) in memory, so the story needs no backend.
 * `fail` makes reveal answer 500. Restores `fetch` on unmount.
 */
function MockBackend({ children, fail = false }: { children: ReactNode; fail?: boolean }) {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const real = window.fetch;
    const createdAt = new Date(Date.now() - 90 * 86_400_000).toISOString();
    let reissuedAt: string | null = new Date(Date.now() - 12 * 86_400_000).toISOString();
    let key = "example-initial-mcp-key-not-a-credential";
    const json = (body: unknown, status = 200) =>
      new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
    window.fetch = async (input, init) => {
      const url = input instanceof Request ? input.url : String(input);
      if (!url.includes(API_KEY_PATH)) return real(input, init);
      const method = (input instanceof Request ? input.method : init?.method ?? "GET").toUpperCase();
      if (url.includes("/regenerate/")) {
        key = "example-regenerated-mcp-key-not-a-credential";
        reissuedAt = new Date().toISOString();
        return json({ key, created_at: createdAt, reissued_at: reissuedAt });
      }
      if (url.includes("/reveal/")) return fail ? json({ detail: "boom" }, 500) : json({ key, created_at: createdAt, reissued_at: reissuedAt });
      return method === "GET" ? json({ key: key.slice(0, 8) + "…", created_at: createdAt, reissued_at: reissuedAt }) : json({}, 405);
    };
    setReady(true);
    return () => {
      window.fetch = real;
    };
  }, [fail]);
  return ready ? <>{children}</> : null;
}

/** No `loadKey`: the key is the user's django-cfg API key, revealed through the generated hooks, with "Renew access" under the panel. */
export const DjangoCfgKey: Story = {
  args: { loadKey: undefined, keysUrl: undefined, initialView: { kind: "manual" } },
  render: (args) => (
    <MockBackend>
      <Connect session="signedIn" {...args} />
    </MockBackend>
  ),
};

/** Revealing the django-cfg key failed: the bar offers Retry. */
export const DjangoCfgKeyError: Story = {
  args: { loadKey: undefined, keysUrl: undefined, initialView: { kind: "manual" } },
  render: (args) => (
    <MockBackend fail>
      <Connect session="signedIn" {...args} />
    </MockBackend>
  ),
};
