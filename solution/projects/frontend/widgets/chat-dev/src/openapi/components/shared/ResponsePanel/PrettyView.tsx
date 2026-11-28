'use client';

import { JsonTree } from '@djangocfg/widget-data/json-tree';
import { LazyPrettyCode as PrettyCode } from '@djangocfg/widget-kit/pretty-code/lazy';
import type { DetectedContent } from './types';

interface PrettyViewProps {
    /** Parsed JSON tree when the body was JSON. */
    treeData: unknown;
    /** Pre-stringified body — used by the code-highlight branch for
     *  non-JSON payloads. */
    rawText: string;
    detected: DetectedContent;
}

/** "Pretty" view — rich-rendering branch. JSON renders as ``JsonTree``;
 *  anything else goes through ``PrettyCode`` in ``plain`` variant so it
 *  flows naturally inside the panel's ``ScrollArea`` — no internal
 *  scroll, no floating toolbar fighting the surrounding layout. */
export function PrettyView({ treeData, rawText, detected }: PrettyViewProps) {
    if (detected.kind === 'json' && treeData != null) {
        // StatusBar already exposes "Copy", so we drop the action from
        // the toolbar — only expand/search remain. `bordered={false}` +
        // host pane owns the frame.
        return (
            <JsonTree
                title="Response Body"
                data={treeData}
                actions={['search', 'expand']}
                bordered={false}
            />
        );
    }
    if (!rawText) {
        return (
            <div className="py-10 text-center text-xs text-muted-foreground">
                Empty response body
            </div>
        );
    }
    return (
        <PrettyCode
            data={rawText}
            language={detected.prism}
            variant="plain"
            isCompact
        />
    );
}
