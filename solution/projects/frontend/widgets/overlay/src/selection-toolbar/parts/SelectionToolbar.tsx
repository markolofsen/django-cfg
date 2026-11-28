'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { SelectionToolbarProvider, useSelectionToolbarContext } from '../context';
import type {
  SelectionToolbarProps,
  SelectionToolbarContentProps,
  SelectionToolbarActionProps,
} from '../types';

export function SelectionToolbar({
  children,
  minSelectionLength = 1,
  onSelectionChange,
}: SelectionToolbarProps) {
  const [isVisible, setIsVisible] = React.useState(false);
  const [selectedText, setSelectedText] = React.useState('');
  const [selectionRect, setSelectionRect] = React.useState<DOMRect | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const hide = React.useCallback(() => {
    setIsVisible(false);
    setSelectedText('');
    setSelectionRect(null);
    window.getSelection()?.removeAllRanges();
  }, []);

  React.useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        setIsVisible(false);
        return;
      }

      const text = selection.toString().trim();
      if (text.length < minSelectionLength) {
        setIsVisible(false);
        return;
      }

      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      // Only show if selection is within our container
      const container = containerRef.current;
      if (container) {
        const containerRect = container.getBoundingClientRect();
        const isInside =
          rect.top >= containerRect.top &&
          rect.bottom <= containerRect.bottom &&
          rect.left >= containerRect.left &&
          rect.right <= containerRect.right;
        if (!isInside) {
          setIsVisible(false);
          return;
        }
      }

      setSelectedText(text);
      setSelectionRect(rect);
      setIsVisible(true);
      onSelectionChange?.(text);
    };

    document.addEventListener('selectionchange', handleSelectionChange);
    return () => document.removeEventListener('selectionchange', handleSelectionChange);
  }, [minSelectionLength, onSelectionChange]);

  // Hide on click outside
  React.useEffect(() => {
    const handlePointerDown = (e: PointerEvent) => {
      const target = e.target as Node;
      const toolbarEl = containerRef.current?.querySelector('[data-slot="selection-toolbar-content"]');
      if (toolbarEl && !toolbarEl.contains(target)) {
        // Don't hide if clicking within the text container (let selectionchange handle it)
        if (!containerRef.current?.contains(target)) {
          hide();
        }
      }
    };
    document.addEventListener('pointerdown', handlePointerDown);
    return () => document.removeEventListener('pointerdown', handlePointerDown);
  }, [hide]);

  const value = React.useMemo(
    () => ({ isVisible, selectedText, selectionRect, hide }),
    [isVisible, selectedText, selectionRect, hide]
  );

  return (
    <SelectionToolbarProvider value={value}>
      <div ref={containerRef} data-slot="selection-toolbar" className="relative">
        {children}
      </div>
    </SelectionToolbarProvider>
  );
}
SelectionToolbar.displayName = 'SelectionToolbar';

export function SelectionToolbarContent({
  children,
  className,
  offset = 8,
}: SelectionToolbarContentProps) {
  const { isVisible, selectionRect } = useSelectionToolbarContext();
  const style = React.useMemo<React.CSSProperties>(() => {
    if (!selectionRect) return { display: 'none' };
    const top = selectionRect.top - offset;
    const left = selectionRect.left + selectionRect.width / 2;
    return {
      position: 'fixed',
      top: `${top}px`,
      left: `${left}px`,
      transform: 'translate(-50%, -100%)',
      zIndex: 700,
      pointerEvents: isVisible ? 'auto' : 'none',
      opacity: isVisible ? 1 : 0,
      transition: 'opacity 150ms ease',
    };
  }, [selectionRect, offset, isVisible]);

  return (
    <div
      data-slot="selection-toolbar-content"
      style={style}
      className={cn(
        'flex items-center gap-1 rounded-lg border border-border bg-background p-1 shadow-lg',
        className
      )}
    >
      {children}
    </div>
  );
}
SelectionToolbarContent.displayName = 'SelectionToolbarContent';

export function SelectionToolbarAction({
  children,
  className,
  label,
  ...props
}: SelectionToolbarActionProps) {
  return (
    <button
      type="button"
      data-slot="selection-toolbar-action"
      className={cn(
        'inline-flex items-center justify-center rounded-md px-2.5 py-1.5',
        'text-xs font-medium text-foreground hover:bg-muted transition-colors',
        'disabled:opacity-50 disabled:pointer-events-none',
        className
      )}
      {...props}
    >
      {children}
      {label && <span className="ml-1">{label}</span>}
    </button>
  );
}
SelectionToolbarAction.displayName = 'SelectionToolbarAction';
