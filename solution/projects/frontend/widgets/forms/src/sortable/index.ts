'use client';

/**
 * Sortable
 *
 * Sortable list with drag handles. Supports vertical and horizontal layouts.
 * Uses pointer events for broad device compatibility.
 *
 * @example
 * import { Sortable, SortableItem, SortableHandle } from '@djangocfg/widget-forms/sortable';
 *
 * <Sortable items={items} onReorder={setItems}>
 *   {items.map((item) => (
 *     <SortableItem key={item.id} id={item.id}>
 *       <SortableHandle />
 *       <span>{item.label}</span>
 *     </SortableItem>
 *   ))}
 * </Sortable>
 */

export {
  Sortable,
  SortableItem,
  SortableHandle,
} from './parts';

export {
  SortableProvider,
  useSortableContext,
} from './context';

export type {
  SortableProps,
  SortableItemProps,
  SortableHandleProps,
  SortableContextValue,
  SortableItemData,
  SortableAxis,
} from './types';
