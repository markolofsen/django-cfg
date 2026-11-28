"use client";

import * as React from "react";
import { visuallyHidden } from "../../../lib/styles";

const VisuallyHidden = React.forwardRef<
  HTMLSpanElement,
  React.ComponentPropsWithoutRef<"span">
>((props, ref) => (
  <span
    ref={ref}
    style={visuallyHidden}
    {...props}
  />
));

VisuallyHidden.displayName = "VisuallyHidden";

export { VisuallyHidden };
