"use client";

export interface MasonryProps extends React.ComponentProps<"div"> {
  columnWidth?: number;
  columnCount?: number;
  maxColumnCount?: number;
  gap?: number | { column: number; row: number };
  itemHeight?: number;
  defaultWidth?: number;
  defaultHeight?: number;
  overscan?: number;
  scrollFps?: number;
  fallback?: React.ReactNode;
  linear?: boolean;
  asChild?: boolean;
}

export interface MasonryItemProps extends React.ComponentProps<"div"> {
  asChild?: boolean;
}

export interface Positioner {
  columnCount: number;
  columnWidth: number;
  set: (index: number, height: number) => void;
  get: (index: number) => PositionerItem | undefined;
  update: (updates: number[]) => void;
  range: (
    low: number,
    high: number,
    onItemRender: (index: number, left: number, top: number) => void,
  ) => void;
  size: () => number;
  estimateHeight: (itemCount: number, defaultItemHeight: number) => number;
  shortestColumn: () => number;
  all: () => PositionerItem[];
}

export interface PositionerItem {
  top: number;
  left: number;
  height: number;
  columnIndex: number;
}
