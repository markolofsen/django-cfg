import type { StoredConversation, StoredMessage, StoredPart } from '../../wire';
import type { ScriptStep } from '../../session';

/**
 * The demo transcript: one long read that shows every kind of message an answer can hold, in the order a real working session produces them.
 * Abstract on purpose: no real people, no real data.
 */

let n = 0;
const at = (minutes: number) => new Date(Date.UTC(2026, 10, 6, 9, 0) + minutes * 60_000).toISOString();
const message = (role: 'user' | 'assistant', text: string, parts: StoredPart[] = []): StoredMessage => {
  n += 1;
  return { id: `demo-${n}`, seq: n, role, text, parts, status: 'done', error_code: null, created_at: at(n * 2) };
};
const user = (text: string) => message('user', text);
const bot = message.bind(null, 'assistant');

export const DEMO_THREAD: StoredConversation = {
  id: 'demo',
  messages: [
    user('Give me a quick overview of the project and what changed this week.'),
    bot(
      '## Weekly overview\n\nThe project is **on track**. Three things moved this week:\n\n1. The onboarding flow was shortened from five steps to three.\n2. Search now answers in under 200 ms.\n3. Two blocked tasks were unblocked.\n\n> Nothing here needs a decision from you yet.',
      [{ kind: 'metrics', data: { items: [{ label: 'Tasks done', value: '24', delta: '+6 this week' }, { label: 'Open issues', value: '9', delta: '−3' }, { label: 'Response time', value: '184 ms', delta: '−41 ms' }], progress: { label: 'Milestone 3', value: 72 } } }],
    ),
    user('Show me the tasks as a table.'),
    bot('Here are the open items, sorted by priority.', [
      { kind: 'table', data: { columns: ['Task', 'Owner', 'Status', 'Due'], rows: [
        { cells: ['Shorten the onboarding', 'Team A', 'Done', 'Nov 3'], tag: { column: 2, tone: 'green' } },
        { cells: ['Search latency budget', 'Team B', 'In review', 'Nov 8'], tag: { column: 2, tone: 'blue' } },
        { cells: ['Migrate the old exports', 'Team C', 'Blocked', 'Nov 12'], tag: { column: 2, tone: 'red' } },
        { cells: ['Write the release notes', 'Team A', 'Not started', 'Nov 14'], tag: { column: 2, tone: 'gray' } },
      ] } },
    ]),
    user('Why is the export migration blocked?'),
    bot(
      'It waits on a schema decision. The old exports store dates as text, the new ones as timestamps. A short script handles both:\n\n```ts\nconst toTimestamp = (value: string | number) =>\n  typeof value === \'number\' ? value : Date.parse(value);\n```\n\nIf you agree with timestamps, I can prepare the change for review.',
      [{ kind: 'ask', data: { question: 'What should I do?', options: ['Prepare the change', 'Show me the old schema', 'Not now'], other: true } }],
    ),
    user('Prepare the change.'),
    bot('Done. Review the proposal below; nothing is applied until you press Apply.', [
      { kind: 'steps', data: { title: 'What I did', steps: [{ label: 'Read the old export schema', state: 'done' }, { label: 'Wrote the conversion', state: 'done' }, { label: 'Checked 1 200 sample rows', state: 'done' }, { label: 'Wait for your approval', state: 'running' }] } },
      { kind: 'changes', data: { title: 'Updated the export schema', undoable: true, items: [{ label: 'export.created_at' }, { label: 'export.updated_at' }, { label: 'export.finished_at' }] } },
      { kind: 'approval', data: { summary: 'Store export dates as timestamps', changes: [{ path: 'export.created_at', from: 'text', to: 'timestamp' }, { path: 'export.updated_at', from: 'text', to: 'timestamp' }, { path: 'export.version', to: '2' }] } },
    ]),
    user('Is there anything to watch while I wait?'),
    bot('Two recordings explain the new flow, and the summary is attached as a file.', [
      { kind: 'media', data: { items: [{ id: 'v1', title: 'The three-step onboarding', meta: 'Walkthrough · 2026', duration: '4:12', hue: 210 }, { id: 'v2', title: 'How search ranks results', meta: 'Explainer · 2026', duration: '7:40', hue: 150 }] } },
      { kind: 'files', data: { files: [{ name: 'weekly-summary.pdf', size: '184 KB' }, { name: 'export-schema.json', size: '12 KB' }] } },
    ]),
  ],
};

const words = (text: string): ScriptStep[] => text.split(/(?<=\s)/).map((delta) => ({ frame: { type: 'text_delta', delta }, after: 35 }));
const payload = (kind: string, data: unknown): ScriptStep => ({ frame: { type: 'ui_payload', kind, data }, after: 250 });

/** The default reply: status, reasoning, text, then two widgets. */
export const demoScript = (): ScriptStep[] => [
  { frame: { type: 'run', version: 1, thread_id: 'demo', message_id: `live-${Date.now()}`, client_id: null, seq: null } },
  { frame: { type: 'status', phase: 'thinking' }, after: 300 },
  { frame: { type: 'reasoning_delta', delta: 'Checking the open tasks and the latest changes. ' }, after: 200 },
  { frame: { type: 'reasoning_delta', delta: 'The export migration is the only blocker.' }, after: 200 },
  { frame: { type: 'reasoning_end', elapsed_ms: 1400, tokens: 38 }, after: 200 },
  { frame: { type: 'status', phase: 'answering' }, after: 200 },
  ...words('Here is where things stand right now. The export migration is still the only blocker, and everything else is moving.\n\n- Review is open for the search budget\n- Release notes are not started\n\n'),
  payload('steps', { title: 'Progress', steps: [{ label: 'Onboarding', state: 'done' }, { label: 'Search budget', state: 'running' }, { label: 'Release notes', state: 'todo' }] }),
  payload('ask', { options: ['Show the blocker', 'Summarize again'], other: false }),
  { frame: { type: 'done', finish_reason: 'stop', tokens_in: null, tokens_out: null, cost_usd: null, replayed: false } },
];

const run = (): ScriptStep => ({ frame: { type: 'run', version: 1, thread_id: 'demo', message_id: `live-${Date.now()}`, client_id: null, seq: null } });
const end: ScriptStep = { frame: { type: 'done', finish_reason: 'stop', tokens_in: null, tokens_out: null, cost_usd: null, replayed: false } };
const think: ScriptStep = { frame: { type: 'status', phase: 'thinking' }, after: 300 };

/**
 * What the demo answers, by what was typed: a keyword picks the kind of block the answer carries, so each can be tried from one chat.
 * `question` / `ask` an `ask` block, `picture` / `chart` an inline picture (click it), `approve` / `schema` an approval card then a finished-change card, `table` / `task` a table, `error` a failed run; anything else the default reply.
 */
/** A picture an agent could send, drawn inline so the demo needs no network. */
const CHART = `data:image/svg+xml;utf8,${encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' width='640' height='320'><rect width='640' height='320' fill='#0f172a'/><g fill='#6366f1'><rect x='60' y='180' width='60' height='100'/><rect x='160' y='140' width='60' height='140'/><rect x='260' y='100' width='60' height='180'/><rect x='360' y='60' width='60' height='220'/><rect x='460' y='90' width='60' height='190'/></g><text x='60' y='40' fill='#e2e8f0' font-family='sans-serif' font-size='20'>Tasks done per day</text></svg>")}`;

export function demoReply(text: string, attached = 0): ScriptStep[] {
  const t = text.toLowerCase();
  if (attached > 0) return [run(), think, ...words(`I can see ${attached === 1 ? 'the file' : `${attached} files`} you attached. Open a picture to look at it large.`), end];
  if (/question|\bask\b|which/.test(t)) return [run(), think, ...words('Before I change anything I need one answer.'), payload('ask', { question: 'Which contact should I keep?', options: [{ label: 'Katerina Gordeeva', description: 'Added 2 March' }, { label: 'Helen' }, { label: 'Nika' }], other: 'Someone else…' }), end];
  if (/picture|image|photo|chart/.test(t)) return [run(), think, ...words(`Here is the chart as a picture. Click it to open it large.\n\n![Weekly tasks](${CHART})`), end];
  if (/approve|schema|change/.test(t)) return [run(), think, ...words('I prepared the change. Nothing is applied until you press Apply.'), payload('approval', { summary: 'Store export dates as timestamps', changes: [{ path: 'export.created_at', from: 'text', to: 'timestamp' }, { path: 'export.updated_at', from: 'text', to: 'timestamp' }] }), payload('changes', { title: 'Updated the export schema', undoable: true, items: ['export.created_at', 'export.updated_at', 'export.finished_at'] }), end];
  if (/table|task/.test(t)) return [run(), think, ...words('Here are the open items.'), payload('table', { columns: ['Task', 'Owner', 'Status'], rows: [{ cells: ['Search latency budget', 'Team B', 'In review'], tag: { column: 2, tone: 'blue' } }, { cells: ['Migrate the old exports', 'Team C', 'Blocked'], tag: { column: 2, tone: 'red' } }] }), end];
  return demoScript();
}

/** The plain text of a script, for a server that stores what it said. */
export const scriptText = (steps: ScriptStep[]): string => steps.map((step) => ('frame' in step && step.frame.type === 'text_delta' ? step.frame.delta : '')).join('');
