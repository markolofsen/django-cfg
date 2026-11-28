"use client";

// Constrained to values that actually carry `defaultPrevented` — both DOM
// events and React synthetic events qualify. Without it the guard below reads a
// property the type never promised.
function composeEventHandlers<E extends { defaultPrevented: boolean }>(
  originalEventHandler?: (event: E) => void,
  ourEventHandler?: (event: E) => void,
  { checkForDefaultPrevented = true } = {},
) {
  return function handleEvent(event: E) {
    originalEventHandler?.(event);

    if (checkForDefaultPrevented && event.defaultPrevented) {
      return;
    }

    ourEventHandler?.(event);
  };
}

export { composeEventHandlers };
