"use client"

import { Menu } from 'lucide-react';
import * as React from 'react';

import * as TabsPrimitive from '@radix-ui/react-tabs';

import { useIsMobile } from '../../../hooks';
import { useStoredValue, type StorageType } from '../../../hooks';
import { useAppT } from '@djangocfg/i18n';
import { useComposedRefs } from '../../../lib/compose-refs';
import { cn } from '../../../lib/utils';
import { useTabIndicator } from './use-tab-indicator';
import { Button } from '../../forms/button';
import { ScrollArea, ScrollBar } from '../../layout/scroll-area';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '../../overlay/sheet';

// ─────────────────────────────────────────────────────────────────────────
// Tabs Root with Mobile Sheet Support
// ─────────────────────────────────────────────────────────────────────────

export interface TabsProps extends React.ComponentPropsWithoutRef<typeof TabsPrimitive.Root> {
  /**
   * Enable mobile sheet mode (automatically shows Sheet on mobile devices)
   * @default false
   */
  mobileSheet?: boolean
  /**
   * Title for mobile sheet header
   * @default "Navigation"
   */
  mobileSheetTitle?: string
  /**
   * Title to display next to burger menu on mobile
   */
  mobileTitleText?: string
  /**
   * Enable sticky positioning (stays at top on scroll)
   * @default false
   */
  sticky?: boolean
  /**
   * When provided, the active tab value is persisted under this key.
   * On mount the last active tab is restored automatically.
   * Works with both controlled (`value`) and uncontrolled (`defaultValue`) modes.
   * In controlled mode the stored value is passed to `defaultValue` on first
   * render; the parent stays in charge after that.
   * @example storageKey="admin-tab"
   */
  storageKey?: string
  /** @default 'local' */
  storageType?: StorageType
}

/**
 * The part of a trigger's props the mobile sheet re-writes when it clones one.
 *
 * Not the trigger's full prop type: everything else passes through untouched,
 * and naming more than is read would be a claim this file cannot check.
 */
type TriggerProps = {
  onClick?: (event: React.MouseEvent) => void
  className?: string
}

const Tabs = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Root>,
  TabsProps
>(({ mobileSheet = false, mobileSheetTitle, mobileTitleText, sticky = false, storageKey, storageType, children, ...props }, ref) => {
  const t = useAppT()
  const resolvedMobileSheetTitle = mobileSheetTitle ?? t('ui.navigation.title')
  const isMobile = useIsMobile()
  const [open, setOpen] = React.useState(false)

  const [storedTab, setStoredTab] = useStoredValue<string>(
    storageKey,
    // seed: prefer defaultValue prop, then controlled value, then empty
    (props.defaultValue as string | undefined) ?? (props.value as string | undefined) ?? '',
    storageKey ? { storage: storageType ?? 'local' } : undefined,
  );

  // Wrap onValueChange to persist tab changes
  const { onValueChange } = props;
  const handleValueChange = React.useCallback(
    (newValue: string) => {
      if (storageKey) setStoredTab(newValue);
      onValueChange?.(newValue);
    },
    [storageKey, setStoredTab, onValueChange],
  );

  // Build enhanced props: inject stored defaultValue when no value/defaultValue given
  const tabsProps = {
    ...props,
    onValueChange: storageKey ? handleValueChange : props.onValueChange,
    // Only inject defaultValue when: storageKey set, no controlled value, storedTab non-empty
    ...(storageKey && props.value === undefined && storedTab
      ? { defaultValue: storedTab }
      : {}),
  };

  // If mobile sheet mode is disabled, render normal tabs
  if (!mobileSheet || !isMobile) {
    // If sticky is enabled for desktop, wrap TabsList in sticky container
    if (sticky) {
      const childrenArray = React.Children.toArray(children)
      const tabsList = childrenArray.find(
        (child) => React.isValidElement(child) && child.type === TabsList
      )
      const tabsContent = childrenArray.filter(
        (child) => React.isValidElement(child) && child.type === TabsContent
      )

      return (
        <TabsPrimitive.Root ref={ref} {...tabsProps}>
          <div className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mb-4">
            {tabsList}
          </div>
          {tabsContent}
        </TabsPrimitive.Root>
      )
    }

    return (
      <TabsPrimitive.Root ref={ref} {...tabsProps}>
        {children}
      </TabsPrimitive.Root>
    )
  }

  // Extract TabsList and TabsContent from children
  const childrenArray = React.Children.toArray(children)
  const tabsList = childrenArray.find(
    (child) => React.isValidElement(child) && child.type === TabsList
  )
  const tabsContent = childrenArray.filter(
    (child) => React.isValidElement(child) && child.type === TabsContent
  )

  // Extract triggers from TabsList children.
  //
  // `isValidElement` narrows to `ReactElement<unknown>` unless it is told the
  // prop shape, which is why reading `.props.children` used to need a cast.
  // Naming the shape is the same assertion, made once and checked: this branch
  // only runs for an element whose `type === TabsList`.
  const triggers = React.isValidElement<{ children?: React.ReactNode }>(tabsList)
    ? React.Children.toArray(tabsList.props.children)
    : []

  // Mobile Sheet Navigation
  return (
    <TabsPrimitive.Root ref={ref} {...tabsProps}>
      <div className={cn(
        "w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mb-4",
        sticky && "sticky top-0 z-40"
      )}>
        <div className="container mx-auto flex items-center justify-between h-14 px-4">
          {/* Title */}
          {mobileTitleText && (
            <h1 className="text-lg font-semibold">{mobileTitleText}</h1>
          )}

          {/* Menu Button */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className={mobileTitleText ? "" : "ml-auto"}>
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[280px] sm:w-[350px]">
              <SheetHeader>
                <SheetTitle>{resolvedMobileSheetTitle}</SheetTitle>
              </SheetHeader>
              <nav className="flex flex-col gap-2 mt-6">
                <TabsPrimitive.List className="flex flex-col gap-2">
                  {triggers.map((trigger, index) => {
                    // Typed here rather than cast at each use: the two props
                    // this clone actually touches are the two it declares, so
                    // `cloneElement` checks the override instead of taking it
                    // on faith.
                    if (!React.isValidElement<TriggerProps>(trigger)) return null

                    // Clone trigger and wrap in mobile-friendly container
                    const triggerProps = trigger.props
                    return React.cloneElement(trigger, {
                      key: index,
                      onClick: (e: React.MouseEvent) => {
                        setOpen(false)
                        triggerProps.onClick?.(e)
                      },
                      className: cn(
                        "flex items-center gap-3 px-3 py-2 rounded-[var(--radius-sm)] transition-colors justify-start w-full",
                        "data-[state=active]:bg-primary data-[state=active]:text-primary-foreground",
                        "hover:bg-muted",
                        triggerProps.className
                      ),
                    })
                  })}
                </TabsPrimitive.List>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
      {tabsContent}
    </TabsPrimitive.Root>
  )
})
Tabs.displayName = "Tabs"

// ─────────────────────────────────────────────────────────────────────────
// Tabs variant context — lets TabsTrigger inherit variant from TabsList
// ─────────────────────────────────────────────────────────────────────────

type TabsVariant = 'default' | 'underline' | 'pill'
/** Control height. `auto` picks `sm` on a phone and `md` elsewhere. */
type TabsSize = 'sm' | 'md' | 'auto'

const TabsVariantContext = React.createContext<{
  variant: TabsVariant
  size: Exclude<TabsSize, 'auto'>
}>({ variant: 'default', size: 'md' })

const TabsList = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.List>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.List> & {
    /**
     * Visual variant.
     * - `default` — segmented control on a `bg-muted` track, rounded corners
     * - `pill`    — the same control drawn as a capsule, with the active
     *               indicator SLIDING between tabs instead of popping
     * - `underline` — borderless, a rule under the active tab
     * @default 'default'
     */
    variant?: TabsVariant
    /**
     * Control height.
     * - `md`   — 36px, the desktop default
     * - `sm`   — 28px, for a toolbar or a phone
     * - `auto` — `sm` under the mobile breakpoint, `md` above it
     *
     * `auto` exists because consumers were already doing this by hand
     * (`isSm ? 'h-7 p-0.5 gap-0.5' : 'h-9 p-0.5'` in a widget's own file),
     * which puts a media query and a set of magic numbers in every caller.
     * @default 'md'
     */
    size?: TabsSize
    /**
     * Stretch the tabs to fill their container.
     *
     * `'mobile'` does it only below the mobile breakpoint, which is the shape
     * a toolbar actually wants: a switch that hugs its labels beside other
     * controls on a desktop row, and spans the width once it is alone on a
     * phone. Consumers were expressing this by setting `fullWidth` and then
     * undoing it in CSS (`width: auto` plus a media query back to `100%`).
     * @default false
     */
    fullWidth?: boolean | 'mobile'
    /**
     * Enable horizontal scrolling when tabs overflow
     * @default false
     */
    scrollable?: boolean
  }
>(({ className, variant = 'default', size = 'md', fullWidth = false, scrollable = false, ...props }, ref) => {
  const isUnderline = variant === 'underline'
  const isPill = variant === 'pill'
  const isMobile = useIsMobile()
  const resolvedSize = size === 'auto' ? (isMobile ? 'sm' : 'md') : size
  const resolvedFullWidth = fullWidth === 'mobile' ? isMobile : fullWidth

  // Only the pill variant animates its indicator. The default variant keeps a
  // background on the active trigger, which cannot travel between two
  // elements — moving it is the whole reason `pill` draws the indicator on the
  // list instead.
  const indicator = useTabIndicator<HTMLDivElement>()
  // Both refs always compose: hooks cannot be called conditionally, and the
  // indicator ref is inert for the variants that do not draw one.
  const listRef = useComposedRefs(ref, indicator.ref)

  // `md` keeps the 36px the default variant has always been: this size scale
  // was added for `pill`, and a taller default would silently reflow every
  // existing tab strip in every consumer.
  const sizing = resolvedSize === 'sm'
    ? { track: 'h-8 p-0.5', gap: 'gap-0.5', inset: '0.125rem' }
    : { track: 'h-9 p-1', gap: 'gap-1', inset: '0.25rem' }
  // A finger needs a 44px trigger. The track grows around it (44px + 2px padding each side) instead of the trigger
  // being squeezed to what a 28-36px track leaves.
  const touchTrack = 'pointer-coarse:h-12 pointer-coarse:p-0.5'

  const listCls = cn(
    isUnderline
      ? "inline-flex items-end gap-0 bg-transparent p-0 h-auto rounded-none"
      : cn(
          "inline-flex items-center justify-center bg-muted text-muted-foreground",
          sizing.track,
          touchTrack,
          sizing.gap,
          isPill ? "rounded-full" : "rounded-[var(--radius)]",
          isPill && "tabs-sliding",
        ),
    resolvedFullWidth && "w-full flex",
    className
  )

  const list = (
    <TabsPrimitive.List
      ref={listRef}
      className={listCls}
      // The pill is hidden until the first measurement lands, so it does not
      // fly in from the left edge of the track on mount.
      data-tab-indicator={isPill ? (indicator.ready ? 'ready' : 'idle') : undefined}
      style={
        isPill
          ? ({
              '--tab-indicator-inset': sizing.inset,
              '--tab-indicator-radius': '9999px',
            } as React.CSSProperties)
          : undefined
      }
      {...props}
    />
  )

  // For underline variant — native overflow-x-auto, full-width border via absolute element
  const wrapped = isUnderline ? (
    <div
      className={cn("relative w-full", scrollable && "overflow-x-auto")}
      style={scrollable ? { scrollbarWidth: 'none', msOverflowStyle: 'none' } as React.CSSProperties : undefined}
    >
      <div className="absolute bottom-0 left-0 right-0 h-px bg-border" />
      {list}
    </div>
  ) : scrollable ? (
    <ScrollArea className="w-full whitespace-nowrap">
      {list}
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  ) : list

  const contextValue = React.useMemo(
    () => ({ variant, size: resolvedSize }),
    [variant, resolvedSize]
  )

  return (
    <TabsVariantContext.Provider value={contextValue}>
      {wrapped}
    </TabsVariantContext.Provider>
  )
})
TabsList.displayName = TabsPrimitive.List.displayName

const TabsTrigger = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger> & {
    /**
     * Makes the trigger take equal space (use with fullWidth TabsList)
     * @default false
     */
    flexEqual?: boolean
    key?: React.Key
  }
>(({ className, flexEqual = false, ...props }, ref) => {
  const { variant, size } = React.useContext(TabsVariantContext)
  const isUnderline = variant === 'underline'
  const isPill = variant === 'pill'
  const isSm = size === 'sm'

  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(
        isUnderline
          ? [
              "relative z-10 rounded-none bg-transparent shadow-none whitespace-nowrap",
              isSm ? "px-2.5 py-2 text-xs" : "px-3 py-2.5 text-sm",
              "font-medium text-muted-foreground/60",
              "border-b-2 border-transparent",
              "transition-all duration-150",
              "hover:text-foreground",
              "focus-visible:outline-none",
              "disabled:pointer-events-none disabled:opacity-50",
              "data-[state=active]:text-foreground data-[state=active]:font-semibold",
              "data-[state=active]:border-foreground data-[state=active]:shadow-none",
            ].join(" ")
          : [
              "inline-flex items-center justify-center gap-1.5 whitespace-nowrap",
              isSm ? "px-2.5 text-xs" : "px-3 text-sm",
              "h-full font-medium",
              "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
              "disabled:pointer-events-none disabled:opacity-50",
              "data-[state=active]:text-foreground",
              // The pill variant's indicator lives on the list and travels, so
              // the trigger carries no background of its own — one would sit on
              // top of the sliding pill and give the movement away. Colour is
              // all that changes here, and it changes fast enough not to lag
              // behind the pill.
              isPill
                ? "relative rounded-full bg-transparent transition-colors duration-150 hover:text-foreground/80 data-[state=active]:bg-transparent data-[state=active]:shadow-none"
                : "rounded-[var(--radius-sm)] transition-all data-[state=active]:bg-background data-[state=active]:shadow",
            ].join(" "),
        // Touch: 44px tall for every variant (`TabsList` leaves room for it).
        "pointer-coarse:min-h-11",
        flexEqual && "flex-1",
        className
      )}
      {...props}
    />
  )
})
TabsTrigger.displayName = TabsPrimitive.Trigger.displayName

const TabsContent = React.forwardRef<
  React.ElementRef<typeof TabsPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TabsPrimitive.Content> & { key?: React.Key }
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn(
      "mt-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
      className
    )}
    {...props}
  />
))
TabsContent.displayName = TabsPrimitive.Content.displayName

export { Tabs, TabsList, TabsTrigger, TabsContent }
