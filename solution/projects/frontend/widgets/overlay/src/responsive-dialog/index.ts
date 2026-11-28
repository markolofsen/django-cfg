'use client';

/**
 * ResponsiveDialog
 *
 * Dialog on desktop, Drawer on mobile. Automatically switches based on viewport.
 * Wraps ui-core's Dialog and Drawer primitives with a unified API.
 *
 * @example
 * import { ResponsiveDialog, ResponsiveDialogContent, ResponsiveDialogHeader, ResponsiveDialogTitle, ResponsiveDialogDescription, ResponsiveDialogFooter } from '@djangocfg/widget-overlay/responsive-dialog';
 *
 * <ResponsiveDialog open={open} onOpenChange={setOpen}>
 *   <ResponsiveDialogContent>
 *     <ResponsiveDialogHeader>
 *       <ResponsiveDialogTitle>Title</ResponsiveDialogTitle>
 *       <ResponsiveDialogDescription>Description</ResponsiveDialogDescription>
 *     </ResponsiveDialogHeader>
 *     <div>Content</div>
 *     <ResponsiveDialogFooter>
 *       <Button>Close</Button>
 *     </ResponsiveDialogFooter>
 *   </ResponsiveDialogContent>
 * </ResponsiveDialog>
 */

export {
  ResponsiveDialog,
  ResponsiveDialogContent,
  ResponsiveDialogHeader,
  ResponsiveDialogTitle,
  ResponsiveDialogDescription,
  ResponsiveDialogFooter,
} from './parts';

export {
  ResponsiveDialogProvider,
  useResponsiveDialogContext,
} from './context';

export type {
  ResponsiveDialogProps,
  ResponsiveDialogContentProps,
  ResponsiveDialogHeaderProps,
  ResponsiveDialogTitleProps,
  ResponsiveDialogDescriptionProps,
  ResponsiveDialogFooterProps,
  ResponsiveDialogContextValue,
} from './types';
