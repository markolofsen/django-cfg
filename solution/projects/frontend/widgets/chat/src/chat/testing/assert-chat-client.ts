// Fails a host's own test when its generated chat client is older than the server contract.
//
// The host checks in the `openapi.json` its client was generated from and calls `assertChatClient(openapi)` once, in a test. The server side of the same contract
// is pinned by the framework's conformance class; this is the other end, so a client that missed `trace`, the cancel or stream route, or still carries `tool_calls`
// fails in the host's CI, not in a user's browser.

/** One thing the schema lacks or still has: a sentence the host can act on. */
export type ChatClientProblem = string;

/** Thrown by `assertChatClient`; `problems` is every finding, not only the first. */
export class ChatClientDriftError extends Error {
  readonly problems: readonly ChatClientProblem[];
  constructor(problems: readonly ChatClientProblem[]) {
    super(
      `The generated chat client is behind the server contract (${problems.length} problem${problems.length === 1 ? '' : 's'}):\n` +
        problems.map((p) => `  - ${p}`).join('\n') +
        '\nRegenerate the client from the server\'s current openapi.json (make update) and replace any code that reads a removed field.',
    );
    this.name = 'ChatClientDriftError';
    this.problems = problems;
  }
}

interface OpenApi {
  paths?: Record<string, Record<string, unknown>>;
  components?: { schemas?: Record<string, { properties?: Record<string, unknown> } | undefined> };
}

/** The routes the transport and the session call, as `METHOD` plus the path below the mount, with every `{param}` written `{}`. */
const ROUTES: ReadonlyArray<readonly [method: string, tail: string, what: string]> = [
  ['get', '/threads/', 'threads list'],
  ['post', '/threads/', 'threads create'],
  ['get', '/threads/{}/', 'threads retrieve'],
  ['post', '/threads/{}/messages/', 'send a message (messages create)'],
  ['get', '/threads/{}/messages/{}/stream/', 'resume a run (messages stream)'],
  ['post', '/threads/{}/messages/{}/cancel/', 'cancel a run (messages cancel)'],
  ['post', '/threads/{}/messages/{}/parts/{}/ack/', 'acknowledge a card (parts ack)'],
  ['post', '/attachments/', 'upload an attachment (attachments create)'],
];

const shape = (path: string) => path.replace(/\{[^}]*\}/g, '{}').replace(/\/$/, '');

/** `attachments: false` for a host whose kinds take no files: it has no upload route, and the check does not ask for one. */
export interface ChatClientOptions {
  attachments?: boolean;
}

/** Every way the document disagrees with the contract; empty when the client is current. */
export function chatClientProblems(openapi: unknown, options: ChatClientOptions = {}): ChatClientProblem[] {
  const doc = (openapi ?? {}) as OpenApi;
  const found: ChatClientProblem[] = [];
  if (!doc.paths || typeof doc.paths !== 'object') return ['the document has no `paths`: pass the parsed openapi.json of the chat API'];

  const have = Object.entries(doc.paths).flatMap(([path, item]) => Object.keys(item ?? {}).map((method) => `${method.toLowerCase()} ${shape(path)}`));
  for (const [method, tail, what] of ROUTES) {
    if (!(options.attachments ?? true) && tail === '/attachments/') continue;
    // A trailing slash is the mount's choice (Django's `APPEND_SLASH` or a router without one): both are the same route.
    if (!have.some((route) => route.startsWith(`${method} `) && route.endsWith(shape(tail)))) found.push(`no route ${method.toUpperCase()} …${tail}: ${what}`);
  }

  const schemas = doc.components?.schemas ?? {};
  const message = schemas.ChatMessage ?? Object.entries(schemas).find(([name, s]) => name.endsWith('Message') && s?.properties && 'parts' in s.properties)?.[1];
  if (!message?.properties) {
    found.push('no `ChatMessage` schema');
  } else {
    if (!('trace' in message.properties)) found.push('`ChatMessage` has no `trace` (the server stores the run on the message)');
    if ('tool_calls' in message.properties) found.push('`ChatMessage` still has `tool_calls` (replaced by `trace`; the client predates it)');
  }
  if (!Object.keys(schemas).some((name) => name.endsWith('TraceStepFrame'))) found.push('no `…TraceStepFrame` schema: the stream\'s `trace_step` frame is unknown to this client');
  return found;
}

/** Call once in a test with the parsed `openapi.json` the host's client was generated from. Throws `ChatClientDriftError` listing every problem. */
export function assertChatClient(openapi: unknown, options?: ChatClientOptions): void {
  const problems = chatClientProblems(openapi, options);
  if (problems.length > 0) throw new ChatClientDriftError(problems);
}
