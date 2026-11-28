"use client";

import * as React from "react";

/**
 * React 18 exposed `ref` on the element itself; React 19 moved it into `props`.
 * Neither placement is in `ReactElement`'s public type, so the legacy one is
 * declared here rather than asserted away.
 */
type ElementWithLegacyRef = React.ReactElement & { ref?: React.Ref<unknown> };

/** Get the ref from a React element without throwing warnings. */
function getElementRef(element: ElementWithLegacyRef) {
  if (!React.isValidElement(element)) return undefined;

  // React <=18 in DEV
  let getter = Object.getOwnPropertyDescriptor(element.props, "ref")?.get;
  let mayWarn = getter && "isReactWarning" in getter && getter.isReactWarning;
  if (mayWarn) {
    return element.ref;
  }

  // React 19 in DEV
  getter = Object.getOwnPropertyDescriptor(element, "ref")?.get;
  mayWarn = getter && "isReactWarning" in getter && getter.isReactWarning;
  if (mayWarn) {
    return (element.props as { ref?: React.Ref<unknown> }).ref;
  }

  // Not DEV
  return (
    (element.props as { ref?: React.Ref<unknown> }).ref || element.ref
  );
}

export { getElementRef };
