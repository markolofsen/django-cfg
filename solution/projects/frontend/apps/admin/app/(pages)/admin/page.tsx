'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Admin Index Page
 * Redirects to /admin/dashboard (default dashboard page)
 */
export default function AdminIndexPage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/admin/dashboard');
  }, [router]);

  return null;
}
