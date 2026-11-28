'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import type { DataGridColumn } from '../types';

interface DataGridCellProps<T> {
  column: DataGridColumn<T>;
  row: T;
}

export function DataGridCell<T>({ column, row }: DataGridCellProps<T>) {
  const value = (row as Record<string, unknown>)[column.key];

  const content = column.cell ? column.cell(row) : value != null ? String(value) : null;

  return (
    <td
      className={cn(
        'p-2 align-middle',
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right'
      )}
    >
      {content}
    </td>
  );
}
DataGridCell.displayName = 'DataGridCell';
