import { useState, type ReactNode } from "react";
import { I18nProvider } from "@djangocfg/i18n";
import { Button } from "@djangocfg/ui-core/components";

import { SessionsPanel } from "../../../assistant/history/sessions-panel";
import { ComposerAttachmentsView, type StagedAttachment } from "../../composer";
import { DEFAULT_VIEW, PRIVACY_PRESETS, type ViewArgs } from "./options";
import { ScenarioChat } from "./scenario-chat";
import { inGroup, scenarioById, SESSION_ROWS } from "./library";
import type { Scenario, ScenarioGroup } from "./scenario";

export interface OverviewArgs {
  readonly view: ViewArgs;
  readonly locale: string;
  readonly dir: "ltr" | "rtl";
}

/** One state: its words, the chat drawing it settled, and a button that replays it at the speed a server would send it. */
function Cell({ scenario, args, children }: { readonly scenario: Scenario; readonly args: OverviewArgs; readonly children?: ReactNode }) {
  const [live, setLive] = useState(false);
  return (
    <section className="flex min-w-0 flex-col gap-2" aria-labelledby={`cell-${scenario.id}`}>
      <header className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 id={`cell-${scenario.id}`} className="m-0 text-sm font-semibold">{scenario.title}</h3>
          <p className="m-0 text-xs text-muted-foreground">{scenario.note}</p>
        </div>
        {scenario.beats.length > 0 ? (
          <Button size="sm" variant="outline" onClick={() => setLive(true)}>{live ? "Replaying" : "Replay"}</Button>
        ) : null}
      </header>
      {children ?? <ScenarioChat key={String(live)} scenario={scenario} view={args.view} locale={args.locale} dir={args.dir} speed={live ? 1 : Number.POSITIVE_INFINITY} />}
    </section>
  );
}

const STAGED: readonly StagedAttachment[] = [
  { id: "1", name: "export-march.csv", size: 4_200_000, kind: "text", status: { state: "uploading", progress: 0.42 } },
  { id: "2", name: "recording.m4a", size: 9_800_000, kind: "audio", status: { state: "uploading", progress: undefined } },
  { id: "3", name: "video-2024-11-23.mp4", size: 48_000_000, kind: "video", status: { state: "error", reason: "type" } },
  { id: "4", name: "huge-archive.zip", size: 900_000_000, kind: "document", status: { state: "error", reason: "size" } },
];

const SESSIONS = {
  thread: { kind: "ready" as const, id: "t1", session: "t1", history: [] },
  sessions: [...SESSION_ROWS],
  busy: false,
  startNew: async () => true,
  switchTo: async () => true,
  refreshSessions: () => {},
};

const GROUPS: readonly { readonly group: ScenarioGroup; readonly title: string; readonly note: string }[] = [
  { group: "messages", title: "Messages", note: "Streaming prose, code, tables and a very long word." },
  { group: "run", title: "Reasoning", note: "A live thought, and a thought whose words never left the server." },
  { group: "tools", title: "Tool timeline", note: "Ok, error, timeout, stopped, parallel, retried, long and large." },
  { group: "blocks", title: "Questions, approvals, sources and page actions", note: "Cards the agent draws; your answer is sent as your next message." },
  { group: "failures", title: "Failures", note: "Failed after a partial answer, a lost stream, offline." },
  { group: "privacy", title: "Public and admin", note: "The same run, read by a visitor and by an operator." },
  { group: "history", title: "Sessions and history", note: "A restored thread and the list of chats." },
  { group: "attachments", title: "Attachments", note: "In a conversation and in the composer tray." },
];

/** The one scenario twice: a visitor on a public chat, and a signed-in admin. */
function PrivacyPair({ args }: { readonly args: OverviewArgs }) {
  const scenario = scenarioById("privacy");
  return (
    <>
      <Cell scenario={{ ...scenario, id: "privacy-public", title: "A visitor on a public chat", note: "Titles, statuses and one-line summaries. Arguments, results and purposes never leave the block." }} args={{ ...args, view: { ...DEFAULT_VIEW, ...args.view, ...PRIVACY_PRESETS.public } }} />
      <Cell scenario={{ ...scenario, id: "privacy-admin", title: "A signed-in admin", note: "Arguments and results, masked where the server masked and absent where it kept them back." }} args={{ ...args, view: { ...DEFAULT_VIEW, ...args.view, ...PRIVACY_PRESETS.admin, defaultOpen: true } }} />
    </>
  );
}

/** Every capability on one page, each drawn by the code the product ships. */
export function Overview({ args }: { readonly args: OverviewArgs }) {
  return (
    <I18nProvider locale={args.locale}>
      <div dir={args.dir} className="flex flex-col gap-10 p-4 text-foreground">
        {GROUPS.map(({ group, title, note }) => (
          <section key={group} className="flex flex-col gap-4" aria-labelledby={`group-${group}`}>
            <div>
              <h2 id={`group-${group}`} className="m-0 text-lg font-semibold">{title}</h2>
              <p className="m-0 text-sm text-muted-foreground">{note}</p>
            </div>
            <div className="grid gap-6 md:grid-cols-2">
              {group === "privacy" ? <PrivacyPair args={args} /> : inGroup(group).map((scenario) => <Cell key={scenario.id} scenario={scenario} args={args} />)}
              {group === "history" ? (
                <section className="flex min-w-0 flex-col gap-2" aria-labelledby="cell-sessions">
                  <h3 id="cell-sessions" className="m-0 text-sm font-semibold">The list of chats</h3>
                  <p className="m-0 text-xs text-muted-foreground">Grouped by day, with a New chat row. The open chat is marked.</p>
                  <div className="h-[24rem] overflow-hidden rounded-[var(--radius)] border border-border bg-background">
                    <SessionsPanel session={SESSIONS} onDone={() => {}} locale={args.locale} />
                  </div>
                </section>
              ) : null}
              {group === "attachments" ? (
                <section className="flex min-w-0 flex-col gap-2" aria-labelledby="cell-tray">
                  <h3 id="cell-tray" className="m-0 text-sm font-semibold">In the composer</h3>
                  <p className="m-0 text-xs text-muted-foreground">Uploading with progress, and refused files with the reason.</p>
                  <div className="rounded-[var(--radius)] border border-border bg-background p-3">
                    <ComposerAttachmentsView items={STAGED} onRemove={() => {}} />
                  </div>
                </section>
              ) : null}
            </div>
          </section>
        ))}
      </div>
    </I18nProvider>
  );
}
