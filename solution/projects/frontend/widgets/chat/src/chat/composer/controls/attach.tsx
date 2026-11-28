import { useCallback, useRef, type ReactNode } from "react";

import { acceptAttribute } from "../../core/compose/attachments";
import { useChatCopy } from "../../../i18n";
import { ComposerButton } from "./button";
import { useComposer } from "../context";

export interface ComposerAttachProps {
  readonly className?: string;
  /** The glyph (a paperclip). Required for the same reason `ComposerSend`'s is: no glyph is an empty pill. */
  readonly children: ReactNode;
}

/**
 * The attach button and its hidden file input.
 *
 * Renders nothing without an `attachments` capability, so a host that cannot
 * store a file shows no control that would fail. The accept list comes from the
 * capability's kinds, so the OS picker already filters what chat would refuse.
 */
export function ComposerAttach({ className, children }: ComposerAttachProps) {
  const { files } = useComposer();
  const copy = useChatCopy().composer;
  const input = useRef<HTMLInputElement>(null);
  const resolved = files.resolved;

  const onChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      files.addFiles(Array.from(event.target.files ?? []));
      // Reset, so choosing the same file again after removing it fires `change`.
      event.target.value = "";
    },
    [files],
  );

  if (resolved === null) return null;
  return (
    <>
      <input
        ref={input}
        type="file"
        multiple={resolved.maxFiles > 1}
        accept={acceptAttribute(resolved)}
        onChange={onChange}
        className="hidden"
        tabIndex={-1}
        aria-hidden
      />
      <ComposerButton
        type="button"
        className={className}
        aria-label={copy.attach}
        tooltip={copy.attach}
        onClick={() => input.current?.click()}
      >
        {children}
      </ComposerButton>
    </>
  );
}
