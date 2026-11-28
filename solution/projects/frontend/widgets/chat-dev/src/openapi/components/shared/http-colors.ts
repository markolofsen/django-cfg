/**
 * Shared HTTP method + status → semantic status-token mappings.
 *
 * Single source of truth for the badge colours used across the OpenAPI
 * viewer (method pills in the request list, status pills in responses).
 * Uses ui-core's semantic status surface tokens (the tinted banner set:
 * `bg-{status}-background` + `text-{status}-foreground` + `border-{status}-border`)
 * so badges adapt to theme + preset instead of hardcoded colour scales.
 *
 * HTTP → status mapping:
 *   2xx / GET → success · 3xx → info · 4xx / PUT / PATCH → warning ·
 *   5xx / DELETE → destructive · POST → info.
 */

type StatusKind = 'success' | 'info' | 'warning' | 'destructive';

const BADGE_CLASS: Record<StatusKind, string> = {
    success: 'bg-success-background text-success-foreground border-success-border',
    info: 'bg-info-background text-info-foreground border-info-border',
    warning: 'bg-warning-background text-warning-foreground border-warning-border',
    destructive: 'bg-destructive-background text-destructive-foreground border-destructive-border',
};

const NEUTRAL_BADGE = 'bg-muted text-muted-foreground border-border';

const METHOD_KIND: Record<string, StatusKind> = {
    GET: 'success',
    POST: 'info',
    PUT: 'warning',
    PATCH: 'warning',
    DELETE: 'destructive',
};

/** Badge classes for an HTTP method. Unknown methods fall back to neutral. */
export function getMethodStyle(method: string): string {
    const kind = METHOD_KIND[method.toUpperCase()];
    return kind ? BADGE_CLASS[kind] : NEUTRAL_BADGE;
}

function statusKind(status: number): StatusKind {
    if (status >= 500) return 'destructive';
    if (status >= 400) return 'warning';
    if (status >= 300) return 'info';
    return 'success';
}

/** Badge classes for a numeric HTTP status code. */
export function getStatusStyle(status: number): string {
    return BADGE_CLASS[statusKind(status)];
}

/**
 * Badge classes for an HTTP status *code string* (e.g. ``"200"``,
 * ``"default"``). Non-numeric codes render neutral so we never flash a
 * wrong-severity colour at the user.
 */
export function getStatusCodeStyle(code: string): string {
    const numeric = Number.parseInt(code, 10);
    if (!Number.isFinite(numeric)) return NEUTRAL_BADGE;
    return getStatusStyle(numeric);
}
