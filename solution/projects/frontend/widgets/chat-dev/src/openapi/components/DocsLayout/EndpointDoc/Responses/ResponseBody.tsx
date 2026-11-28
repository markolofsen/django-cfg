'use client';

import { useMemo } from 'react';

import { CopyButton } from '@djangocfg/ui-core/components';

import { JsonTree } from '@djangocfg/widget-data/json-tree';

interface ResponseBodyProps {
    example: string;
    contentType?: string;
}

/** Render the example response body: content-type strip + copy button
 *  header, then the JSON tree (falling back to a ``<pre>`` if the
 *  example isn't valid JSON — sampler occasionally emits non-JSON for
 *  exotic content types). */
export function ResponseBody({ example, contentType }: ResponseBodyProps) {
    // Parse once and cache. ``example`` is pre-stringified by the
    // sampler; JsonTree wants a live object to render nodes with proper
    // folding, so we flip it back here.
    const parsed = useMemo(() => {
        try {
            return JSON.parse(example);
        } catch {
            return null;
        }
    }, [example]);

    return (
        <div className="border-t bg-muted/20">
            <div className="flex items-center justify-between px-3 py-1.5 border-b border-border/50">
                <code className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/70">
                    {contentType ?? 'application/json'}
                </code>
                <CopyButton
                    value={example}
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-[10px] text-muted-foreground"
                >
                    Copy
                </CopyButton>
            </div>
            {parsed != null ? (
                // Docs longread is space-constrained: no toolbar (Copy
                // lives on the row header above), no border (host owns
                // it), shallow auto-expand.
                <JsonTree
                    data={parsed}
                    toolbar="never"
                    bordered={false}
                    defaultExpandedDepth={1}
                />
            ) : (
                <pre className="p-3 text-[11px] font-mono text-foreground/70 whitespace-pre-wrap break-all leading-relaxed">
                    {example}
                </pre>
            )}
        </div>
    );
}
