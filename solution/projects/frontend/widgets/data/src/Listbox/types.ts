"use client";

import * as React from "react";

export type ListboxValue<Multiple extends boolean = false> = Multiple extends true
  ? string[]
  : string;

export interface ListboxState {
  selectedValues: Set<string>;
  focusedValue: string | null;
  highlightedValue: string | null;
}

export type StoreListener = () => void;
export type StoreStateSelector<T> = (state: ListboxState) => T;

export interface ListboxStore {
  onSubscribe: (callback: StoreListener) => () => void;
  getSnapshot: () => ListboxState;
  onStateChange: <K extends keyof ListboxState>(
    key: K,
    value: ListboxState[K],
    silent?: boolean,
  ) => void;
  onEmit: () => void;
  onSelectedStateChange: (value: string, multiple?: boolean) => void;
  onClearSelection: () => void;
  onHighlightedValueChange: (value: string | null) => void;
}

export interface ItemData {
  value: string;
  disabled?: boolean;
  onSelect?: (value: string) => void;
}

export type ItemElement = HTMLDivElement;

export interface CollectionItem extends ItemData {
  ref: React.RefObject<ItemElement | null>;
}

export type CollectionItemMap = Map<
  React.RefObject<ItemElement | null>,
  CollectionItem
>;

export type CollectionGroupMap = Map<string, Set<React.RefObject<ItemElement | null>>>;

export interface ListboxContextValue<Multiple extends boolean = false> {
  store: ListboxStore;
  onItemRegister: (item: CollectionItem, groupId?: string) => () => void;
  onItemSelect: (value: string, isMultipleEvent?: boolean) => void;
  onItemFocus: (value: string) => void;
  onItemBlur: () => void;
  onItemHighlight: (value: string | null) => void;
  dir: "ltr" | "rtl";
  disabled: boolean;
  multiple: Multiple;
}

export interface ListboxRootProps<Multiple extends boolean = false>
  extends React.ComponentPropsWithoutRef<"div"> {
  defaultValue?: ListboxValue<Multiple>;
  value?: ListboxValue<Multiple>;
  onValueChange?: (value: ListboxValue<Multiple>) => void;
  dir?: "ltr" | "rtl";
  asChild?: boolean;
  disabled?: boolean;
  loop?: boolean;
  multiple?: Multiple;
  virtual?: boolean;
  orientation?: "horizontal" | "vertical" | "mixed";
  name?: string;
}

export interface ListboxGroupProps extends React.ComponentPropsWithoutRef<"div"> {
  asChild?: boolean;
}

export interface ListboxGroupLabelProps extends React.ComponentPropsWithoutRef<"div"> {
  asChild?: boolean;
}

export interface ListboxItemProps
  extends Omit<React.ComponentPropsWithoutRef<"div">, "onSelect"> {
  value: string;
  disabled?: boolean;
  asChild?: boolean;
  onSelect?: (value: string) => void;
}

export interface ListboxItemIndicatorProps
  extends React.ComponentPropsWithoutRef<"span"> {
  forceMount?: boolean;
  asChild?: boolean;
}
