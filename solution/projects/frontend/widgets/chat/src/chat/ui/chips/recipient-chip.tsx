import { Check, Lock, Users } from "lucide-react";
import { useRef } from "react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@djangocfg/ui-core/components";

import { focusComposerField } from "../../composer/focus-field";
import { useComposer } from "../../composer/context";
import { isPrivate, type Recipient } from "../../core/room/recipient";
import { useRoomCopy } from "../../../i18n";
import { useCapabilities } from "../../store";

/** The radio group's value for "everyone"; a person's value is their id. */
const EVERYONE = "\u0000all";

/**
 * Who this line is for, above the field: "To: Everyone" by default, or one person (a private line).
 *
 * A control, not a reading of the text: tapping it opens the list of people the host passed (`recipients` capability), and
 * the choice sticks until it is changed. A private recipient is drawn in the accent with a lock, so it cannot be missed.
 * The assistant is never in the list: a question to it is a plain line. Self-gating: no capability, or nobody to write to,
 * renders nothing.
 */
export function ChatRecipientChip() {
  const copy = useRoomCopy();
  const { recipients } = useCapabilities();
  const { recipient, setRecipient } = useComposer();
  const trigger = useRef<HTMLButtonElement>(null);
  if (recipients === undefined || recipients.people.length === 0) return null;

  const priv = isPrivate(recipient);
  const choose = (value: string) => {
    const next: Recipient | undefined = value === EVERYONE ? "all" : recipients.people.find((person) => person.id === value);
    if (next !== undefined) setRecipient(next);
  };

  // A popover over the page (Radix, portalled, flips on collision), so opening it never moves the field.
  return (
    <div className="flex w-full flex-col gap-1 text-xs">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            ref={trigger}
            type="button"
            aria-label={copy.pickRecipient}
            className={`inline-flex min-h-8 w-fit max-w-full items-center gap-1.5 rounded-full px-3 py-1 ${
              priv ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"
            }`}
          >
            {priv ? <Lock className="size-3 shrink-0" aria-hidden /> : <Users className="size-3 shrink-0" aria-hidden />}
            <span className="shrink-0">{copy.to}</span>
            <span className="truncate font-medium">{priv ? recipient.label : copy.everyone}</span>
            {priv ? <span className="sr-only">{copy.privateLine}</span> : null}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          side="top"
          align="start"
          aria-label={copy.pickRecipient}
          className="max-h-[min(40dvh,var(--radix-dropdown-menu-content-available-height))] w-72 max-w-[calc(100vw-1rem)] p-1 text-sm"
          // Focus goes back to the field, not the chip: the next thing the user does is type.
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            focusComposerField(trigger.current?.closest<HTMLElement>(".composer-box"));
          }}
        >
          <DropdownMenuRadioGroup value={priv ? recipient.id : EVERYONE} onValueChange={choose}>
            <RecipientRow value={EVERYONE} label={copy.everyone} hint={copy.everyoneHint} />
            {recipients.people.map((person) => (
              <RecipientRow key={person.id} value={person.id} label={person.label} hint={copy.privateHint} locked />
            ))}
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

/** One choice: lock for a private line, people for the room, a check on the chosen one, a 44px target. */
function RecipientRow({ value, label, hint, locked = false }: { value: string; label: string; hint: string; locked?: boolean }) {
  const Icon = locked ? Lock : Users;
  return (
    <DropdownMenuRadioItem value={value} className="group min-h-11 gap-2 pl-2 [&>span:first-child]:hidden">
      <Icon className="size-3.5 shrink-0 text-muted-foreground" aria-hidden />
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate">{label}</span>
        <span className="truncate text-xs text-muted-foreground">{hint}</span>
      </span>
      <Check className="size-4 shrink-0 text-primary opacity-0 group-data-[state=checked]:opacity-100" aria-hidden />
    </DropdownMenuRadioItem>
  );
}
