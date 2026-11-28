import { Plug } from 'lucide-react';
import type { ComponentType, ReactNode } from 'react';

import { McpConnect, type McpConnectProps } from './connect/McpConnect';
import { McpApproval } from './consent/McpApproval';

export type McpSettingsOptions = Omit<McpConnectProps, 'className' | 'bare'>;

/** Structurally a `SettingsLayout` section (`@djangocfg/layouts`), so this widget needs no import of it. */
export interface McpSettingsSection {
  /** A literal, so `defineSettingsSections([mcpSettingsSection()])` in layouts keeps `'mcp'` in its id union. Layouts exports the same value as `MCP_SECTION_ID`. */
  id: 'mcp';
  label: string;
  title: string;
  icon: ComponentType<{ className?: string }>;
  group: string;
  keywords: string[];
  /** A function receives the address's one-shot intent for this section (`#settings/mcp?request=…`). */
  content: ReactNode | ((context: { intent: { params: Record<string, string>; clear: () => void } | null }) => ReactNode);
}

/**
 * The **MCP** section for the Settings dialog: `sections={[mcpSettingsSection()]}`.
 * It lands in the Platform group next to API keys; the widget's own lede is the subtitle, in the
 * host's language. It also answers an assistant's connect request (`#settings/mcp?request=…`, django-cfg's
 * default consent address) by approving it for the signed-in user, so a host needs no consent page of its own. `server` defaults to the API host + `/cfg/mcp/`; add it only for another server.
 */
export function mcpSettingsSection(options?: McpSettingsOptions): McpSettingsSection {
  return {
    id: 'mcp',
    label: 'MCP',
    title: 'MCP',
    icon: Plug,
    group: 'platform',
    keywords: ['mcp', 'assistant', 'claude', 'chatgpt', 'cursor', 'agent', 'connector'],
    content: ({ intent }) => (
      <div className="mx-auto flex max-w-2xl flex-col gap-4">
        {/* An assistant sent the user here (`?request=…`): it is approved at once and a status line says so. */}
        {intent?.params.request ? <McpApproval request={intent.params.request} server={options?.server} /> : null}
        <McpConnect {...options} bare />
      </div>
    ),
  };
}
