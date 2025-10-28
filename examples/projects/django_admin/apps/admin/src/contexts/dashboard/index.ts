/**
 * Dashboard Contexts
 *
 * Re-exports all dashboard contexts organized by domain
 */

// Overview Context
export {
  DashboardOverviewProvider,
  useDashboardOverviewContext,
} from './DashboardOverviewContext';

export type {
  DashboardOverviewContextValue,
  DashboardOverview,
} from './DashboardOverviewContext';

// Statistics Context
export {
  DashboardStatisticsProvider,
  useDashboardStatisticsContext,
} from './DashboardStatisticsContext';

export type {
  DashboardStatisticsContextValue,
  StatCard,
  UserStatistics,
  AppStatistics,
} from './DashboardStatisticsContext';

// System Context
export {
  DashboardSystemProvider,
  useDashboardSystemContext,
} from './DashboardSystemContext';

export type {
  DashboardSystemContextValue,
  SystemHealth,
  SystemMetrics,
} from './DashboardSystemContext';

// Activity Context
export {
  DashboardActivityProvider,
  useDashboardActivityContext,
} from './DashboardActivityContext';

export type {
  DashboardActivityContextValue,
  ActivityEntry,
  QuickAction,
} from './DashboardActivityContext';

// Charts Context
export {
  DashboardChartsProvider,
  useDashboardChartsContext,
} from './DashboardChartsContext';

export type {
  DashboardChartsContextValue,
  ChartData,
  RecentUser,
  ActivityTrackerDay,
} from './DashboardChartsContext';

// Commands Context
export {
  DashboardCommandsProvider,
  useDashboardCommandsContext,
} from './DashboardCommandsContext';

export type {
  DashboardCommandsContextValue,
  CommandsSummary,
  Command,
  CommandExecutionEvent,
  CommandExecutionCallback,
} from './DashboardCommandsContext';

// API Zones Context
export {
  DashboardZonesProvider,
  useDashboardZonesContext,
} from './DashboardZonesContext';

export type {
  DashboardZonesContextValue,
  APIZonesSummary,
  APIZone,
} from './DashboardZonesContext';
