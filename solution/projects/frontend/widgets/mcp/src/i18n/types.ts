/**
 * The package's copy schema. English is the schema of record: every locale is
 * typed against `McpCopy`, so a missing key fails `tsc`, not the render.
 */

/** Every string the connect widget renders, besides product names. */
export interface McpConnectCopy {
  title: string;
  lede: string;
  /** The row for any client not named: a category, so it is translated. */
  otherFamily: string;
  /** @deprecated No longer rendered (the home screen is tiles); kept so a host's `copy` override still type-checks. */
  groupApps: string;
  /** The hint on the "other client" row: where the config goes. */
  configHint: string;
  /** @deprecated No longer rendered; kept for a host's `copy` override. */
  groupManual: string;
  /** Under the legend: which apps need the form. */
  manualLede: string;
  manualStep1: string;
  manualStep2: string;
  manualStep3: string;
  /** The form's field names, as the apps print them. */
  fieldUrl: string;
  fieldName: string;
  fieldAuth: string;
  /** The value shown on the Authentication row. */
  authOauth: string;
  /** API key option: the "Key" field, which holds the header name. */
  fieldHeader: string;
  /** API key option: the "Value" field, or the Bearer token. */
  fieldSecret: string;
  /** Basic authentication is not accepted by the server. */
  noBasic: string;
  /** Hints of the Notion, Perplexity and Goose rows. */
  notionApp: string;
  perplexityApp: string;
  gooseApp: string;
  /** @deprecated No longer rendered (every app is its own home tile); kept for a host's `copy` override. */
  groupCode: string;
  /** The home tile for any app not named: the manual form. */
  otherApp: string;
  /** The back button; also its accessible name. */
  back: string;
  /** The first crumb. */
  crumbRoot: string;
  /** The accessible name of the breadcrumb. */
  breadcrumbLabel: string;
  /** Where each form lives, filled into `stepUrl2` as `{where}`. */
  whereChatgpt: string;
  whereNotion: string;
  wherePerplexity: string;
  /** The (at most three) steps of a client, by how it connects. */
  stepConnector1: string;
  stepConnector2: string;
  stepUrl1: string;
  /** `{where}` is filled in. */
  stepUrl2: string;
  stepUrl3: string;
  stepCmd1: string;
  stepCmd2: string;
  stepLink1: string;
  stepLink2: string;
  /** The button that copies the setup instructions for an AI agent. */
  copyPrompt: string;
  promptHint: string;
  /** The text an agent receives: `{name}` and `{url}` are filled in. Written to an AI, so it may use "you". */
  promptBody: string;
  /** `{header}` and `{key}` are filled in. */
  promptKeyLine: string;
  claudeApp: string;
  chatgptApp: string;
  terminal: string;
  editor: string;
  /** A terminal or editor row, seen on a phone. */
  onComputer: string;
  open: string;
  copy: string;
  copyAndOpen: string;
  /** The footer line with the masked key. */
  yourKey: string;
  keyMissing: string;
  createKey: string;
  keyError: string;
  retry: string;
  /** Under a key just created: it is not shown again. */
  keyOnce: string;
  /** Title of the list of the server's tools. */
  canTitle: string;
  /** `{count}` is filled in. */
  canMore: string;
  canLess: string;
  /** The "Quick connect" card of the Other-app screen: for AI agents and terminals. */
  quickTitle: string;
  quickLede: string;
  quickAgentTitle: string;
  quickAgentHint: string;
  /** The request an agent receives, no key: `{url}` (the server's SKILL.md) and `{name}` are filled in. Written to an AI. */
  quickAgentPrompt: string;
  quickCommandTitle: string;
  quickCommandHint: string;
  /** The row that runs the installer with the user's key (shown masked, copied whole). */
  quickKeyTitle: string;
  quickKeyHint: string;
  /** The link that opens SKILL.md in a new tab. */
  view: string;
}

/** The approval status line of the Settings dialog. `{client}` is filled in. */
export interface McpConsentCopy {
  expired: string;
  unreachable: string;
  /** The server answered but refused or failed (401, 403, 5xx): not a network problem. */
  failed: string;
  /** `{client}`: shown while the request is approved without a question. */
  connecting: string;
  /** `{client}`: shown for the moment before the browser returns to the assistant. */
  connected: string;
  /** When the client sent no name. */
  unknownClient: string;
}

/** The renew section under the panel. `{when}` is filled in. */
export interface McpRenewCopy {
  renew: string;
  /** Under the button: what renewing does. */
  renewHint: string;
  renewConfirm: string;
  /** Confirms the renew step. */
  confirm: string;
  /** Declines the renew step. */
  keep: string;
  lastRenewed: string;
  /** Announced when the new key is in use. */
  renewedAnnounce: string;
  /** Renewing failed and the server gave no detail. */
  error: string;
}

export interface McpCopy {
  connect: McpConnectCopy;
  consent: McpConsentCopy;
  renew: McpRenewCopy;
}
