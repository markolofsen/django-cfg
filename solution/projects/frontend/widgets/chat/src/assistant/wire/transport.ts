import type { Attachment } from '../../chat/core';
import { decodeFrame, IDLE_MS, type ChatContext, type Frame } from './frames';
import { parseSSE, StreamLostError } from './parse-sse';

/** Problem codes the API answers before a stream starts (CONTRACT.md "Auth and errors"). */
export type RejectCode = 'unauthorized' | 'busy' | 'invalid' | 'rate_limited' | 'unavailable' | 'not_found' | 'already_given' | 'too_large' | 'unsupported_type' | 'failed';

/** The request was refused before any frame: nothing ran, so a retry with the same `client_id` is safe. */
export class ChatHttpError extends Error {
  readonly status: number;
  readonly code: RejectCode;
  /** Seconds from `Retry-After`, for 429. */
  readonly retryAfter?: number;

  constructor(status: number, code: RejectCode, retryAfter?: number) {
    super(`chat ${status} ${code}`);
    this.status = status;
    this.code = code;
    this.retryAfter = retryAfter;
  }
}

/** The session is not there (never was, or it is someone else's: the API answers both with a 404). The host forgets the remembered id. */
export class ThreadNotFoundError extends Error {
  constructor() {
    super('chat thread not found');
  }
}

/** No answer at all (offline, DNS, reset before the response): nothing is known to have run. */
export class ChatNetworkError extends Error {
  constructor() {
    super('chat network error');
  }
}

export interface SendInput {
  /** The session this message goes to (set by the session layer; read by `streamUrl`). Absent for an anonymous host. */
  threadId?: string;
  text: string;
  clientId: string;
  context?: ChatContext;
  /** Files the user attached, already stored by the host's `upload`. Absent when none. */
  attachments?: readonly Attachment[];
  /** The model id chosen in the composer (an alias such as `fast`). Absent when the host offers no choice. */
  model?: string;
  signal: AbortSignal;
}

/** Opens one run and yields its frames. The adapter owns the meaning; tests and stories supply a scripted one. */
export interface ChatTransport {
  open(input: SendInput): AsyncGenerator<Frame>;
}

export interface TransportConfig {
  /** API origin, no trailing slash; prefixes a relative `streamUrl`. The stream is called directly, never through a Next rewrite. */
  baseUrl: string;
  /** Where one run is opened: a path or URL, or a function read per request (a thread id in the path). Absent: the legacy `/apix/chat/v1/stream` (anonymous hosts only; a signed-in host with sessions always sets this). */
  streamUrl?: string | ((input: SendInput) => string);
  /** The request body. Absent: `{text, client_id, context?, attachments?: [{id}], model?}`; files go by id only, the server knows the rest. */
  buildBody?: (input: SendInput) => unknown;
  /** The bearer token, read per request; the header only, never the query string. Signed-in hosts. */
  getToken?: () => string | null | undefined;
  /** Anonymous hosts: an opaque token the host stores, sent as `x-visitor-token`. No cookie is assumed, no history is fetched. */
  visitorToken?: () => string | null | undefined;
  /** Context headers every generated-client request already carries (`accept-language`, `x-timezone`, `x-client-time`, `x-client-id`): `auth.clientHeaders()`. On the server it has no id and sends none. */
  contextHeaders?: () => Record<string, string>;
  /** More headers per request (a CSRF token). Wins over the ones above. */
  headers?: () => Record<string, string>;
  idleMs?: number;
  /** Replaces `fetch` for the stream: add auth, a CSRF token, credentials. */
  streamFetch?: typeof fetch;
  /** @deprecated Use `streamFetch`. */
  fetch?: typeof fetch;
}

const CODES: readonly string[] = ['unauthorized', 'busy', 'invalid', 'rate_limited', 'unavailable', 'not_found', 'already_given', 'too_large', 'unsupported_type'];
/** A server may name a bad request its own way; these read as `invalid`. */
const INVALID: readonly string[] = ['validation_error'];

function rejectCode(status: number, body: unknown): RejectCode {
  const code = typeof body === 'object' && body !== null ? (body as { code?: unknown }).code : undefined;
  if (typeof code === 'string' && CODES.includes(code)) return code as RejectCode;
  if (typeof code === 'string' && INVALID.includes(code)) return 'invalid';
  if (status === 401) return 'unauthorized';
  if (status === 404) return 'not_found';
  if (status === 409) return 'busy';
  if (status === 400 || status === 422) return 'invalid';
  if (status === 413) return 'too_large';
  if (status === 415) return 'unsupported_type';
  if (status === 429) return 'rate_limited';
  if (status === 503) return 'unavailable';
  return 'failed';
}

const LEGACY_STREAM = '/apix/chat/v1/stream';

export function createTransport(config: TransportConfig): ChatTransport {
  const call = config.streamFetch ?? config.fetch ?? fetch;
  return {
    async *open(input) {
      const { text, clientId, context, signal } = input;
      const token = config.getToken?.();
      const visitor = config.visitorToken?.();
      const target = typeof config.streamUrl === 'function' ? config.streamUrl(input) : (config.streamUrl ?? LEGACY_STREAM);
      const url = /^https?:\/\//.test(target) ? target : `${config.baseUrl}${target}`;
      let response: Response;
      try {
        response = await call(url, {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            ...(token ? { authorization: `Bearer ${token}` } : {}),
            ...(visitor ? { 'x-visitor-token': visitor } : {}),
            ...config.contextHeaders?.(),
            ...config.headers?.(),
          },
          body: JSON.stringify(config.buildBody ? config.buildBody(input) : { text, client_id: clientId, ...(context ? { context } : {}), ...(input.attachments?.length ? { attachments: input.attachments.map((file) => ({ id: file.id })) } : {}), ...(input.model ? { model: input.model } : {}) }),
          signal,
        });
      } catch {
        if (signal.aborted) return;
        throw new ChatNetworkError();
      }
      if (!response.ok) {
        const body: unknown = await response.json().catch(() => null);
        const wait = Number(response.headers.get('retry-after'));
        throw new ChatHttpError(response.status, rejectCode(response.status, body), Number.isFinite(wait) && wait > 0 ? Math.ceil(wait) : undefined);
      }
      if (!response.body || !(response.headers.get('content-type') ?? '').includes('text/event-stream')) throw new ChatHttpError(response.status, 'failed');
      for await (const raw of parseSSE(response.body, { idleMs: config.idleMs ?? IDLE_MS, signal })) {
        const frame = decodeFrame(raw);
        if (frame) yield frame;
      }
    },
  };
}

export { StreamLostError };
