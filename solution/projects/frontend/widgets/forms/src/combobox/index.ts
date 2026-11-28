'use client';

/**
 * Combobox
 *
 * Advanced combobox with filtering, multi-select, and custom rendering.
 * Built on ui-core Popover primitives.
 *
 * @example
 * import { Combobox, ComboboxTrigger, ComboboxInput, ComboboxList, ComboboxItem } from '@djangocfg/widget-forms/combobox';
 *
 * <Combobox options={options} onChange={console.log}>
 *   <ComboboxTrigger />
 *   <ComboboxList>
 *     {options.map((opt, i) => (
 *       <ComboboxItem key={opt.value} option={opt} index={i} />
 *     ))}
 *   </ComboboxList>
 * </Combobox>
 */

export {
  Combobox,
  ComboboxTrigger,
  ComboboxInput,
  ComboboxList,
  ComboboxItem,
  ComboboxEmpty,
} from './parts';

export {
  ComboboxProvider,
  useComboboxContext,
} from './context';

export type {
  ComboboxProps,
  ComboboxTriggerProps,
  ComboboxInputProps,
  ComboboxListProps,
  ComboboxItemProps,
  ComboboxEmptyProps,
  ComboboxContextValue,
  ComboboxOption,
} from './types';
