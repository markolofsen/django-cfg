"use client";

export {
  ListboxRoot as Listbox,
  ListboxRoot,
} from "./context/ListboxProvider";
export {
  ListboxGroup,
  ListboxGroupLabel,
} from "./parts/ListboxGroup";
export {
  ListboxItem,
  ListboxItemIndicator,
} from "./parts/ListboxItem";
export type {
  ListboxRootProps as ListboxProps,
  ListboxRootProps,
  ListboxGroupProps,
  ListboxGroupLabelProps,
  ListboxItemProps,
  ListboxItemIndicatorProps,
  ListboxValue,
} from "./types";

// The dynamic-import wrapper. Exported here because the subpath resolves to
// this barrel: in the retired ui-tools `lazy.tsx` was reachable from no declared export,
// so `LazyListbox` was dead code for every tool but `JsonTree`.
export { LazyListbox } from './lazy';
