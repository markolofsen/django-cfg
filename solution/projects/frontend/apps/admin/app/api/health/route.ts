import { NextResponse } from 'next/server';

// Mark as static for static export compatibility
export const dynamic = 'force-static';
export const revalidate = false;

interface HealthResponse {
  status: 'ok';
  timestamp: string;
  uptime: number;
  version: string;
}

export async function GET() {
  const response: HealthResponse = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  };

  return NextResponse.json(response);
}
