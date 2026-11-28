'use client';

import { MoreHorizontal, Archive, Link2, PenLine, Pin, Trash2 } from 'lucide-react';
import { useMemo, useState } from 'react';

import { Button, MenuBuilder } from '@djangocfg/ui-core/components';
import { PanelIconButton } from '../../../chat/ui';
import { AssistantChat } from '../../shell';
import { AssistantHostProvider, AssistantPortal, AssistantSlot } from '../../shell';
import { AssistantHistory } from '../../history/assistant-history';
import { DEFAULT_MODEL, useModelAliases } from '../../shell';
import { SessionsMenu } from '../../history/sessions-menu';
import { ChatDock } from '../../shell';
import { useSession, type SessionCopy } from '../../session';
import { KB_RENDERERS } from '../kb-assistant';
import { createDemoServer } from './server';
import { DEMO_RENDERERS } from './widgets';

const COPY: SessionCopy = {
  messages: { rejected: () => 'The demo cannot send this.', streamError: () => 'Something went wrong.', failed: 'Something went wrong.' },
  status: { thinking: 'Thinking…', searching: 'Searching…', answering: 'Writing the answer…' },
  failedText: 'Something went wrong.',
};

export const DEMO_SUGGESTIONS = ['Give me a quick overview', 'Show the tasks as a table', 'Ask me a question', 'Approve a schema change'];
const RENDERERS = { ...DEMO_RENDERERS, ...KB_RENDERERS };
const noop = () => undefined;

/** A fake host `upload`: reports progress over ~1 s and keeps the file as a local object URL (a file named `fail*` is refused). */
const fakeUpload = async (file: File, { signal, onProgress }: { signal: AbortSignal; onProgress: (fraction: number) => void }) => {
  for (let step = 1; step <= 5; step += 1) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    if (signal.aborted) throw new DOMException('aborted', 'AbortError');
    onProgress(step / 5);
  }
  if (file.name.startsWith('fail')) throw new Error('The server refused this file');
  return { url: URL.createObjectURL(file) };
};

/** The host's own "..." menu, built from UI Core and dropped into the header's free slot. */
function HeaderMenu() {
  return (
    <MenuBuilder
      align="end"
      items={[
        { kind: 'item', id: 'link', label: 'Copy link', icon: Link2, onSelect: noop },
        { kind: 'item', id: 'pin', label: 'Pin', icon: Pin, onSelect: noop },
        { kind: 'item', id: 'rename', label: 'Rename', icon: PenLine, onSelect: noop },
        { kind: 'item', id: 'archive', label: 'Archive', icon: Archive, onSelect: noop },
        { kind: 'separator' },
        { kind: 'item', id: 'delete', label: 'Delete', icon: Trash2, onSelect: noop, variant: 'destructive' },
      ]}
    >
      <PanelIconButton label="More"><MoreHorizontal className="size-4" aria-hidden="true" /></PanelIconButton>
    </MenuBuilder>
  );
}

export type DemoPlacement = 'inline' | 'dock' | 'sheet';

interface Props {
  /** Start with no open chat: greeting and suggestions. */
  empty?: boolean;
  /** `inline` a bordered column, `dock` the floating window of a tablet, `sheet` the full-screen phone sheet. */
  placement?: DemoPlacement;
  className?: string;
}

/**
 * The demo's session, its chat and its header controls, for a host that places them itself. `simple` is the plain assistant a page layout wants: an empty chat with a greeting and suggestions, no attachments, no model switch, only a New chat button, no history (the full one is `DemoAssistant`; (a page shell mounts `chat` through `AssistantPortal`, `header` in the frame's `actions`, and `<AssistantHistory session={session} />` beside it)).
 * `null` while the first conversation loads. `DemoAssistant` is this plus a placement; Storybook's page shell uses it directly, so there is one fixture, not two.
 */
export function useDemoAssistant({ simple = false, empty = simple, focusWhen }: { simple?: boolean; empty?: boolean; focusWhen?: boolean } = {}) {
  const server = useMemo(() => createDemoServer({ empty }), [empty]);
  const session = useSession({ transport: server.transport, api: server.api, storage: server.storage, getContext: () => undefined, copy: COPY });
  const [model, setModel] = useState(DEFAULT_MODEL);
  const aliases = useModelAliases();
  if (session.thread.kind !== 'ready') return null;
  const chat = (
    <AssistantChat
      adapter={session.adapter}
      dataRenderers={RENDERERS}
      suggestions={DEMO_SUGGESTIONS}
      conversation={{ id: session.thread.id, history: session.thread.history }}
      draftRoom={session.thread.session ?? 'new'}
      attachments={simple ? undefined : { upload: fakeUpload, maxFileSize: 5 * 1024 * 1024 }}
      models={simple ? undefined : { options: aliases, value: model, onChange: setModel }}
      focusWhen={focusWhen}
      refocus={focusWhen !== undefined}
      className="h-full min-h-0"
    />
  );
  const header = simple ? <SessionsMenu session={session} newOnly /> : <SessionsMenu session={session}><HeaderMenu /></SessionsMenu>;
  return { session, chat, header };
}

/**
 * The complete assistant with no server: the one fixture every story and screenshot uses. Everything the package offers is on: the long stored thread, history as a screen over twelve older chats,
 * attachments (a picture opens in the lightbox), the model chip, dictation, blocks (type "question", "approve", "table"), the header's custom slot, and any of the three placements.
 * Replies go through the real adapter and session; the "server" is in memory (`createDemoServer`).
 */
export function DemoAssistant({ empty = false, placement = 'inline', className }: Props) {
  const demo = useDemoAssistant({ empty });
  const [open, setOpen] = useState(true);
  if (demo === null) return null;
  const { session, chat, header } = demo;
  return (
    <AssistantHostProvider>
      {placement === 'inline' ? (
        <div className={`flex flex-col rounded-xl border ${className ?? 'h-[640px]'}`}>
          <div className="flex items-center justify-between border-b px-3 py-1">
            <span className="text-sm font-medium">Ask the assistant</span>
            {header}
          </div>
          <AssistantSlot className="min-h-0 flex-1" />
        </div>
      ) : (
        <div className="space-y-4 p-4">
          <p className="max-w-prose text-sm text-muted-foreground">The page stays usable while the assistant is open. {placement === 'sheet' ? 'On a phone this is a full-screen sheet.' : 'A tablet gets a floating window.'}</p>
          <Button onClick={() => setOpen(true)}>Ask</Button>
          <ChatDock open={open} onOpenChange={setOpen} title="Ask the assistant" actions={header} tablet={placement === 'sheet' ? 'sheet' : 'window'}>
            <AssistantSlot className="h-full min-h-0" />
          </ChatDock>
        </div>
      )}
      <AssistantHistory session={session} />
      <AssistantPortal>{chat}</AssistantPortal>
    </AssistantHostProvider>
  );
}
