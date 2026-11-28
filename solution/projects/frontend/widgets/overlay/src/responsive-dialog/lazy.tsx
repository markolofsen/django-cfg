'use client';

/**
 * Lazy-loaded ResponsiveDialog Component
 *
 * ResponsiveDialog is lightweight but lazy-loaded for consistency
 * with the other widget components.
 *
 * @example
 * import { LazyResponsiveDialog, LazyResponsiveDialogContent } from '@djangocfg/widget-overlay/responsive-dialog';
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  ResponsiveDialogProps,
  ResponsiveDialogContentProps,
  ResponsiveDialogHeaderProps,
  ResponsiveDialogTitleProps,
  ResponsiveDialogDescriptionProps,
  ResponsiveDialogFooterProps,
} from './types';

export type {
  ResponsiveDialogProps,
  ResponsiveDialogContentProps,
  ResponsiveDialogHeaderProps,
  ResponsiveDialogTitleProps,
  ResponsiveDialogDescriptionProps,
  ResponsiveDialogFooterProps,
} from './types';

export const LazyResponsiveDialog = createLazyComponent<
  ResponsiveDialogProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialog })),
  {
    displayName: 'LazyResponsiveDialog',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazyResponsiveDialogContent = createLazyComponent<
  ResponsiveDialogContentProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialogContent })),
  {
    displayName: 'LazyResponsiveDialogContent',
    fallback: null,
  }
);

export const LazyResponsiveDialogHeader = createLazyComponent<
  ResponsiveDialogHeaderProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialogHeader })),
  {
    displayName: 'LazyResponsiveDialogHeader',
    fallback: null,
  }
);

export const LazyResponsiveDialogTitle = createLazyComponent<
  ResponsiveDialogTitleProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialogTitle })),
  {
    displayName: 'LazyResponsiveDialogTitle',
    fallback: null,
  }
);

export const LazyResponsiveDialogDescription = createLazyComponent<
  ResponsiveDialogDescriptionProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialogDescription })),
  {
    displayName: 'LazyResponsiveDialogDescription',
    fallback: null,
  }
);

export const LazyResponsiveDialogFooter = createLazyComponent<
  ResponsiveDialogFooterProps
>(
  () => import('./parts/ResponsiveDialog').then((m) => ({ default: m.ResponsiveDialogFooter })),
  {
    displayName: 'LazyResponsiveDialogFooter',
    fallback: null,
  }
);
