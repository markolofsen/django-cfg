import { useMemo } from 'react';

import { detectContent } from './detectContent';
import type { DetectedContent } from './types';

interface UseResponseViewResult {
    /** Parsed JSON value when the body is JSON, otherwise ``null``.
     *  JsonTree needs a live object to render properly, so we parse
     *  once up-front and cache. */
    treeData: unknown;
    /** Stringified body, always present when the server returned
     *  anything. Used by Raw and Pretty-for-text tabs. */
    rawText: string;
    /** Content-type + prism language inference. */
    detected: DetectedContent;
}

/** Shape the raw response payload into the pieces each view tab
 *  needs. Exposed as a hook so the component stays thin and the
 *  normalisation is easy to test in isolation. */
export function useResponseView(
    data: unknown,
    headers: unknown,
): UseResponseViewResult {
    return useMemo(() => {
        if (data == null) {
            return {
                treeData: null,
                rawText: '',
                detected: detectContent(headers, ''),
            };
        }

        // String body — might be JSON-in-a-string or a plain text dump.
        if (typeof data === 'string') {
            try {
                return {
                    treeData: JSON.parse(data),
                    rawText: data,
                    detected: detectContent(headers, data),
                };
            } catch {
                return {
                    treeData: null,
                    rawText: data,
                    detected: detectContent(headers, data),
                };
            }
        }

        // Object body — axios already parsed it. Stringify for Raw/
        // Preview tabs and treat it as JSON regardless of headers.
        const stringified = (() => {
            try { return JSON.stringify(data, null, 2); } catch { return String(data); }
        })();
        return {
            treeData: data,
            rawText: stringified,
            detected: detectContent(headers, stringified),
        };
    }, [data, headers]);
}
