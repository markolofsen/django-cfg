"use client";

export type TimelineDirection = "ltr" | "rtl";
export type TimelineOrientation = "vertical" | "horizontal";
export type TimelineVariant = "default" | "alternate";
export type TimelineStatus = "completed" | "active" | "pending";

export interface DivProps extends React.ComponentProps<"div"> {
  asChild?: boolean;
}

export interface TimelineProps extends DivProps {
  dir?: TimelineDirection;
  orientation?: TimelineOrientation;
  variant?: TimelineVariant;
  activeIndex?: number;
}

export interface TimelineConnectorProps extends DivProps {
  forceMount?: boolean;
}

export interface TimelineTimeProps extends React.ComponentProps<"time"> {
  asChild?: boolean;
}
