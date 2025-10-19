"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

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
  const pathname = usePathname();
  
  // Use provided items or generate from pathname
  const breadcrumbs = items || generateBreadcrumbsFromPath(pathname);

  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <nav className={`flex items-center space-x-2 text-sm ${className}`} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {breadcrumbs.map((item: BreadcrumbItem, index: number) => (
          <li key={item.path} className="flex items-center">
            {index > 0 && (
              <ChevronRight className="w-4 h-4 text-gray-400 mx-2" />
            )}
            
            {item.isActive ? (
              <span className="text-gray-900 dark:text-white font-medium flex items-center gap-1">
                {index === 0 && <Home className="w-4 h-4" />}
                {item.label}
              </span>
            ) : (
              <Link
                href={item.path}
                className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 
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
function generateBreadcrumbsFromPath(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [
    { path: '/', label: 'Home', isActive: pathname === '/' }
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