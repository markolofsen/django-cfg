/**
 * Small data visualisations: five charts and three indicators.
 *
 * One package because they share a shape rather than a library — each is a few
 * hundred lines of SVG or canvas over `@djangocfg/ui-core`'s palette, and none
 * carries a charting dependency the others would pay for. Splitting them would
 * be eight packages with one file of value each.
 *
 * Every surface also ships a `Lazy*` wrapper; reach for a subpath in an app
 * that wants one chart.
 */
export * from './charts/ActivityGraph';
export * from './charts/CommitGraph';
export * from './charts/Gauge';
export * from './charts/SmoothLine';
export * from './charts/Sparkline';
export * from './indicators/Fps';
export * from './indicators/Rating';
export * from './indicators/StatusIndicator';
