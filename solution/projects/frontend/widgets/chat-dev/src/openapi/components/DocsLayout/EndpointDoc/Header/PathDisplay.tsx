'use client';

import { relativePath } from '../../../shared/ui';

interface PathDisplayProps {
    path: string;
}

/** The endpoint path as the visual focal point of the card. Renders in
 *  large monospace so readers scanning the page land on it first — the
 *  path is what distinguishes one endpoint from another, so it should
 *  be the biggest visible element short of the section title hierarchy.
 *
 *  ``relativePath`` strips the resolved base URL so the docs always
 *  show the API-local path, not an absolute URL cluttered with host
 *  noise. */
export function PathDisplay({ path }: PathDisplayProps) {
    return (
        <code
            className="block font-mono text-lg md:text-xl font-semibold text-foreground leading-tight"
            style={{ overflowWrap: 'anywhere', wordBreak: 'break-word' }}
        >
            {relativePath(path)}
        </code>
    );
}
