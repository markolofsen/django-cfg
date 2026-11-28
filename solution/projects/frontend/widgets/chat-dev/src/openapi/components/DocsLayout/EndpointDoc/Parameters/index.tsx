'use client';

import type { ApiEndpoint } from '../../../../types';
import { ParamGroup } from './ParamGroup';

interface ParametersProps {
    pathParams: NonNullable<ApiEndpoint['parameters']>;
    queryParams: NonNullable<ApiEndpoint['parameters']>;
}

/** Combined path + query parameters block. Each group renders only
 *  when non-empty; when both are empty the parent should not render
 *  the Section at all (we check up-stream so the Section badge shows a
 *  real count). */
export function Parameters({ pathParams, queryParams }: ParametersProps) {
    return (
        <div className="space-y-4">
            <ParamGroup label="Path" params={pathParams} />
            <ParamGroup label="Query" params={queryParams} />
        </div>
    );
}
