/**
 * Private Layout exports
 */

export { PrivateLayout } from './PrivateLayout';
export { PrivateLayoutProvider, usePrivateLayoutContext } from './context';
export { LAYOUT_BAR_HEIGHT } from './geometry';
export { mcpSidebarItem, mcpSidebarGroup } from './mcpSidebar';
export type { McpSidebarItemOptions, McpSidebarGroupOptions } from './mcpSidebar';
export { SidebarBrandSwitcher, ForbiddenState } from './components';
export type { ForbiddenStateProps } from './components';
export type {
  PrivateLayoutProps,
  SidebarItem,
  SidebarLinkItem,
  SidebarSettingsItem,
  SidebarGroupConfig,
  SidebarViewConfig,
  SidebarConfig,
  HeaderConfig,
  SidebarActiveIndicator,
  SidebarGroupLabelStyle,
  SidebarFeaturedConfig,
  SidebarBrandSwitcherConfig,
  SidebarBrandSwitcherItem,
  PrivateTopBarConfig,
} from './types';
