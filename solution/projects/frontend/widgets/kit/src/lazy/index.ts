/**
 * Placeholders for dynamically imported components, and the factory that
 * attaches one to a `React.lazy` boundary.
 *
 * Separate from the root barrel because this half is React and the root half
 * is pure: a consumer importing a formatter must not pull React and `ui-core`
 * in behind it.
 */
export {
  LazyWrapper,
  LoadingFallback,
  InlineLoadingFallback,
  CardLoadingFallback,
  MapLoadingFallback,
  Spinner,
  createLazyComponent,
} from './lazy-wrapper';
export type {
  LazyWrapperProps,
  LoadingFallbackProps,
  CreateLazyComponentOptions,
} from './lazy-wrapper';
export { configureLazyCopy, DEFAULT_LAZY_COPY } from './copy';
export type { LazyCopy } from './copy';
