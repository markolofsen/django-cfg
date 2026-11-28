// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center py-10 text-sm text-muted-foreground">
      {message}
    </div>
  );
}
