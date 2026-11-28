/**
 * Files on the draft: validated, uploaded, and tracked until the turn is sent.
 *
 * Not part of `Draft` — a draft holds only what can be sent, and a file still
 * uploading or refused is neither. The hook returns the `uploaded` list for the
 * draft to carry and `uploading` for `canSend` to wait on.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  kindOf,
  rejectionFor,
  resolveAttachments,
  type Attachment,
  type AttachmentKind,
  type AttachmentRejection,
  type AttachmentsCapability,
  type ResolvedAttachments,
} from "../../core/compose/attachments";

export type StagedStatus =
  | { readonly state: "uploading"; readonly progress: number | undefined }
  | { readonly state: "done"; readonly attachment: Attachment }
  /** `reason` is a validation verdict, or `upload` when the host's function rejected (with its `message`). */
  | { readonly state: "error"; readonly reason: AttachmentRejection | "upload"; readonly message?: string };

export interface StagedAttachment {
  readonly id: string;
  readonly name: string;
  readonly size: number;
  readonly kind: AttachmentKind;
  readonly status: StagedStatus;
}

export interface AttachmentsApi {
  /** Everything on the draft, in the order added, failures included. */
  readonly staged: readonly StagedAttachment[];
  /** The stored files — what the draft carries. */
  readonly uploaded: readonly Attachment[];
  readonly uploading: boolean;
  /** Null when the host gave no `attachments` capability. */
  readonly resolved: ResolvedAttachments | null;
  readonly addFiles: (files: Iterable<File>) => void;
  readonly remove: (id: string) => void;
  /** Drop everything; aborts what is still uploading. */
  readonly clear: () => void;
}

let counter = 0;
const makeId = (): string => (typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `att-${(counter += 1)}`);

export function useAttachments(capability: AttachmentsCapability | undefined): AttachmentsApi {
  const [staged, setStaged] = useState<readonly StagedAttachment[]>([]);
  const controllers = useRef(new Map<string, AbortController>());
  const resolved = useMemo(() => (capability === undefined ? null : resolveAttachments(capability)), [capability]);

  // Read through refs: an upload outlives the render that started it, and must
  // see the latest capability and list without being re-created.
  const capabilityRef = useRef(capability);
  capabilityRef.current = capability;
  const resolvedRef = useRef(resolved);
  resolvedRef.current = resolved;
  const stagedRef = useRef(staged);
  stagedRef.current = staged;

  const patch = useCallback((id: string, status: StagedStatus) => {
    setStaged((current) => current.map((item) => (item.id === id ? { ...item, status } : item)));
  }, []);

  const addFiles = useCallback(
    (files: Iterable<File>) => {
      const cap = capabilityRef.current;
      const rules = resolvedRef.current;
      if (cap === undefined || rules === null) return;
      // Counted as we go: five files dropped at once must not all see "0 held".
      let held = stagedRef.current.filter((item) => item.status.state !== "error").length;
      const added: StagedAttachment[] = [];
      for (const file of files) {
        const id = makeId();
        const kind = kindOf(file);
        const base = { id, name: file.name, size: file.size, kind };
        const reason = rejectionFor(file, held, rules);
        if (reason !== null) {
          added.push({ ...base, status: { state: "error", reason } });
          continue;
        }
        held += 1;
        added.push({ ...base, status: { state: "uploading", progress: undefined } });
        const controller = new AbortController();
        controllers.current.set(id, controller);
        void cap
          .upload(file, { signal: controller.signal, onProgress: (fraction) => patch(id, { state: "uploading", progress: Math.min(1, Math.max(0, fraction)) }) })
          .then((stored) => {
            if (controller.signal.aborted) return;
            patch(id, { state: "done", attachment: { id: stored.id ?? id, name: file.name, mime: file.type || "application/octet-stream", size: file.size, kind, url: stored.url } });
          })
          .catch((error: unknown) => {
            if (controller.signal.aborted) return;
            patch(id, { state: "error", reason: "upload", message: error instanceof Error ? error.message : undefined });
          })
          .finally(() => {
            controllers.current.delete(id);
          });
      }
      if (added.length > 0) setStaged((current) => [...current, ...added]);
    },
    [patch],
  );

  const remove = useCallback((id: string) => {
    controllers.current.get(id)?.abort();
    controllers.current.delete(id);
    setStaged((current) => current.filter((item) => item.id !== id));
  }, []);

  const clear = useCallback(() => {
    for (const controller of controllers.current.values()) controller.abort();
    controllers.current.clear();
    setStaged([]);
  }, []);

  useEffect(() => {
    const live = controllers.current;
    return () => {
      for (const controller of live.values()) controller.abort();
      live.clear();
    };
  }, []);

  const uploaded = useMemo(
    () => staged.flatMap((item) => (item.status.state === "done" ? [item.status.attachment] : [])),
    [staged],
  );
  const uploading = staged.some((item) => item.status.state === "uploading");

  return useMemo(
    () => ({ staged, uploaded, uploading, resolved, addFiles, remove, clear }),
    [staged, uploaded, uploading, resolved, addFiles, remove, clear],
  );
}
