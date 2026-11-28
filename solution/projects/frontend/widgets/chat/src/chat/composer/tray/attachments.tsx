import { AlertCircle, FileText, Film, Image as ImageIcon, Loader2, Music, X } from "lucide-react";

import { formatBytes, type AttachmentKind } from "../../core/compose/attachments";
import { useChatCopy } from "../../../i18n";
import type { StagedAttachment } from "../../store/composing/use-attachments";
import { useComposer } from "../context";

const KIND_ICON: Record<AttachmentKind, typeof FileText> = {
  image: ImageIcon,
  audio: Music,
  video: Film,
  text: FileText,
  document: FileText,
};

export interface ComposerAttachmentsProps {
  readonly className?: string;
}

/** The one-line reason a file was refused. */
function useReason() {
  const copy = useChatCopy().composer;
  return (item: StagedAttachment): string => {
    const { status } = item;
    if (status.state !== "error") return "";
    if (status.reason === "type") return copy.attachTypeRefused;
    if (status.reason === "size") return copy.attachTooLarge;
    if (status.reason === "count") return copy.attachTooMany;
    return status.message ?? copy.attachFailed;
  };
}

/**
 * The files on this draft, a block of their own above the composer's box (`Composer before`), not chips inside it: each accepted file is a full-width row (thumbnail or icon, name, size or
 * progress, remove), so a long name reads and the row is a target. Past four rows the block scrolls instead of growing. Every refused file folds into one row of the same width
 * (`3 × reason`, the names in its tooltip) with one button that clears them. Renders null when there are none.
 */
export function ComposerAttachments({ className }: ComposerAttachmentsProps) {
  const { files } = useComposer();
  return <ComposerAttachmentsView items={files.staged} onRemove={files.remove} className={className} />;
}

export interface ComposerAttachmentsViewProps extends ComposerAttachmentsProps {
  readonly items: readonly StagedAttachment[];
  readonly onRemove: (id: string) => void;
}

/** The tray from plain data, with no composer around it: what `ComposerAttachments` draws, and what a story or a host with its own staging can feed directly. */
export function ComposerAttachmentsView({ items, onRemove, className }: ComposerAttachmentsViewProps) {
  const copy = useChatCopy().composer;
  const reason = useReason();
  if (items.length === 0) return null;
  const failed = items.filter((item) => item.status.state === "error");
  const ok = items.filter((item) => item.status.state !== "error");
  const reasons = [...new Set(failed.map(reason))];
  return (
    <div className={className ?? "mb-2 flex w-full min-w-0 flex-col gap-1"}>
      {ok.length > 0 ? (
        <ul aria-label={copy.attachments} className="flex max-h-[10.5rem] min-w-0 flex-col gap-1 overflow-y-auto [scrollbar-width:thin]">
          {ok.map((item) => (
            <li key={item.id}>
              <AttachmentChip item={item} onRemove={onRemove} />
            </li>
          ))}
        </ul>
      ) : null}
      {failed.length > 0 ? (
        <div
          role="alert"
          data-state="error"
          title={failed.map((item) => item.name).join("\n")}
          className="flex min-w-0 items-center gap-2 rounded-lg border border-destructive/50 bg-background px-2.5 py-1.5 text-sm text-destructive"
        >
          <AlertCircle className="size-4 shrink-0" aria-hidden />
          <span className="min-w-0 flex-1 truncate">
            {failed.length > 1 ? `${failed.length} × ` : `${failed[0]?.name} · `}
            {reasons.join(" · ")}
          </span>
          <button
            type="button"
            aria-label={copy.attachRemove}
            onClick={() => failed.forEach((item) => onRemove(item.id))}
            className="shrink-0 rounded-sm opacity-70 hover:opacity-100 focus-visible:outline focus-visible:outline-2"
          >
            <X className="size-4" aria-hidden />
          </button>
        </div>
      ) : null}
    </div>
  );
}

function AttachmentChip({ item, onRemove }: { readonly item: StagedAttachment; readonly onRemove: (id: string) => void }) {
  const copy = useChatCopy().composer;
  const { status } = item;
  const Icon = KIND_ICON[item.kind];
  const uploading = status.state === "uploading";
  const progress = uploading ? status.progress : undefined;
  // A stored picture shows itself instead of a generic icon.
  const thumb = status.state === "done" && item.kind === "image" ? status.attachment.url : null;
  return (
    <div data-state={status.state} title={item.name} className="relative flex w-full items-center gap-2.5 overflow-hidden rounded-lg border border-border bg-background px-2.5 py-1.5 text-sm text-foreground">
      {thumb ? (
        <img src={thumb} alt="" className="size-7 shrink-0 rounded-md object-cover" />
      ) : (
        <span className="grid size-7 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground">
          {uploading ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Icon className="size-4" aria-hidden />}
        </span>
      )}
      <span className="min-w-0 flex-1 truncate">{item.name}</span>
      <span className="shrink-0 text-xs text-muted-foreground">{progress !== undefined ? `${Math.round(progress * 100)}%` : formatBytes(item.size)}</span>
      <button
        type="button"
        aria-label={copy.attachRemove}
        onClick={() => onRemove(item.id)}
        className="shrink-0 rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline focus-visible:outline-2"
      >
        <X className="size-4" aria-hidden />
      </button>
      {uploading ? (
        <span aria-hidden className="absolute inset-x-0 bottom-0 h-0.5 bg-primary/20">
          <span className={`block h-full bg-primary transition-[width] ${progress === undefined ? "w-1/3 animate-pulse" : ""}`} style={progress === undefined ? undefined : { width: `${Math.round(progress * 100)}%` }} />
        </span>
      ) : null}
    </div>
  );
}
