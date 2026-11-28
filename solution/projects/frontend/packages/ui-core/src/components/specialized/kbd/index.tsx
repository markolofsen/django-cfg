import { cn } from '../../../lib/utils';

type KbdSize = "xs" | "sm" | "default" | "lg";

interface KbdProps extends React.ComponentProps<"kbd"> {
  size?: KbdSize;
}

const kbdSizeStyles: Record<KbdSize, string> = {
  xs: "h-4 min-w-4 px-0.5 text-[10px] [&_svg:not([class*='size-'])]:size-2.5",
  sm: "h-5 min-w-5 px-1 text-xs [&_svg:not([class*='size-'])]:size-3",
  default: "h-6 min-w-6 px-1.5 text-xs [&_svg:not([class*='size-'])]:size-3.5",
  lg: "h-7 min-w-7 px-2 text-sm [&_svg:not([class*='size-'])]:size-4",
};

function Kbd({ className, size = "default", ...props }: KbdProps) {
  return (
    <kbd
      data-slot="kbd"
      className={cn(
        "bg-muted text-muted-foreground pointer-events-none inline-flex w-fit select-none items-center justify-center gap-1 rounded-sm font-mono font-medium border border-border/50",
        "[[data-slot=tooltip-content]_&]:bg-background/20 [[data-slot=tooltip-content]_&]:text-background dark:[[data-slot=tooltip-content]_&]:bg-background/10",
        kbdSizeStyles[size],
        className
      )}
      {...props}
    />
  )
}

function KbdGroup({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <kbd
      data-slot="kbd-group"
      className={cn("inline-flex items-center gap-1", className)}
      {...props}
    />
  )
}

export { Kbd, KbdGroup }
export type { KbdProps, KbdSize }
