'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { useDataGridContext } from '../context/DataGridContext';
import { DataGridCell } from './DataGridCell';

interface DataGridRowProps<T> {
  row: T;
  index: number;
}

export function DataGridRow<T>({ row, index }: DataGridRowProps<T>) {
  const {
    columns,
    getRowId,
    selectionMode,
    select,
    isSelected,
    getRowClassName,
    onRowClick,
    onRowDoubleClick,
  } = useDataGridContext<T>();

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
    <tr
      data-slot="data-grid-row"
      data-id={String(id)}
      data-selected={selected ? '' : undefined}
      data-state={selected ? 'selected' : undefined}
      className={cn(
        'border-b transition-colors hover:bg-muted/50',
        selected && 'bg-muted',
        getRowClassName?.(row, index)
      )}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
    >
      {selectionMode === 'multiple' && (
        <td className="p-2 align-middle">
          <input
            type="checkbox"
            checked={selected}
            onChange={() => select(id)}
            className="h-4 w-4 rounded border-border accent-primary"
            aria-label={`Select row ${String(id)}`}
            onClick={(e) => e.stopPropagation()}
          />
        </td>
      )}
      {selectionMode === 'single' && (
        <td className="p-2 align-middle">
          <input
            type="radio"
            checked={selected}
            onChange={() => select(id)}
            className="h-4 w-4 border-border accent-primary"
            aria-label={`Select row ${String(id)}`}
            onClick={(e) => e.stopPropagation()}
          />
        </td>
      )}
      {columns.map((col) => (
        <DataGridCell key={col.key} column={col} row={row} />
      ))}
    </tr>
  );
}
DataGridRow.displayName = 'DataGridRow';
