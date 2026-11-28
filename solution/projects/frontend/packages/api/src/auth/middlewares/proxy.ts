import { NextRequest, NextResponse } from 'next/server';

/**
 * Proxy middleware for media and API endpoints
 * Use this in your middleware.ts file
 */
export function proxyMiddleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  // Proxy /media/* - Images and static files
  if (pathname.startsWith('/media/')) {
    const targetUrl = `${apiUrl}${pathname}${search}`;
    return NextResponse.rewrite(targetUrl, { request: { headers: request.headers } });
  }

  // Proxy /api/* - API endpoints
  if (pathname.startsWith('/api/')) {
    const targetUrl = `${apiUrl}${pathname}${search}`;
    return NextResponse.rewrite(targetUrl, { request: { headers: request.headers } });
  }

  return NextResponse.next();
}

/**
 * Recommended matcher config for proxy middleware
 * Add this to your middleware.ts config
 */
export const proxyMiddlewareConfig = {
  matcher: ['/media/:path*', '/api/:path*'],
};
