import type { LucideIcon as LucideIconType } from 'lucide-react';

/**
 * Maps menu/route `icon` values into `SidebarItem['icon']`.
 * Supports Lucide icon **name** (`"LayoutDashboard"`), a **Lucide component**, or legacy `{ name: string }`.
 */
export function normalizeSidebarNavIcon(icon: unknown): string | LucideIconType | undefined {
  if (icon == null) return undefined;
  if (typeof icon === 'string') return icon;
  if (typeof icon === 'function') return icon as LucideIconType;
  if (typeof icon === 'object' && icon !== null && 'name' in icon) {
    const n = (icon as { name?: unknown }).name;
    if (typeof n === 'string' && n.length > 0) return n;
  }
  return undefined;
}
