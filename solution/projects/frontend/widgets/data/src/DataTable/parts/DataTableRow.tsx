'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { TableRow, TableCell } from '@djangocfg/ui-core/components';

import { useDataTableContext } from '../context/DataTableContext';

interface DataTableRowProps<T> {
  row: T;
  index: number;
}

export function DataTableRow<T>({ row, index }: DataTableRowProps<T>) {
  const {
    columns,
    getRowId,
    selectionMode,
    select,
    isSelected,
    getRowClassName,
    onRowClick,
    onRowDoubleClick,
  } = useDataTableContext<T>();

  const id = getRowId(row);
  const selected = isSelected(id);

  const handleClick = React.useCallback(() => {
    if (selectionMode !== 'none') {
      select(id);
    }
    onRowClick?.(row);
  }, [id, selectionMode, select, onRowClick, row]);

  const handleDoubleClick = React.useCallback(() => {
    onRowDoubleClick?.(row);
  }, [onRowDoubleClick, row]);

  return (
    <TableRow
      data-slot="data-table-row"
      data-id={String(id)}
      data-selected={selected ? '' : undefined}
      data-state={selected ? 'selected' : undefined}
      className={cn(getRowClassName?.(row, index))}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
    >
      {selectionMode === 'multiple' && (
        <TableCell>
          <input
            type="checkbox"
            checked={selected}
            onChange={() => select(id)}
            className="h-4 w-4 rounded border-border accent-primary"
            aria-label={`Select row ${String(id)}`}
            onClick={(e) => e.stopPropagation()}
          />
        </TableCell>
      )}
      {selectionMode === 'single' && (
        <TableCell>
          <input
            type="radio"
            checked={selected}
            onChange={() => select(id)}
            className="h-4 w-4 border-border accent-primary"
            aria-label={`Select row ${String(id)}`}
            onClick={(e) => e.stopPropagation()}
          />
        </TableCell>
      )}
      {columns.map((col) => (
        <DataTableCell key={col.key} column={col} row={row} />
      ))}
    </TableRow>
  );
}
DataTableRow.displayName = 'DataTableRow';

function DataTableCell<T>({ column, row }: { column: { key: string; cell?: (row: T) => React.ReactNode; align?: 'left' | 'center' | 'right' }; row: T }) {
  const value = (row as Record<string, unknown>)[column.key];
  const content = column.cell ? column.cell(row) : value != null ? String(value) : null;

  return (
    <TableCell
      className={cn(
        column.align === 'center' && 'text-center',
        column.align === 'right' && 'text-right'
      )}
    >
      {content}
    </TableCell>
  );
}
