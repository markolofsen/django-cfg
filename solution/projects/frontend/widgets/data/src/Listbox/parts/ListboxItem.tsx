"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { useComposedRefs } from "@djangocfg/ui-core/lib";
import { composeEventHandlers } from "@djangocfg/ui-core/lib";
import { cn } from "@djangocfg/ui-core/lib";
import { useListboxContext, useListboxState } from "../context/ListboxProvider";
import { ListboxGroupContext } from "./ListboxGroup";
import type { ListboxItemProps, ListboxItemIndicatorProps } from "../types";

const ITEM_NAME = "ListboxItem";
const ITEM_INDICATOR_NAME = "ListboxItemIndicator";

const ListboxItemContext = React.createContext<{ isSelected: boolean } | null>(null);
ListboxItemContext.displayName = ITEM_NAME;

function useListboxItemContext(name: string) {
  const context = React.useContext(ListboxItemContext);
  if (!context) {
    throw new Error(`\`${name}\` must be used within \`${ITEM_NAME}\``);
  }
  return context;
}

const useIsomorphicLayoutEffect = typeof window !== "undefined" ? React.useLayoutEffect : React.useEffect;

const ListboxItem = React.forwardRef<HTMLDivElement, ListboxItemProps>(
  (props, forwardedRef) => {
    const { asChild, value, disabled = false, onSelect, className, ...itemProps } = props;
    const context = useListboxContext(ITEM_NAME);
    const groupContext = React.useContext(ListboxGroupContext);
    const itemRef = React.useRef<HTMLDivElement>(null);
    const composedRef = useComposedRefs(itemRef, forwardedRef);

    const isSelected = useListboxState((state) => state.selectedValues.has(value));
    const isHighlighted = useListboxState((state) => state.highlightedValue === value);
    const isDisabled = disabled || context.disabled;

    useIsomorphicLayoutEffect(() => {
      if (value === "") {
        throw new Error(`${ITEM_NAME} value cannot be an empty string`);
      }
      return context.onItemRegister(
        { ref: itemRef, value, disabled: isDisabled, onSelect },
        groupContext?.id,
      );
    }, [value, isDisabled, context.onItemRegister, groupContext?.id, onSelect]);

    // The handlers below depend on individual context MEMBERS, not on
    // `context`. Every one is a `useCallback` in ListboxProvider and the
    // context is a `useMemo` over exactly them, so a member is stable whenever
    // it matters. Depending on the whole object instead would rebuild all six
    // handlers — and re-register the item — whenever any unrelated context
    // field moved. The linter cannot see through the member access, hence the
    // per-hook disables.
    const onBlur = React.useCallback(() => {
      context.onItemBlur();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [context.onItemBlur]);

    const onClick = React.useCallback(
      (event: React.MouseEvent) => {
        if (!isDisabled) {
          const isMultipleSelectionKey =
            context.multiple && (context.multiple === true || event.ctrlKey || event.metaKey);
          context.onItemSelect(value, isMultipleSelectionKey);
        }
      },
      // eslint-disable-next-line react-hooks/exhaustive-deps
      [context.onItemSelect, value, isDisabled, context.multiple],
    );

    const onFocus = React.useCallback(() => {
      if (!isDisabled) {
        context.onItemFocus(value);
        context.onItemHighlight(value);
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [context.onItemFocus, context.onItemHighlight, isDisabled, value]);

    const onKeyDown = React.useCallback(
      (event: React.KeyboardEvent) => {
        if (event.key === "Tab") {
          if (!event.shiftKey) {
            context.onItemBlur();
          }
          return;
        }
      },
      // eslint-disable-next-line react-hooks/exhaustive-deps
      [context.onItemBlur],
    );

    const onPointerLeave = React.useCallback(() => {
      context.onItemHighlight(null);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [context.onItemHighlight]);

    const onPointerMove = React.useCallback(() => {
      if (!isDisabled) {
        context.onItemHighlight(value);
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [context.onItemHighlight, isDisabled, value]);

    const ItemPrimitive = asChild ? Slot : "div";

    const itemContextValue = React.useMemo(() => ({ isSelected }), [isSelected]);

    return (
      <ListboxItemContext.Provider value={itemContextValue}>
        <ItemPrimitive
          role="option"
          aria-selected={isSelected}
          data-selected={isSelected ? "" : undefined}
          data-highlighted={isHighlighted ? "" : undefined}
          data-disabled={isDisabled ? "" : undefined}
          tabIndex={isDisabled ? undefined : -1}
          className={cn(
            "relative flex cursor-pointer items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
            "hover:bg-accent hover:text-accent-foreground",
            "focus:bg-accent focus:text-accent-foreground",
            isSelected && "bg-accent text-accent-foreground",
            isDisabled && "pointer-events-none opacity-50",
            className,
          )}
          {...itemProps}
          ref={composedRef}
          onClick={composeEventHandlers(itemProps.onClick, onClick)}
          onFocus={composeEventHandlers(itemProps.onFocus, onFocus)}
          onBlur={composeEventHandlers(itemProps.onBlur, onBlur)}
          onKeyDown={composeEventHandlers(itemProps.onKeyDown, onKeyDown)}
          onPointerLeave={composeEventHandlers(itemProps.onPointerLeave, onPointerLeave)}
          onPointerMove={composeEventHandlers(itemProps.onPointerMove, onPointerMove)}
        />
      </ListboxItemContext.Provider>
    );
  },
);
ListboxItem.displayName = ITEM_NAME;

const ListboxItemIndicator = React.forwardRef<HTMLSpanElement, ListboxItemIndicatorProps>(
  (props, forwardedRef) => {
    const { forceMount = false, asChild, className, ...indicatorProps } = props;
    const itemContext = useListboxItemContext(ITEM_INDICATOR_NAME);

    if (!forceMount && !itemContext.isSelected) return null;

    const IndicatorPrimitive = asChild ? Slot : "span";

    return (
      <IndicatorPrimitive
        aria-hidden="true"
        className={cn("mr-2 inline-flex size-4 items-center justify-center", className)}
        {...indicatorProps}
        ref={forwardedRef}
      />
    );
  },
);
ListboxItemIndicator.displayName = ITEM_INDICATOR_NAME;

export { ListboxItem, ListboxItemIndicator, useListboxItemContext, ListboxItemContext };
