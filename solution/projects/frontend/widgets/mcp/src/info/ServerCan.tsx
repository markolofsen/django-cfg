'use client';

import { useState } from 'react';

import { Button, Collapsible, CollapsibleContent, CollapsibleTrigger } from '@djangocfg/ui-core/components';

import { useMcpConnect } from '../connect/context';
import { HINT, NAME } from '../connect/styles';

/** Rows shown before the rest folds away. */
export const VISIBLE_TOOLS = 5;

/** "This connector can": the server's tools, one line each. Renders nothing until `/info/` answered with tools. */
export function ServerCan() {
  const { server, labels } = useMcpConnect();
  const [open, setOpen] = useState(false);
  const tools = server.info?.tools ?? [];
  if (!tools.length) return null;
  const rest = tools.length - VISIBLE_TOOLS;
  const row = (tool: (typeof tools)[number]) => (
    <li key={tool.name} className="flex flex-col">
      <span translate="no" className={NAME}>{tool.name}</span>
      {tool.description ? <span className={`${HINT} line-clamp-2`}>{tool.description}</span> : null}
    </li>
  );
  return (
    <section className="flex flex-col gap-2 rounded-xl border border-border bg-background p-4">
      <span className={NAME}>{labels.canTitle}</span>
      <Collapsible open={open} onOpenChange={setOpen}>
        <ul className="flex flex-col gap-2">{tools.slice(0, VISIBLE_TOOLS).map(row)}</ul>
        {rest > 0 ? (
          <>
            <CollapsibleContent>
              <ul className="mt-2 flex flex-col gap-2">{tools.slice(VISIBLE_TOOLS).map(row)}</ul>
            </CollapsibleContent>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="mt-2 h-auto px-1 py-1 text-sm">
                {open ? labels.canLess : labels.canMore.replace('{count}', String(rest))}
              </Button>
            </CollapsibleTrigger>
          </>
        ) : null}
      </Collapsible>
    </section>
  );
}
