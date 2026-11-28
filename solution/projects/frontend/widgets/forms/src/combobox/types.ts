'use client';

import type * as React from 'react';

export interface ComboboxOption {
  value: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
}

export interface ComboboxContextValue {
  open: boolean;
  search: string;
  value: string | string[] | null;
  multiple: boolean;
  highlightedIndex: number;
  options: ComboboxOption[];
  filteredOptions: ComboboxOption[];
  setOpen: (open: boolean) => void;
  setSearch: (search: string) => void;
  setHighlightedIndex: (index: number | ((prev: number) => number)) => void;
  selectOption: (option: ComboboxOption) => void;
  removeValue: (value: string) => void;
  isSelected: (value: string) => boolean;
}

export interface ComboboxProps {
  children: React.ReactNode;
  /** Available options */
  options: ComboboxOption[];
  /** Controlled value */
  value?: string | string[] | null;
  /** Default value */
  defaultValue?: string | string[] | null;
  /** Allow multiple selection */
  multiple?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Called when value changes */
  onChange?: (value: string | string[] | null) => void;
  /** Custom filter function */
  onFilter?: (options: ComboboxOption[], search: string) => ComboboxOption[];
  /** Disabled state */
  disabled?: boolean;
  className?: string;
}

export interface ComboboxTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode;
}

export type ComboboxInputProps = React.InputHTMLAttributes<HTMLInputElement>;

export interface ComboboxListProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export interface ComboboxItemProps extends React.HTMLAttributes<HTMLDivElement> {
  option: ComboboxOption;
  index: number;
}

export interface ComboboxEmptyProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}
