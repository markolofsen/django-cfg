import { ChevronDown } from "lucide-react";

import { MenuBuilder } from "@djangocfg/ui-core/components";

import { useChatCopy } from "../../../i18n";
import { useCapabilities } from "../../store/hooks";
import { ComposerButton } from "./button";

/**
 * The model switch: the current choice as a quiet text chip that opens a radio menu above the composer.
 * Renders nothing without a `models` capability (or with fewer than two options: one choice is no choice).
 */
export function ComposerModel({ className }: { readonly className?: string }) {
  const models = useCapabilities().models;
  const copy = useChatCopy().composer;
  if (models === undefined || models.options.length < 2) return null;
  const current = models.options.find((option) => option.id === models.value) ?? models.options[0]!;
  return (
    <MenuBuilder
      side="top"
      align="end"
      sideOffset={8}
      items={[
        {
          kind: "radio-group",
          id: "model",
          label: copy.model,
          value: current.id,
          onValueChange: models.onChange,
          options: models.options.map((option) => ({ id: option.id, value: option.id, label: option.label, ...(option.hint ? { description: option.hint } : {}) })),
        },
      ]}
    >
      <ComposerButton type="button" wide className={className} aria-label={`${copy.model}: ${current.label}`} tooltip={copy.model} data-testid="composer-model">
        <span className="text-sm">{current.label}</span>
        <ChevronDown className="size-3.5" aria-hidden="true" />
      </ComposerButton>
    </MenuBuilder>
  );
}
