import type { Meta, StoryObj } from '@storybook/react-vite';
import { useMemo } from 'react';

import '../styles/index.css';

import { KB_RENDERERS } from './examples/kb-assistant';
import { AssistantChat } from './shell';
import { scriptedTransport, type ScriptStep } from './session';
import type { ThreadApi } from './session';
import { useSession, type SessionCopy } from './session';
import type { Frame } from './wire';
import type { StoredConversation, StoredMessage } from './wire';
import { ChatHttpError, ChatNetworkError } from './wire';

/**
 * The chat's failure and edge states, each driven through the production adapter and session with a scripted transport (the real code path). The full, everything-on assistant is `Widgets/Chat/Assistant/Complete`;
 * this file holds only what that one cannot show: a refusal, a lost stream, an offline reader, a restored thread.
 */

const ITEMS = [{ n: 1, title: 'Refund policy', heading_path: ['Refund policy', 'Eligibility'] }, { n: 2, title: 'Onboarding a new client' }];
const dataRenderers = KB_RENDERERS;
const SUGGESTIONS = ['What is our refund policy?', 'How do we onboard a new client?', 'Where is the holiday calendar?'];

const copy: SessionCopy = {
  messages: {
    rejected: (e) => ({ unauthorized: 'Sign in to ask the assistant.', busy: 'Finish in the other tab first.', invalid: 'That message is too long.', rate_limited: `Too many messages. Try again in ${e.retryAfter ?? 30} s.`, unavailable: 'The assistant is resting. Try again later.', failed: 'Something went wrong.', not_found: 'That conversation is gone.', already_given: 'Already sent.', too_large: 'That file is too large.', unsupported_type: 'That file type is not supported.' })[e.code],
    streamError: () => 'Something went wrong. Try again.',
    failed: 'Something went wrong. Try again.',
  },
  status: { thinking: 'Thinking…', searching: 'Searching…', answering: 'Writing the answer…' },
  failedText: 'Something went wrong. Try again.',
};

const run: ScriptStep = { frame: { type: 'run', version: 1, thread_id: 't1', message_id: 'a1', client_id: 'c1', seq: 2 } satisfies Frame };
const words = (text: string): ScriptStep[] => text.split(/(?<=\s)/).map((delta) => ({ frame: { type: 'text_delta', delta }, after: 45 }));
const status = (phase: 'thinking' | 'searching' | 'answering', after = 500): ScriptStep => ({ frame: { type: 'status', phase }, after });
const done: ScriptStep = { frame: { type: 'done', finish_reason: 'stop', tokens_in: null, tokens_out: null, cost_usd: null, replayed: false } };
const TEXT = 'A client can ask for a refund within 14 days of paying [1]. Onboarding follows the checklist [2]. ';

const stored = (over: Partial<StoredMessage>): StoredMessage => ({ id: 'm1', seq: 1, role: 'user', text: '', parts: [], status: 'done', error_code: null, created_at: '2026-10-24T10:00:00Z', ...over });
const HISTORY: StoredConversation = {
  id: 'c1',
  messages: [
    stored({ id: 'm1', seq: 1, text: 'What is our refund policy?' }),
    stored({ id: 'm2', seq: 2, role: 'assistant', text: TEXT, parts: [{ kind: 'citations', data: { items: ITEMS } }] }),
  ],
};

interface HarnessProps {
  script: ScriptStep[];
  thread?: StoredConversation;
  /** What the server says when the client reconciles after a lost stream. */
  reconciled?: StoredConversation;
  loadDelay?: number;
}

function Harness({ script, thread = { id: null, messages: [] }, reconciled, loadDelay = 300 }: HarnessProps) {
  const transport = useMemo(() => scriptedTransport(script), [script]);
  const api = useMemo<ThreadApi>(() => {
    let calls = 0;
    return {
      list: async () => (thread.id ? [{ id: thread.id, title: 'Earlier', last_message_at: '2026-10-24T10:00:00Z', message_count: thread.messages.length }] : []),
      create: async () => ({ id: 'new-session', title: '', last_message_at: '2026-10-24T10:00:00Z', message_count: 0 }),
      load: () => new Promise((resolve) => setTimeout(() => resolve(calls++ > 0 && reconciled ? reconciled : thread), loadDelay)),
    };
  }, [thread, reconciled, loadDelay]);
  const session = useSession({ transport, api, getContext: () => undefined, copy });
  if (session.thread.kind !== 'ready') return <p className="p-4 text-sm text-muted-foreground">{session.thread.kind === 'error' ? 'Could not load the conversation.' : 'Loading…'}</p>;
  return (
    <div className="mx-auto flex h-[640px] max-w-md flex-col rounded-xl border">
      <AssistantChat adapter={session.adapter} dataRenderers={dataRenderers} suggestions={SUGGESTIONS} conversation={{ id: session.thread.id, history: session.thread.history }} draftRoom={session.thread.session ?? 'new'} notice={session.notice} onRetry={session.reload} className="h-full min-h-0" />
    </div>
  );
}

const meta = {
  title: 'Widgets/Chat/Assistant/States',
  component: Harness,
  parameters: { layout: 'padded' },
} satisfies Meta<typeof Harness>;
export default meta;
type Story = StoryObj<typeof meta>;

/** A stored thread restored on load (no empty-state flash). */
export const RestoredThread: Story = { args: { script: [run, ...words('Sure. '), done], thread: HISTORY } };
/** Text arrives in small steps and stops partway: the stream fails after some text, which is kept. */
export const ErrorAfterPartial: Story = { args: { script: [run, status('searching'), ...words('Let me look at the refund'), { frame: { type: 'error', code: 'failed', message: 'x', retryable: true } }] } };
export const RateLimited: Story = { args: { script: [{ throw: new ChatHttpError(429, 'rate_limited', 12) }] } };
export const BusyInAnotherTab: Story = { args: { script: [{ throw: new ChatHttpError(409, 'busy') }] } };
export const SignedOut: Story = { args: { script: [{ throw: new ChatHttpError(401, 'unauthorized') }] } };
export const Unavailable: Story = { args: { script: [{ throw: new ChatHttpError(503, 'unavailable') }] } };
export const Offline: Story = { args: { script: [{ throw: new ChatNetworkError() }] } };
/** The stream is cut mid-answer; the client asks the server and the stored answer replaces the partial one. */
export const InterruptedThenReconciled: Story = {
  args: {
    script: [run, ...words('A client can ask for a ref'), { throw: new Error('lost'), after: 200 }].map((s) => ('throw' in s ? { throw: new (class extends Error {})('lost') } : s)),
    reconciled: { id: 'c1', messages: [stored({ id: 'u1', seq: 1, text: 'What is our refund policy?' }), stored({ id: 'a1', seq: 2, role: 'assistant', text: TEXT, parts: [{ kind: 'citations', data: { items: ITEMS } }] })] },
  },
};
