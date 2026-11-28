"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@djangocfg/ui-core/lib";
import type { ListboxGroupProps, ListboxGroupLabelProps } from "../types";

const GROUP_NAME = "ListboxGroup";
const GROUP_LABEL_NAME = "ListboxGroupLabel";

interface ListboxGroupContextValue {
  id: string;
  labelId: string;
}

const ListboxGroupContext = React.createContext<ListboxGroupContextValue | null>(null);
ListboxGroupContext.displayName = GROUP_NAME;

function useListboxGroupContext(name: string) {
  const context = React.useContext(ListboxGroupContext);
  if (!context) {
    throw new Error(`\`${name}\` must be used within \`${GROUP_NAME}\``);
  }
  return context;
}

const ListboxGroup = React.forwardRef<HTMLDivElement, ListboxGroupProps>(
  (props, forwardedRef) => {
    const { asChild, className, ...groupProps } = props;
    const id = React.useId();
    const labelId = React.useId();

    const groupContextValue = React.useMemo(() => ({ id, labelId }), [id, labelId]);
    const GroupPrimitive = asChild ? Slot : "div";

    return (
      <ListboxGroupContext.Provider value={groupContextValue}>
        <GroupPrimitive
          role="group"
          id={id}
          aria-labelledby={labelId}
          className={cn("", className)}
          {...groupProps}
          ref={forwardedRef}
        />
      </ListboxGroupContext.Provider>
    );
  },
);
ListboxGroup.displayName = GROUP_NAME;

const ListboxGroupLabel = React.forwardRef<HTMLDivElement, ListboxGroupLabelProps>(
  (props, forwardedRef) => {
    const { asChild, className, ...labelProps } = props;
    const groupContext = useListboxGroupContext(GROUP_LABEL_NAME);
    const LabelPrimitive = asChild ? Slot : "div";

    return (
      <LabelPrimitive
        id={groupContext.labelId}
        className={cn("px-2 py-1.5 text-sm font-semibold text-muted-foreground", className)}
        {...labelProps}
        ref={forwardedRef}
      />
    );
  },
);
ListboxGroupLabel.displayName = GROUP_LABEL_NAME;

export { ListboxGroup, ListboxGroupLabel, useListboxGroupContext, ListboxGroupContext };
