import { Bird, BookOpen, Cpu, Search, Sparkles } from 'lucide-react';

import type { ComponentType, SVGProps } from 'react';

import {
  CHATGPT_CONNECTORS_URL,
  claudeCodeCommand,
  claudeConnectorUrl,
  codexCommand,
  cursorInstallUrl,
  geminiCliCommand,
  gooseInstallUrl,
  lmStudioInstallUrl,
  maskKey,
  normalizeMcpEndpoint,
  PERPLEXITY_PLUGINS_URL,
  vscodeInstallUrl,
  type McpServer,
} from '../install';
import { ClaudeColorIcon, CodexIcon, CursorIcon, OpenAIIcon, VSCodeIcon } from '../marks';

import type { McpConnectCopy } from '../i18n';

/** The single list of what the widget offers: apps (brands), each with the ways to connect that app. */

export type Mark = ComponentType<SVGProps<SVGSVGElement>>;
type LabelKey = keyof McpConnectCopy;

export type Action =
  | { kind: 'link'; href: string; newTab: boolean }
  /** `shown` is what the row displays under its hint: the key masked, never the command; none for a block too long to show. */
  | { kind: 'copy'; text: string; shown?: string }
  | { kind: 'copyOpen'; text: string; href: string };

interface VariantBase {
  id: string;
  /** A product name, literal in every locale, or a label key for a category such as "Other client". */
  name: string | { label: LabelKey };
  hint: LabelKey;
  /** Known before the action can be built, so a disabled row keeps its final label. */
  actionKind: Action['kind'];
  /** Overrides the button label the action kind implies: Notion copies a URL, which is not the plain "Copy" of a command. */
  actionLabel?: LabelKey;
  /** How it connects, which picks its steps: a prefilled connector, a URL pasted into a form, a terminal command, or an install link. */
  flow: 'connector' | 'url' | 'command' | 'link';
  /** For a `url` flow: where the form lives, a label key filled into the second step. */
  where?: LabelKey;
  /** Set up on a computer: a terminal or an editor. On a phone the row says so. */
  desktopOnly?: true;
}

/** OAuth clients take the URL only; local clients take the user's key. */
export type Variant =
  | (VariantBase & { auth: 'oauth'; action: (server: McpServer) => Action })
  | (VariantBase & { auth: 'key'; action: (server: McpServer, key: string) => Action });

/** An app the visitor knows by name, with every documented way to connect it. One tile on the home screen. */
export interface Brand {
  id: string;
  name: string;
  Mark: Mark;
  variants: readonly Variant[];
}

const command = (text: string, key: string): Action => ({
  kind: 'copy',
  text,
  shown: maskKey(key),
});

export const BRANDS: readonly Brand[] = [
  {
    id: 'claude',
    name: 'Claude',
    Mark: ClaudeColorIcon,
    variants: [
      {
        id: 'claude-app',
        name: 'Claude',
        hint: 'claudeApp',
        flow: 'connector',
        actionKind: 'link',
        auth: 'oauth',
        action: (server) => ({ kind: 'link', href: claudeConnectorUrl(server), newTab: true }),
      },
      {
        id: 'claude-code',
        name: 'Claude Code',
        hint: 'terminal',
        flow: 'command',
        actionKind: 'copy',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => command(claudeCodeCommand(server, key), key),
      },
    ],
  },
  {
    id: 'chatgpt',
    name: 'ChatGPT',
    Mark: OpenAIIcon,
    variants: [
      {
        id: 'chatgpt',
        name: 'ChatGPT',
        hint: 'chatgptApp',
        flow: 'url',
        where: 'whereChatgpt',
        actionKind: 'copyOpen',
        auth: 'oauth',
        action: (server) => ({ kind: 'copyOpen', text: normalizeMcpEndpoint(server.url), href: CHATGPT_CONNECTORS_URL }),
      },
    ],
  },
  {
    id: 'codex',
    name: 'Codex',
    Mark: CodexIcon,
    variants: [
      {
        id: 'codex',
        name: 'Codex',
        hint: 'terminal',
        flow: 'command',
        actionKind: 'copy',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => command(codexCommand(server, key), key),
      },
    ],
  },
  {
    id: 'gemini',
    name: 'Gemini',
    Mark: Sparkles,
    variants: [
      {
        id: 'gemini-cli',
        name: 'Gemini CLI',
        hint: 'terminal',
        flow: 'command',
        actionKind: 'copy',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => command(geminiCliCommand(server, key), key),
      },
    ],
  },
  {
    id: 'notion',
    name: 'Notion',
    Mark: BookOpen,
    variants: [
      {
        /* Business and Enterprise; the form is per agent, so there is no link to open: the URL is copied. */
        id: 'notion',
        name: 'Notion',
        hint: 'notionApp',
        flow: 'url',
        where: 'whereNotion',
        actionKind: 'copy',
        actionLabel: 'copyAndOpen',
        auth: 'oauth',
        action: (server) => ({ kind: 'copy', text: normalizeMcpEndpoint(server.url) }),
      },
    ],
  },
  {
    id: 'perplexity',
    name: 'Perplexity',
    Mark: Search,
    variants: [
      {
        id: 'perplexity',
        name: 'Perplexity',
        hint: 'perplexityApp',
        flow: 'url',
        where: 'wherePerplexity',
        actionKind: 'copyOpen',
        auth: 'oauth',
        action: (server) => ({ kind: 'copyOpen', text: normalizeMcpEndpoint(server.url), href: PERPLEXITY_PLUGINS_URL }),
      },
    ],
  },
  {
    id: 'cursor',
    name: 'Cursor',
    Mark: CursorIcon,
    variants: [
      {
        id: 'cursor',
        name: 'Cursor',
        hint: 'editor',
        flow: 'link',
        actionKind: 'link',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => ({ kind: 'link', href: cursorInstallUrl(server, key), newTab: false }),
      },
    ],
  },
  {
    id: 'vscode',
    name: 'VS Code',
    Mark: VSCodeIcon,
    variants: [
      {
        id: 'vscode',
        name: 'VS Code',
        hint: 'editor',
        flow: 'link',
        actionKind: 'link',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => ({ kind: 'link', href: vscodeInstallUrl(server, key), newTab: false }),
      },
    ],
  },
  {
    id: 'lm-studio',
    name: 'LM Studio',
    Mark: Cpu,
    variants: [
      {
        id: 'lm-studio',
        name: 'LM Studio',
        hint: 'editor',
        flow: 'link',
        actionKind: 'link',
        desktopOnly: true,
        auth: 'key',
        action: (server, key) => ({ kind: 'link', href: lmStudioInstallUrl(server, key), newTab: false }),
      },
    ],
  },
  {
    id: 'goose',
    name: 'Goose',
    Mark: Bird,
    variants: [
      {
        /* No header parameter in the deeplink: it signs in with OAuth on first use, so no key. */
        id: 'goose',
        name: 'Goose',
        hint: 'gooseApp',
        flow: 'link',
        actionKind: 'link',
        desktopOnly: true,
        auth: 'oauth',
        action: (server) => ({ kind: 'link', href: gooseInstallUrl(server), newTab: false }),
      },
    ],
  },
];

/** Every variant, flat. */
export const VARIANTS: readonly Variant[] = BRANDS.flatMap((brand) => brand.variants);

export function variantById(id: string): Variant | undefined {
  return VARIANTS.find((v) => v.id === id);
}

export function brandById(id: string): Brand | undefined {
  return BRANDS.find((b) => b.id === id);
}

/** A variant's display name: literal, or from the labels. */
export function nameOf(item: { name: string | { label: LabelKey } }, labels: McpConnectCopy): string {
  return typeof item.name === 'string' ? item.name : labels[item.name.label];
}
