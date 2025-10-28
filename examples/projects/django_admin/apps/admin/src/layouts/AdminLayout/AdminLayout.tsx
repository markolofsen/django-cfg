/**
 * AdminLayout Component
 *
 * Main layout for admin pages
 * Features:
 * - Compact horizontal navigation
 * - Sticky header
 * - Responsive container
 * - Optimized for Django iframe embedding
 *
 * Usage:
 * ```tsx
 * import { AdminLayout } from '@/layouts/AdminLayout';
 *
 * export default function AdminPage() {
 *   return (
 *     <AdminLayout>
 *       <YourContent />
 *     </AdminLayout>
 *   );
 * }
 * ```
 */

import type { ReactNode } from 'react';
import { AdminNav } from './AdminNav';

interface AdminLayoutProps {
  /**
   * Page content to display
   */
  children: ReactNode;

  /**
   * Optional additional className for the main content area
   */
  className?: string;

  /**
   * Maximum width of the content container
   * @default '7xl'
   */
  maxWidth?: 'full' | '7xl' | '6xl' | '5xl' | '4xl';
}

const maxWidthClasses = {
  full: 'max-w-full',
  '7xl': 'max-w-7xl',
  '6xl': 'max-w-6xl',
  '5xl': 'max-w-5xl',
  '4xl': 'max-w-4xl',
} as const;

export function AdminLayout({
  children,
  className,
  maxWidth = '7xl',
}: AdminLayoutProps) {
  return (
    <div className="relative flex flex-col">
      {/* Navigation */}
      <AdminNav />

      {/* Main Content */}
      <main
        className="flex-1"
        id="main-content"
        role="main"
      >
        <div
          className={`container ${maxWidthClasses[maxWidth]}`}
        >
          <div className={className}>{children}</div>
        </div>
      </main>
    </div>
  );
}
