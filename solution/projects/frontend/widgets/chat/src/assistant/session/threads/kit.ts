import { auth } from '@djangocfg/api';
import type { AttachmentKind, AttachmentsCapability } from '../../../chat/core';
import type { StoredAttachment, StoredConversation, StoredMessage, StoredStatus, StoredThread } from '../../wire/stored';
import { createTransport, ThreadNotFoundError, type ChatTransport, type SendInput, type TransportConfig } from '../../wire/transport';
import type { ThreadApi } from './sessions';

/**
 * The chat API kit's thread shapes (django-cfg `django_llm.agent.chat.api`), as the generated client names them (`ChatThread`, `ChatThreadListItem`,
 * `ChatThreadDetail`, `ChatMessage`). Structural and read-only: a generated type is assignable (its enums are string enums), and a field the contract
 * changes shows up at the host's call site as a type error. Only the fields the widget reads are listed.
 */
export interface ChatMessageShape {
  id: string;
  seq: number;
  role: string;
  text: string;
  status: string;
  /** `''` when there is none. */
  error_code: string | null;
  parts: ReadonlyArray<{ kind: string; data?: unknown }>;
  /** Absent from a server built before attachments. */
  attachments?: ReadonlyArray<StoredAttachment>;
  created_at: string;
}
export interface ChatThreadShape {
  id: string;
  title: string;
  updated_at: string;
}
export interface ChatThreadListItemShape extends ChatThreadShape {
  message_count: number;
  last_message_at: string | null;
}
export interface ChatThreadDetailShape extends ChatThreadShape {
  messages: readonly ChatMessageShape[];
}

/** What a host API adapter resolves to (`{data, error, response}`); `response.status` carries a 404. */
export interface ChatCallResult<T> {
  data?: T;
  error?: unknown;
  response?: { status: number };
}

/** The three plain calls of the kit's thread routes, as the host maps them from its generated Orval operations. The stream is not among them: no schema describes it. */
export interface ChatThreadCalls {
  list: (options: { signal?: AbortSignal }) => Promise<ChatCallResult<readonly ChatThreadListItemShape[]>>;
  create: (options: { body?: { kind?: string; context?: Record<string, unknown> } }) => Promise<ChatCallResult<ChatThreadShape>>;
  retrieve: (options: { path: { thread_id: string }; signal?: AbortSignal }) => Promise<ChatCallResult<ChatThreadDetailShape>>;
}

const STATUSES: readonly StoredStatus[] = ['done', 'running', 'error', 'cancelled'];

/** The kit's message as the widget's stored message. An unknown status reads as `error` (never a spinner without a stream). */
export function storedMessageOf(message: ChatMessageShape): StoredMessage {
  return {
    id: message.id,
    seq: message.seq,
    role: message.role === 'user' ? 'user' : 'assistant',
    text: message.text,
    parts: message.parts.map((part) => ({ kind: part.kind, data: part.data })),
    ...(message.attachments?.length ? { attachments: message.attachments.map((file) => ({ ...file })) } : {}),
    status: (STATUSES as readonly string[]).includes(message.status) ? (message.status as StoredStatus) : 'error',
    error_code: message.error_code ? message.error_code : null,
    created_at: message.created_at,
  };
}

/** A listed row, or a freshly created thread (`POST` answers without the counters). */
export function storedThreadOf(row: ChatThreadShape & Partial<Pick<ChatThreadListItemShape, 'message_count' | 'last_message_at'>>): StoredThread {
  return { id: row.id, title: row.title, last_message_at: row.last_message_at ?? row.updated_at, message_count: row.message_count ?? 0 };
}

export interface ChatTransportConfig
  extends Pick<TransportConfig, 'getToken' | 'contextHeaders' | 'headers' | 'idleMs' | 'streamFetch' | 'buildBody'> {
  /** The thread calls of the generated client. */
  client: ChatThreadCalls;
  /** API origin, no trailing slash (the stream is called directly, never through a rewrite). */
  baseUrl: string;
  /** Where the kit is mounted, e.g. `/apix/assistant` (no trailing slash). The stream goes to `<mount>/threads/<id>/messages/`. */
  mount: string;
  /** `false` when the kit was mounted with `trailing_slash=False`. Default `true`. */
  trailingSlash?: boolean;
  /** The chat kind "New chat" asks for; omit where the server named a default kind. */
  kind?: string;
  /**
   * Context sent on "New chat" as the create body's `context` (a document id, the page locale), read per call. Return `undefined` for none.
   * Without it a host wraps `client.create` to add it.
   */
  getCreateContext?: () => Record<string, unknown> | undefined;
  /** List only threads that hold at least one message (`message_count > 0`), so an empty "New chat" never fills the menu. Default `false`. */
  hideEmpty?: boolean;
}

export interface ChatConnection {
  /** Hand to `useSession({ transport })`. */
  transport: ChatTransport;
  /** Hand to `useSession({ api })`. */
  api: ThreadApi;
}

/**
 * Everything a host connects to the kit, from the generated client's three thread calls: the SSE transport (`POST <mount>/threads/<id>/messages`, the frames of
 * `wire-contract.md`) and the `ThreadApi` for list / new chat / load (a 404 is `ThreadNotFoundError`, an error body or an absent one is a plain `Error`).
 * The host adds renderers, words, auth (`getToken` / `streamFetch`) and the mount point; nothing else.
 */
export function createChatTransport(config: ChatTransportConfig): ChatConnection {
  const { client, baseUrl, mount, kind, trailingSlash = true, getCreateContext, hideEmpty = false } = config;
  const tail = trailingSlash ? '/' : '';
  const streamUrl = ({ threadId }: SendInput) => `${mount}/threads/${encodeURIComponent(threadId ?? '')}/messages${tail}`;
  const transport = createTransport({ baseUrl, streamUrl, getToken: config.getToken, contextHeaders: config.contextHeaders ?? (() => auth.clientHeaders()), buildBody: config.buildBody, headers: config.headers, idleMs: config.idleMs, streamFetch: config.streamFetch });
  const api: ThreadApi = {
    async list(signal) {
      const res = await client.list({ signal });
      if (res.error || !res.data) throw new Error('chat threads');
      const rows = hideEmpty ? res.data.filter((row) => row.message_count > 0) : res.data;
      return rows.map(storedThreadOf);
    },
    async create() {
      const context = getCreateContext?.();
      const body = { ...(kind ? { kind } : {}), ...(context ? { context } : {}) };
      const res = await client.create(Object.keys(body).length ? { body } : {});
      if (res.error || !res.data) throw new Error('chat create');
      return storedThreadOf(res.data);
    },
    async load(id, signal): Promise<StoredConversation> {
      const res = await client.retrieve({ path: { thread_id: id }, signal });
      if (res.response?.status === 404) throw new ThreadNotFoundError();
      if (res.error || !res.data) throw new Error('chat thread');
      return { id: res.data.id, messages: res.data.messages.map(storedMessageOf) };
    },
  };
  return { transport, api };
}

/** The kit's `ChatAttachmentLimits`, as the generated client names its fields. */
export interface ChatAttachmentLimitsShape {
  enabled: boolean;
  kinds: readonly string[];
  accept: readonly string[];
  max_files: number;
  max_bytes: number;
}

/** What `POST attachments/` answers (`ChatAttachment`); the file is stored and owned by the caller until a send binds it. */
export type ChatAttachmentShape = StoredAttachment;

/** The two attachment calls of the generated client, mapped by the host (`Chat.chatAttachmentsLimits`, `Chat.chatAttachmentsCreate`). */
export interface ChatAttachmentCalls {
  limits: (options: { signal?: AbortSignal }) => Promise<ChatCallResult<ChatAttachmentLimitsShape>>;
  /** Multipart: the generated body serializer builds the form from `{file, kind?}`. */
  upload: (options: { body: { file: File; kind?: string }; signal?: AbortSignal }) => Promise<ChatCallResult<ChatAttachmentShape>>;
}

/** A refusal of the upload, carrying the HTTP status and the problem `code` so the chip can say why. */
export class ChatUploadError extends Error {
  readonly status: number;
  readonly code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export interface ChatAttachmentsConfig {
  calls: ChatAttachmentCalls;
  /** The chat kind the file is for; omit where the server named a default kind. */
  kind?: string;
  /** The words of a refusal by problem code (`too_large`, `unsupported_type`, ...); `fallback` for any other. */
  messages?: Partial<Record<string, string>> & { fallback?: string };
}

const KNOWN_KINDS: readonly AttachmentKind[] = ['image', 'audio', 'video', 'text', 'document'];

/**
 * The composer's `attachments` capability, from the server's own limits (`GET attachments/limits/`) and the generated multipart upload.
 * Resolves `undefined` when the kind takes no files or the limits cannot be read: no attach button is better than one the server will refuse.
 * The limits are the server's; a host never restates them.
 */
export async function loadChatAttachments(config: ChatAttachmentsConfig, signal?: AbortSignal): Promise<AttachmentsCapability | undefined> {
  const { calls, kind, messages } = config;
  let limits: ChatAttachmentLimitsShape | undefined;
  try {
    const res = await calls.limits({ signal });
    limits = res.error ? undefined : res.data;
  } catch {
    return undefined;
  }
  if (!limits?.enabled) return undefined;
  const kinds = limits.kinds.filter((k): k is AttachmentKind => (KNOWN_KINDS as readonly string[]).includes(k));
  return {
    kinds,
    accept: limits.accept,
    maxFileSize: limits.max_bytes,
    maxFiles: limits.max_files,
    async upload(file, context) {
      const res = await calls.upload({ body: { file, ...(kind ? { kind } : {}) }, signal: context.signal });
      if (res.error || !res.data) {
        const status = res.response?.status ?? 0;
        const code = typeof res.error === 'object' && res.error !== null ? String((res.error as { code?: unknown }).code ?? '') : '';
        const word = messages?.[code] ?? (status === 413 ? messages?.too_large : status === 415 ? messages?.unsupported_type : undefined) ?? messages?.fallback ?? 'Upload failed';
        throw new ChatUploadError(status, code, word);
      }
      context.onProgress(1);
      return { id: res.data.id, url: res.data.url };
    },
  };
}
