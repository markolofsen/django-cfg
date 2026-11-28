'use client';

/**
 * SelectionToolbar
 *
 * Toolbar that appears when text is selected within its container.
 * Useful for text formatting, sharing, or quick actions on selection.
 *
 * @example
 * import { SelectionToolbar, SelectionToolbarContent, SelectionToolbarAction } from '@djangocfg/widget-overlay/selection-toolbar';
 *
 * <SelectionToolbar>
 *   <div>Some selectable text...</div>
 *   <SelectionToolbarContent>
 *     <SelectionToolbarAction onClick={handleCopy}>Copy</SelectionToolbarAction>
 *     <SelectionToolbarAction onClick={handleShare}>Share</SelectionToolbarAction>
 *   </SelectionToolbarContent>
 * </SelectionToolbar>
 */

export {
  SelectionToolbar,
  SelectionToolbarContent,
  SelectionToolbarAction,
} from './parts';

export {
  SelectionToolbarProvider,
  useSelectionToolbarContext,
} from './context';

export type {
  SelectionToolbarProps,
  SelectionToolbarContentProps,
  SelectionToolbarActionProps,
  SelectionToolbarContextValue,
} from './types';
