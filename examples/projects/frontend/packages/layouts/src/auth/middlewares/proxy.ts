import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
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

export const config = {
  matcher: ['/media/:path*', '/api/:path*'],
};
