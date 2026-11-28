/**
 * Attachments: what a turn may carry besides words, and who decides.
 *
 * The host decides — `AttachmentsCapability` is the whole feature, and absent
 * means the composer has no button, no drop target and no paste handling.
 * This file is the pure half: kinds, limits and validation. No React, no I/O.
 */

/** The vocabulary a host speaks. A MIME list is the escape hatch (`accept`), not the front door. */
export type AttachmentKind = "image" | "audio" | "video" | "text" | "document";

/** A file the host's `upload` stored. What the transcript and the adapter receive. */
export interface Attachment {
  /** Stable within the turn. The host's own id when it has one, else chat makes one. */
  readonly id: string;
  readonly name: string;
  readonly mime: string;
  readonly size: number;
  readonly kind: AttachmentKind;
  /** Where the stored bytes are served from. */
  readonly url: string;
}

export interface AttachmentUploadContext {
  readonly signal: AbortSignal;
  /** 0..1. Optional to call: a host with no progress signal leaves the chip indeterminate. */
  readonly onProgress: (fraction: number) => void;
}

/** What `upload` resolves with. `id` and `url` are the host's; the rest chat already knows. */
export interface UploadedAttachment {
  readonly url: string;
  readonly id?: string;
}

export interface AttachmentsCapability {
  /**
   * Store one file. Rejecting shows the message on the chip and keeps the rest.
   * Back it with the forms Uploader or a generated client — chat knows no endpoint.
   */
  readonly upload: (file: File, context: AttachmentUploadContext) => Promise<UploadedAttachment>;
  /** Kinds accepted. Default `DEFAULT_ATTACHMENT_KINDS`. */
  readonly kinds?: readonly AttachmentKind[];
  /** Extra MIME types (`application/zip`, `image/*`) or extensions (`.csv`) on top of the kinds. */
  readonly accept?: readonly string[];
  /** Per file, in bytes. Default `DEFAULT_MAX_FILE_BYTES`. */
  readonly maxFileSize?: number;
  /** Files per turn. Default `DEFAULT_MAX_FILES`. */
  readonly maxFiles?: number;
}

export const DEFAULT_ATTACHMENT_KINDS: readonly AttachmentKind[] = ["image", "audio", "text", "document"];
export const DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024;
export const DEFAULT_MAX_FILES = 5;

/**
 * Same grouping as the forms uploader's `ASSET_TYPE_ACCEPT`, plus `text`, which
 * it has no group for. Kept here rather than imported: chat must not pull the
 * form stack.
 */
const KIND_ACCEPT: Record<AttachmentKind, readonly string[]> = {
  image: ["image/*"],
  audio: ["audio/*"],
  video: ["video/*"],
  text: ["text/*", ".md", ".markdown", ".txt", ".log", ".json", ".csv", ".yaml", ".yml", ".xml"],
  document: ["application/pdf", ".pdf", ".doc", ".docx", ".odt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx"],
};

export interface ResolvedAttachments {
  readonly kinds: readonly AttachmentKind[];
  readonly accept: readonly string[];
  readonly maxFileSize: number;
  readonly maxFiles: number;
}

/** Defaults filled in once, so no caller re-derives them. */
export function resolveAttachments(capability: AttachmentsCapability): ResolvedAttachments {
  const kinds = capability.kinds ?? DEFAULT_ATTACHMENT_KINDS;
  const accept = [...kinds.flatMap((kind) => KIND_ACCEPT[kind]), ...(capability.accept ?? [])];
  return {
    kinds,
    accept: [...new Set(accept)],
    maxFileSize: capability.maxFileSize ?? DEFAULT_MAX_FILE_BYTES,
    maxFiles: Math.max(1, capability.maxFiles ?? DEFAULT_MAX_FILES),
  };
}

/** The `accept` attribute of a file input. */
export const acceptAttribute = (resolved: ResolvedAttachments): string => resolved.accept.join(",");

const TEXT_EXTENSIONS = new Set(["md", "markdown", "txt", "log", "json", "csv", "yaml", "yml", "xml"]);

function extensionOf(name: string): string {
  const dot = name.lastIndexOf(".");
  return dot < 0 ? "" : name.slice(dot + 1).toLowerCase();
}

/** The kind of a file by its MIME, falling back to the extension (a `.md` often arrives as an empty or odd type). */
export function kindOf(file: { readonly name: string; readonly type: string }): AttachmentKind {
  const type = file.type.toLowerCase();
  if (type.startsWith("image/")) return "image";
  if (type.startsWith("audio/")) return "audio";
  if (type.startsWith("video/")) return "video";
  if (type.startsWith("text/") || TEXT_EXTENSIONS.has(extensionOf(file.name))) return "text";
  return "document";
}

function matchesAccept(file: { readonly name: string; readonly type: string }, accept: readonly string[]): boolean {
  const type = file.type.toLowerCase();
  const ext = `.${extensionOf(file.name)}`;
  return accept.some((rule) => {
    const r = rule.toLowerCase();
    if (r.startsWith(".")) return r === ext;
    if (r.endsWith("/*")) return type.startsWith(r.slice(0, -1));
    return r === type;
  });
}

export type AttachmentRejection = "type" | "size" | "count";

/**
 * Whether one file may join a turn that already holds `held` files.
 * Returns the reason, or `null` when it may. Count is checked last so a file that
 * is wrong anyway says so rather than "too many".
 */
export function rejectionFor(
  file: { readonly name: string; readonly type: string; readonly size: number },
  held: number,
  resolved: ResolvedAttachments,
): AttachmentRejection | null {
  if (!matchesAccept(file, resolved.accept)) return "type";
  if (file.size > resolved.maxFileSize) return "size";
  if (held >= resolved.maxFiles) return "count";
  return null;
}

/** Human size, 1024-based, one decimal at most. */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value >= 10 ? Math.round(value) : Math.round(value * 10) / 10} ${units[i]}`;
}
