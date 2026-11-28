import type { MessagePart } from "../../../core/conversation/parts";
import { decodeStep, stepPart } from "../../../../assistant/wire/trace";

/** A step part as the server would have sent it (the real decoder and mapping), for stories and tests. Not shipped. */
export function step(id: string, over: Record<string, unknown> = {}, messageId = "m"): MessagePart {
  const decoded = decodeStep({ v: 1, step_id: id, seq: Number(id.replace(/\D/g, "")) || 1, kind: "tool", status: "ok", name: "kb_search", redaction: "none", ...over });
  if (decoded === null) throw new Error(`bad step ${id}`);
  return stepPart(messageId, decoded);
}
