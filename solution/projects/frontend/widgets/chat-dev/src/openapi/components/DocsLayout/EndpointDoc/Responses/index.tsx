'use client';

import type { ApiEndpoint } from '../../../../types';
import { ResponseRow } from './ResponseRow';

interface ResponsesProps {
    responses: NonNullable<ApiEndpoint['responses']>;
}

/** Flat list of response rows. Outer collapsible wrapper lives in the
 *  ``Section`` component higher up; this component only knows how to
 *  arrange the individual rows. */
export function Responses({ responses }: ResponsesProps) {
    return (
        <div className="divide-y border rounded-md overflow-hidden">
            {responses.map((r) => (
                <ResponseRow key={r.code} response={r} />
            ))}
        </div>
    );
}
