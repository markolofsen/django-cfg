import { describe, expect, it } from 'vitest';

import {
  claudeCodeCommand,
  claudeConnectorUrl,
  codexCommand,
  agentSetupPrompt,
  cursorInstallUrl,
  geminiCliCommand,
  gooseInstallUrl,
  installCommand,
  installCommandWithKey,
  installScriptUrl,
  shellQuote,
  skillPrompt,
  skillUrl,
  lmStudioInstallUrl,
  manualFields,
  maskKey,
  mcpInfoUrl,
  parseServerInfo,
  mcpServersConfig,
  normalizeMcpEndpoint,
  vscodeInstallUrl,
  type McpServer,
} from './install';

const server: McpServer = { url: 'https://mcp.example.com/mcp', alias: 'example', name: 'Example' };
const KEY = 'key_1234567890abcdef';

describe('install builders', () => {
  it('normalises to one trailing slash', () => {
    expect(normalizeMcpEndpoint(' https://a.b/mcp/// ')).toBe('https://a.b/mcp/');
  });

  it('prefills the Claude connector with the name and URL, never a key', () => {
    const url = new URL(claudeConnectorUrl(server));
    expect(url.searchParams.get('connectorName')).toBe('Example');
    expect(url.searchParams.get('connectorUrl')).toBe('https://mcp.example.com/mcp/');
  });

  it('makes the Claude Code command replace an earlier entry', () => {
    const command = claudeCodeCommand(server, KEY);
    expect(command.startsWith('claude mcp remove --scope user example')).toBe(true);
    expect(command).toContain(`--header "X-MCP-Access-Key: ${KEY}"`);
  });

  it('writes the Codex table with http_headers', () => {
    const command = codexCommand(server, KEY);
    expect(command).toContain('[mcp_servers.example]');
    expect(command).toContain(`http_headers = { "X-MCP-Access-Key" = "${KEY}" }`);
  });

  it('keeps editor deeplinks on local schemes, with no command or args', () => {
    const cursor = cursorInstallUrl(server, KEY);
    const vscode = vscodeInstallUrl(server, KEY);
    expect(cursor.startsWith('cursor://')).toBe(true);
    expect(vscode.startsWith('vscode:mcp/install?')).toBe(true);
    const config = JSON.parse(atob(decodeURIComponent(new URL(cursor).searchParams.get('config') ?? '')));
    expect(Object.keys(config).sort()).toEqual(['headers', 'url']);
    expect(JSON.parse(decodeURIComponent(vscode.split('?')[1] ?? ''))).not.toHaveProperty('command');
  });

  it('keys the mcpServers block by the alias', () => {
    expect(JSON.parse(mcpServersConfig(server, KEY)).mcpServers.example.headers['X-MCP-Access-Key']).toBe(KEY);
  });

  it('never shows a short key', () => {
    expect(maskKey('short')).toBe('••••');
    expect(maskKey(KEY)).toBe('key_12…cdef');
  });

  it('makes the Gemini CLI command user-scoped, replacing an earlier entry', () => {
    const command = geminiCliCommand(server, KEY);
    expect(command.startsWith('gemini mcp remove --scope user example')).toBe(true);
    expect(command).toContain('gemini mcp add --scope user --transport http');
    expect(command).toContain(`--header "X-MCP-Access-Key: ${KEY}"`);
    expect(command.endsWith('example https://mcp.example.com/mcp/')).toBe(true);
  });

  it('builds the LM Studio deeplink on a local scheme with url and headers only', () => {
    const link = lmStudioInstallUrl(server, KEY);
    expect(link.startsWith('lmstudio://add_mcp?name=example&config=')).toBe(true);
    const config = JSON.parse(atob(decodeURIComponent(new URL(link).searchParams.get('config') ?? '')));
    expect(Object.keys(config).sort()).toEqual(['headers', 'url']);
    expect(config.headers['X-MCP-Access-Key']).toBe(KEY);
  });

  it('builds the Goose deeplink by URL with no key', () => {
    const link = gooseInstallUrl(server);
    const params = new URL(link).searchParams;
    expect(link.startsWith('goose://extension?')).toBe(true);
    expect(params.get('url')).toBe('https://mcp.example.com/mcp/');
    expect(params.get('type')).toBe('streamable_http');
    expect(link).not.toContain(KEY);
  });

  it('lists the wizard fields in order, masking the secret on screen but copying it whole', () => {
    const fields = manualFields(server, KEY);
    expect(fields.map((f) => f.id)).toEqual(['url', 'name', 'header', 'secret']);
    expect(fields[0]?.value).toBe('https://mcp.example.com/mcp/');
    expect(fields[2]?.value).toBe('X-MCP-Access-Key');
    expect(fields[3]).toEqual({ id: 'secret', value: KEY, shown: 'key_12…cdef' });
    expect(manualFields(server, null).map((f) => f.id)).toEqual(['url', 'name', 'header']);
  });

  it('builds the agent prompt with the URL and the key, and none without a key', () => {
    const template = { body: 'Connect. Name: {name}. URL: {url}.', keyLine: 'Send {header}: {key}.' };
    expect(agentSetupPrompt(server, KEY, template)).toBe(
      `Connect. Name: Example. URL: https://mcp.example.com/mcp/. Send X-MCP-Access-Key: ${KEY}.`,
    );
    expect(agentSetupPrompt(server, null, template)).toBeNull();
  });

  describe('server info', () => {
    const body = {
      instructions: ' Use validate_document first. ',
      tools: [{ name: 'validate_document', description: 'Checks a doc' }, { name: '' }, 'x'],
      resources: [{ name: 'guide', description: '', uri: 'doc://guide' }, { name: 'bad', description: '' }],
      prompts: [{ name: 'review', description: 'Review a page' }],
    };
    const info = parseServerInfo(body)!;
    const withInfo: McpServer = { ...server, info };

    it('points at /info/ under the endpoint', () => {
      expect(mcpInfoUrl({ url: 'https://mcp.example.com/mcp' })).toBe('https://mcp.example.com/mcp/info/');
    });

    it('keeps well-formed rows, trims, and drops resources without a uri', () => {
      expect(info.instructions).toBe('Use validate_document first.');
      expect(info.tools).toEqual([{ name: 'validate_document', description: 'Checks a doc' }]);
      expect(info.resources).toEqual([{ name: 'guide', description: '', uri: 'doc://guide' }]);
      expect(info.prompts).toHaveLength(1);
    });

    it('returns null for an empty or non-object body (an older server)', () => {
      expect(parseServerInfo(null)).toBeNull();
      expect(parseServerInfo({ server: { name: 'x' } })).toBeNull();
    });

    it('adds instructions and resource URIs to the agent prompt only when info is present', () => {
      const template = { body: 'Connect {url}.', keyLine: 'Send {header}: {key}.' };
      const plain = agentSetupPrompt(server, KEY, template);
      expect(agentSetupPrompt({ ...server, info: undefined }, KEY, template)).toBe(plain);
      const full = agentSetupPrompt(withInfo, KEY, template)!;
      expect(full.startsWith(plain!)).toBe(true);
      expect(full).toContain('Server instructions: Use validate_document first.');
      expect(full).toContain('Resources it exposes: doc://guide.');
    });

    it('adds them beside mcpServers, not inside the entry, and leaves the plain output unchanged', () => {
      const plain = JSON.parse(mcpServersConfig(server, KEY));
      expect(Object.keys(plain)).toEqual(['mcpServers']);
      const full = JSON.parse(mcpServersConfig(withInfo, KEY));
      expect(full.instructions).toBe('Use validate_document first.');
      expect(full.resources).toEqual(['doc://guide']);
      expect(full.mcpServers.example).toEqual(plain.mcpServers.example);
    });
  });
});

describe('quick connect', () => {
  it('hangs both paths off the endpoint, with or without a trailing slash', () => {
    for (const url of ['https://mcp.example.com/mcp', 'https://mcp.example.com/mcp/', 'https://mcp.example.com/mcp//']) {
      expect(skillUrl({ url })).toBe('https://mcp.example.com/mcp/SKILL.md');
      expect(installScriptUrl({ url })).toBe('https://mcp.example.com/mcp/install.sh');
    }
  });

  it('builds the keyless command with a quoted URL', () => {
    expect(installCommand(server)).toBe("curl -fsSL 'https://mcp.example.com/mcp/install.sh' | sh");
  });

  it('puts the key in MCP_API_KEY for sh, quoted', () => {
    expect(installCommandWithKey(server, KEY)).toBe(
      "curl -fsSL 'https://mcp.example.com/mcp/install.sh' | MCP_API_KEY='key_1234567890abcdef' sh",
    );
  });

  it('escapes single quotes in the URL and the key', () => {
    expect(shellQuote("a'b")).toBe(String.raw`'a'\''b'`);
    expect(shellQuote("'; rm -rf ~; '")).toBe(String.raw`''\''; rm -rf ~; '\'''`);
    const cmd = installCommandWithKey({ url: "https://x.example/m'cp" }, "k'$(id)`id`");
    expect(cmd).toBe("curl -fsSL 'https://x.example/m'\\''cp/install.sh' | MCP_API_KEY='k'\\''$(id)`id`' sh");
  });

  it('refuses a key with a control character or no key', () => {
    expect(installCommandWithKey(server, 'a\nb')).toBeNull();
    expect(installCommandWithKey(server, 'a\rb')).toBeNull();
    expect(installCommandWithKey(server, '')).toBeNull();
  });

  it('keeps the key out of the keyless command and fills the prompt', () => {
    expect(installCommand(server)).not.toContain(KEY);
    expect(skillPrompt(server, 'Read {url} and connect {name}.')).toBe('Read https://mcp.example.com/mcp/SKILL.md and connect Example.');
  });
});
