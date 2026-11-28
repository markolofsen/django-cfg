import type { ReactNode } from "react";

import { useChatCopy } from "../../../i18n";
import { useCapabilities } from "../../store";
import { ComposerButton } from "./button";

export interface ComposerThinkProps {
  readonly className?: string;
  /**
   * Icon or glyph, a FUNCTION of the on/off state like `ComposerVoice`'s. The
   * accessible name comes from the label, never from this.
   */
  readonly children?: (enabled: boolean) => ReactNode;
}

/**
 * Ask the model to think longer before answering, or nothing at all.
 *
 * **No capability ⇒ absent button**, never a disabled one. Only a third of the
 * catalogue accepts the `reasoning_effort` request field, so a toggle rendered
 * unconditionally would be pressable and inert on the rest — worse than absent,
 * because it looks like it worked.
 *
 * The state is STICKY across turns (ChatGPT's behaviour): it lives on the
 * capability, which the host owns, not in the draft. A draft-held value would
 * switch itself off on every send, since `send` clears the draft.
 */
export function ComposerThink({ className, children }: ComposerThinkProps) {
  const { think } = useCapabilities();
  const copy = useChatCopy().composer;

  if (!think) return null;

  const label = think.enabled ? copy.thinkOff : copy.thinkOn;

  return (
    <ComposerButton
        tooltip={label}
        className={className}
        aria-label={label}
        // A toggle, so the state is announced rather than inferred from the icon.
        aria-pressed={think.enabled}
        onClick={() => think.setEnabled(!think.enabled)}
      >
        {children?.(think.enabled)}
      </ComposerButton>
  );
}
