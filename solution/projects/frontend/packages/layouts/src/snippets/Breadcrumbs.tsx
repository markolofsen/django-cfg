"use client";
import { ChevronRight, Home } from 'lucide-react';
import { Link } from '@djangocfg/ui-core/components';
import { useLocation } from '@djangocfg/ui-core/hooks';
import React, { useMemo } from 'react';

import { useAppT } from '@djangocfg/i18n';

export interface BreadcrumbItem {
  path: string;
  label: string;
  isActive: boolean;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
  className?: string;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className = "" }) => {
  const { pathname } = useLocation();
  const t = useAppT();

  const labels = useMemo(() => ({
    home: t('layouts.navigation.home'),
    breadcrumb: t('layouts.navigation.breadcrumb'),
  }), [t]);

  // Use provided items or generate from pathname
  const breadcrumbs = useMemo(() => {
    if (items) return items;
    return generateBreadcrumbsFromPath(pathname, labels.home);
  }, [items, pathname, labels.home]);

  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav className={`flex items-center space-x-2 text-sm ${className}`} aria-label={labels.breadcrumb}>
      <ol className="flex items-center space-x-2">
        {breadcrumbs.map((item: BreadcrumbItem, index: number) => (
          <li key={item.path} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="w-4 h-4 text-muted-foreground mx-2" />
            )}

            {item.isActive ? (
              <span className="text-foreground font-medium flex items-center gap-1">
                {index === 0 && <Home className="w-4 h-4" />}
                {item.label}
              </span>
            ) : (
              <Link
                href={item.path}
                className="text-muted-foreground hover:text-foreground
                         transition-colors duration-200 flex items-center gap-1 hover:underline"
              >
                {index === 0 && <Home className="w-4 h-4" />}
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

// Helper function to generate breadcrumbs from pathname
function generateBreadcrumbsFromPath(pathname: string, homeLabel: string = 'Home'): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [
    { path: '/', label: homeLabel, isActive: pathname === '/' }
  ];

  let currentPath = '';
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    breadcrumbs.push({
      path: currentPath,
      label: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
      isActive: index === segments.length - 1
    });
  });

  return breadcrumbs;
}

export default Breadcrumbs;
export { generateBreadcrumbsFromPath };