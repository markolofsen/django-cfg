import type { ReactNode } from 'react';

export interface AssistantGreetingProps {
  /** The line over the starter rows ("How can I help you today?"). */
  title: ReactNode;
  /** A round mark above it: an avatar, a logo, an icon. Absent: none. */
  mark?: ReactNode;
}

/**
 * The empty room's greeting, shown in the transcript until the first message: a round mark and one line, left-aligned to
 * sit over the starter rows, near the composer where the eye already is (the Notion AI arrangement).
 */
export function AssistantGreeting({ title, mark }: AssistantGreetingProps) {
  return (
    <div className="flex h-full min-h-0 flex-col justify-end px-3 pb-2">
      {mark ? <div className="mb-3 flex size-12 items-center justify-center overflow-hidden rounded-full bg-muted text-foreground">{mark}</div> : null}
      <h3 className="text-[length:var(--greeting-font-size,1.0625rem)] font-semibold leading-tight text-foreground">{title}</h3>
    </div>
  );
}
