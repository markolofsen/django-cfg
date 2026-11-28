import { AlertTriangle, Cpu, FileText, Gauge, Hourglass, Pencil, Search, Share2, ShieldCheck, StickyNote, Wrench, XCircle } from "lucide-react";
import type { ComponentType } from "react";

import { isFailedStatus, type RunStep } from "../../core/run/view";
import { stepVerb, type RunVerbWord } from "../../core/run/phrase";

type Icon = ComponentType<{ className?: string; "aria-hidden"?: boolean }>;

const VERB_ICONS: Readonly<Record<RunVerbWord, Icon>> = { read: FileText, search: Search, write: Pencil, think: Hourglass, other: Wrench };

const KIND_ICONS: Readonly<Record<string, Icon>> = {
  model: Cpu,
  approval: ShieldCheck,
  guardrail: ShieldCheck,
  handoff: Share2,
  source: FileText,
  error: AlertTriangle,
  usage: Gauge,
  note: StickyNote,
};

/** One small icon per step: the kind of work, or a red cross when it failed or was stopped. */
export function StepIcon({ step }: { step: RunStep }) {
  const Icon = isFailedStatus(step.status) || step.status === "cancelled" ? XCircle : step.kind === "tool" || step.kind === "reasoning" ? VERB_ICONS[stepVerb(step)] : (KIND_ICONS[step.kind] ?? StickyNote);
  return <Icon className="chat-run-icon" aria-hidden />;
}
