import { DEFAULT_VIEW, PRIVACY_PRESETS, type ArgsMode, type Privacy, type ResultMode } from "./options";
import { Overview } from "./overview";
import { scenarioById } from "./library";
import { ScenarioChat } from "./scenario-chat";
import type { Fault } from "./scenario";

export interface CapabilitiesProps {
  /** `overview`: every state on one page, settled. `player`: one scenario in your hand. */
  readonly mode: "overview" | "player";
  readonly scenario: string;
  readonly transport: "chunks" | "frames";
  readonly fault: Fault;
  readonly speed: number;
  readonly autoplay: boolean;
  readonly runBlock: boolean;
  readonly privacy: Privacy;
  readonly argsMode: ArgsMode | "default";
  readonly resultMode: ResultMode | "default";
  readonly labelsOnly: boolean;
  readonly showReasoningText: boolean;
  readonly defaultOpen: boolean;
  readonly dir: "ltr" | "rtl";
  readonly locale: string;
}

/** What the story's args say about a reader, as the options the shipped Run renderer takes. */
export const viewOf = (args: CapabilitiesProps) => ({
  ...DEFAULT_VIEW,
  runBlock: args.runBlock,
  defaultOpen: args.defaultOpen,
  labelsOnly: args.labelsOnly,
  showReasoningText: args.showReasoningText,
  ...PRIVACY_PRESETS[args.privacy],
  ...(args.argsMode === "default" ? {} : { argsMode: args.argsMode }),
  ...(args.resultMode === "default" ? {} : { resultMode: args.resultMode }),
});

export function Capabilities(args: CapabilitiesProps) {
  const view = viewOf(args);
  if (args.mode === "overview") return <Overview args={{ view, locale: args.locale, dir: args.dir }} />;
  // Any change to what is played restarts the turn: a stream already in flight keeps the settings it started with.
  const signature = JSON.stringify([args.scenario, args.transport, args.fault, args.speed, args.autoplay, view, args.locale, args.dir]);
  return (
    <div className="p-4">
      <ScenarioChat key={signature} scenario={scenarioById(args.scenario)} transport={args.transport} fault={args.fault} speed={args.speed} autoplay={args.autoplay} view={view} locale={args.locale} dir={args.dir} full />
    </div>
  );
}
