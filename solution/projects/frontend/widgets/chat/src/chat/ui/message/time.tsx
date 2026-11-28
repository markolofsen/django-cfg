import { cn } from "@djangocfg/ui-core/lib";
import { formatTimeOfDay } from "@djangocfg/widget-kit";

import type { ChatMessage } from "../../core/conversation/parts";

/**
 * The time a message was sent, quiet beside its actions and shown with them (on hover or focus within the row).
 *
 * The instant is stored as UTC (an ISO string on the wire, epoch milliseconds in the message) and drawn in the READER'S zone and
 * locale by `formatTimeOfDay` — no zone name is ever shown. The exact instant stays one hover away in the native `title` as UTC
 * ISO, which is also the `dateTime` a machine reads. A message with no usable time draws nothing.
 */
export function MessageTime({ message, className }: { readonly message: ChatMessage; readonly className?: string }) {
  const at = message.createdAt;
  if (!at) return null;
  const label = formatTimeOfDay(at);
  if (label === "") return null;
  const iso = new Date(at).toISOString();
  return (
    <time
      dateTime={iso}
      title={iso}
      className={cn(
        "text-xs text-muted-foreground tabular-nums opacity-0 transition-opacity",
        "group-hover:opacity-100 group-focus-within:opacity-100",
        className,
      )}
    >
      {label}
    </time>
  );
}
