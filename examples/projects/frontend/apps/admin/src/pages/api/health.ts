/**
 * Health Check Endpoint
 *
 * Used by Docker healthcheck and load balancers
 */

import type { NextApiRequest, NextApiResponse } from 'next';

interface HealthResponse {
  status: 'ok';
  timestamp: string;
  uptime: number;
  version: string;
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthResponse>
) {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  });
}
