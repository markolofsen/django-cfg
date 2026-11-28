'use client';

// Thin re-export so the Header barrel file stays self-contained. The
// actual badge lives in ``shared/ui`` because it's used by the sidebar
// and the playground too — duplicating styles would drift.
export { MethodBadge } from '../../../shared/ui';
