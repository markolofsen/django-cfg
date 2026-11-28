import { useEffect, useMemo, useState, type ReactNode } from "react";
import { I18nProvider } from "@djangocfg/i18n";

import { AssistantChat, useAssistantCopy, type DataPartRenderer } from "../../../assistant/shell";
import { DEMO_RENDERERS } from "../../../assistant/examples/demo/widgets";
import { KB_RENDERERS } from "../../../assistant/examples/kb-assistant";
import { fromStoredThread } from "../../../assistant/session";
import { createActionRenderer, readUiAction, type ProposalQueue } from "../../../page-tooling/copilot";
import type { Proposal } from "../../../page-tooling/copilot/actions/proposal";
import type { ActionOutcome } from "../../../page-tooling/browser-bridge/perform";
import type { PartRegistry, PartRenderProps } from "../../primitives";
import { createChatStore } from "../../store";
import { DataRenderer } from "../../ui";
import { createRunRenderer } from "../../ui/run";
import { runOptionsOf, DEFAULT_VIEW, type ViewArgs } from "./options";
import { PlayerBar } from "./player-bar";
import { createSlot, scenarioAdapter, type Transport } from "./run";
import { storedTurn, type Fault, type Scenario } from "./scenario";

/** What the host draws by `kind`: the assistant's own examples, so every card is code a host ships. */
const HOST_KINDS: Readonly<Record<string, DataPartRenderer>> = { ...DEMO_RENDERERS, ...KB_RENDERERS };

/** The assistant's own `data` composition (the host's kinds first, then the widget's cards). */
function hostData(props: PartRenderProps): ReactNode {
  const { part } = props;
  if (part.type === "data") {
    const drawn = HOST_KINDS[part.kind]?.(part.data, props);
    if (drawn !== undefined) return drawn;
  }
  return DataRenderer(props);
}

/** The proposals a scenario makes, answered the way the story's `outcome` says. This queue records an answer; it never touches a page (the real gate is `PageCopilot Live`). */
function useProposalQueue(scenario: Scenario, outcome: ActionOutcome | "pending"): ProposalQueue {
  const [proposals, setProposals] = useState<readonly Proposal[]>(() => {
    if (outcome === "pending") return [];
    return scenario.beats.flatMap((beat) => {
      const block = beat.kind === "payload" && beat.name === "ui-action" ? readUiAction(beat.data) : null;
      return block === null ? [] : [{ id: block.id, action: block.action, label: block.label, state: { status: "settled", outcome } } satisfies Proposal];
    });
  });
  return useMemo<ProposalQueue>(() => {
    const settle = (id: string, action: Proposal["action"], label: string, result: ActionOutcome) =>
      setProposals((held) => (held.some((proposal) => proposal.id === id) ? held : [...held, { id, action, label, state: { status: "settled", outcome: result } }]));
    return {
      proposals,
      add: () => {},
      approve: async (id, action, label) => settle(id, action, label ?? "", "approved"),
      reject: (id, action, label) => {
        if (action !== undefined) settle(id, action, label ?? "", "rejected");
      },
      expire: () => {},
    };
  }, [proposals]);
}

export interface ScenarioChatProps {
  readonly scenario: Scenario;
  readonly transport?: Transport;
  readonly fault?: Fault;
  readonly speed?: number;
  readonly autoplay?: boolean;
  readonly view?: ViewArgs;
  /** Show the player bar and the real composer; off for an overview cell. */
  readonly full?: boolean;
  readonly outcome?: ActionOutcome | "pending";
  readonly locale?: string;
  readonly dir?: "ltr" | "rtl";
  readonly height?: string;
}

/** One scenario in a real assistant chat: the production adapter or the chunk path, the shipped renderers, the shipped composer. */
export function ScenarioChat(props: ScenarioChatProps) {
  const [generation, setGeneration] = useState(0);
  const { locale = "en", dir = "ltr" } = props;
  return (
    <I18nProvider locale={locale}>
      <div dir={dir}>
        <Turn key={generation} {...props} onRestart={() => setGeneration((n) => n + 1)} />
      </div>
    </I18nProvider>
  );
}

function Turn({ scenario, transport = "frames", fault = "none", speed = 1, autoplay = true, view = DEFAULT_VIEW, full = false, outcome = "pending", height = full ? "36rem" : "24rem", onRestart }: ScenarioChatProps & { readonly onRestart: () => void }) {
  const copy = useAssistantCopy();
  const [notice, setNotice] = useState<"reconnecting" | null>(null);
  const [{ slot, store, adapter }] = useState(() => {
    const made = createSlot();
    const built = scenarioAdapter(scenario, { transport, fault, speed, autoplay, failed: copy.failed, slot: made });
    return { slot: made, adapter: built, store: createChatStore({ adapter: built, makeId: () => globalThis.crypto.randomUUID(), now: () => Date.now() }) };
  });
  const queue = useProposalQueue(scenario, outcome);

  useEffect(() => {
    if (scenario.history !== undefined) store.load(scenario.history);
    if (scenario.beats.length > 0) void store.send({ text: scenario.prompt });
    return () => store.stop();
  }, [store, scenario]);

  // The faults that act on the host rather than on the stream.
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;
    let unwatch = () => {};
    const watch = () => {
      unwatch();
      const player = slot.get();
      if (player === null) return;
      unwatch = player.subscribe(() => {
        const state = player.getState();
        if (fault === "abort" && !stopped && state.index >= Math.ceil(state.total / 2)) {
          stopped = true;
          store.stop();
        }
        if (fault === "reconnect" && state.finished && timer === undefined) {
          setNotice("reconnecting");
          timer = setTimeout(() => {
            store.load(fromStoredThread(storedTurn(scenario), copy.failed));
            setNotice(null);
          }, 1500);
        }
      });
    };
    const drop = slot.subscribe(watch);
    watch();
    return () => {
      drop();
      unwatch();
      if (timer !== undefined) clearTimeout(timer);
    };
  }, [slot, store, fault, scenario, copy.failed]);

  const renderers = useMemo<PartRegistry>(
    () => ({
      ...(view.runBlock ? { run: createRunRenderer(runOptionsOf(view)) } : {}),
      data: createActionRenderer({ queue, fallback: hostData }),
    }),
    [view, queue],
  );

  return (
    <div className="flex flex-col overflow-hidden rounded-[var(--radius)] border border-border bg-background text-foreground">
      {full ? <PlayerBar slot={slot} onRestart={onRestart} fault={fault} note={scenario.note} /> : null}
      <div style={{ height }} className="min-h-0">
        <AssistantChat
          adapter={adapter}
          store={store}
          renderers={renderers}
          notice={notice}
          {...(full ? {} : { readOnly: <></> })}
          className="h-full"
        />
      </div>
    </div>
  );
}
