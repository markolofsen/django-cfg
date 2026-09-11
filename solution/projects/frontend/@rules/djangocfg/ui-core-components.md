---
title: "ui-core — component catalogue"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/ui-core` — components

Every component export, by group. **Scan this before writing a `<div>`.** Import
rules are in [overview.md](overview.md); import everything below from
`@djangocfg/ui-core` directly — the group is where the source lives, not a path.

## Choosing between near-identical exports

The catalogue answers "does it exist". This answers "which one", where the names
alone do not.

| Reaching for | Use | Not |
|---|---|---|
| A date input in a form | `DateField` / `TimeField` / `DateTimeField` (`forms/datetime-field`) | `DatePicker`, `Calendar` — the calendar is the popup surface, not the field |
| An amount of money | `MoneyField` — carries **integer minor units**, never a float | `Input type="number"` |
| A dropdown with search | `Combobox`; `ComboboxAsync` when options are fetched | `Select`, which is a fixed list |
| Multi-select | `MultiSelect` for a short list; `MultiSelectPro` for tags/grouping; `…ProAsync` when fetched | — |
| A side panel | `ResponsiveSheet` — a sheet on desktop, a drawer on mobile | `Sheet` or `Drawer` directly, unless the breakpoint behaviour is deliberate |
| A modal that asks a yes/no | `AlertDialog`, or the imperative `dialog-service` `confirm()` | `Dialog` with hand-built buttons |
| An empty state | `Empty` + `EmptyTitle` / `EmptyDescription` / `EmptyMedia` | a bespoke centred `<div>` |
| A row in a list with actions | `Item` + `ItemContent` / `ItemActions` / `ItemMedia` | a bespoke flex row |
| A metric readout | `Stat` + `StatValue` / `StatLabel` / `StatTrend` | a bespoke figure |
| A labelled form row | `Field` + `FieldLabel` / `FieldError` / `FieldDescription` | a hand-built `<label>` pair |
| A settings toggle row | `SettingRow` inside `SettingsBlock` | a bespoke flex row |

`Container` and `Grid` do **not** exist — use `Stack` or Tailwind utilities.
`Marquee` is in [`@djangocfg/widget-visual`](widgets.md), not here.

## Traps

- **Compound components are not optional.** `Table`, `Card`, `Stat`, `Item`,
  `Empty`, `Field`, `Stepper` and the menus all expose a root plus parts. The
  root alone usually renders nothing useful.
- **`Link` routes through the adapter.** It needs the Next adapter mounted (see
  [layouts](layouts.md)); without it, it falls back to the History API and the
  App Router never sees the navigation.
- **A `*Variants` export is a class-generator, not a component** —
  `buttonVariants`, `badgeVariants`, `statusVariants` return class strings for
  composing onto another element.

<!-- GENERATED:start -->
_397 exports in 10 groups. Generated from `ui-core/src/components/index.ts` — do not hand-edit._

| Group | Exports | Names |
|---|---|---|
| `boundary` | 2 | `Boundary` · `useBoundary` |
| `data` | 52 | `Avatar` · `AvatarFallback` · `AvatarGroup` · `AvatarImage` · `Badge` · `BadgeOverflow` · `BalancedText` · `Calendar` · `CalendarDayButton` · `Carousel` · `CarouselContent` · `CarouselItem` · `CarouselNext` · `CarouselPrevious` · `CircularProgress` · `CircularProgressCombined` · `CircularProgressIndicator` · `CircularProgressRange` · `CircularProgressTrack` · `CircularProgressValueText` · `DEFAULT_BALANCED_FONT` · `DEFAULT_BALANCED_MAX_WIDTH` · `DatePicker` · `DateRangePicker` · `Progress` · `RelativeTimeCard` · `Stat` · `StatDescription` · `StatIndicator` · `StatLabel` · `StatSeparator` · `StatTrend` · `StatValue` · `Status` · `StatusIndicator` · `StatusLabel` · `Table` · `TableBody` · `TableCaption` · `TableCell` · `TableFooter` · `TableHead` · `TableHeader` · `TableRow` · `Toggle` · `ToggleGroup` · `ToggleGroupItem` · `badgeVariants` · `relativeTimeCardVariants` · `statIndicatorVariants` · `statusVariants` · `toggleVariants` |
| `effects` | 5 | `GlowBackground` · `Swap` · `SwapOff` · `SwapOn` · `useSwap` |
| `feedback` | 23 | `Alert` · `AlertDescription` · `AlertTitle` · `Banner` · `BannerActions` · `BannerClose` · `BannerContent` · `BannerDescription` · `BannerIcon` · `BannerTitle` · `Banners` · `Empty` · `EmptyContent` · `EmptyDescription` · `EmptyHeader` · `EmptyMedia` · `EmptyTitle` · `Preloader` · `PreloaderSkeleton` · `Spinner` · `Toaster` · `useBanner` · `useBanners` |
| `forms` | 73 | `Button` · `ButtonGroup` · `ButtonGroupComponent` · `ButtonGroupSeparator` · `ButtonGroupText` · `ButtonLink` · `Checkbox` · `CheckboxGroup` · `CheckboxGroupDescription` · `CheckboxGroupItem` · `CheckboxGroupLabel` · `CheckboxGroupList` · `CheckboxGroupMessage` · `DownloadButton` · `Editable` · `EditableInput` · `EditablePreview` · `EditableTextarea` · `Field` · `FieldContent` · `FieldDescription` · `FieldError` · `FieldGroup` · `FieldLabel` · `FieldLegend` · `FieldSeparator` · `FieldSet` · `FieldTitle` · `Form` · `FormControl` · `FormDescription` · `FormField` · `FormItem` · `FormLabel` · `FormMessage` · `Input` · `InputAffix` · `InputGroup` · `InputGroupAddon` · `InputGroupButton` · `InputGroupInput` · `InputGroupText` · `InputGroupTextarea` · `InputOTP` · `InputOTPGroup` · `InputOTPSeparator` · `InputOTPSlot` · `Label` · `MaskInput` · `MoneyField` · `OTPInput` · `PhoneInput` · `PopoverActionButton` · `RadioGroup` · `RadioGroupItem` · `SegmentedInput` · `SettingRow` · `SettingsBlock` · `Slider` · `Switch` · `TagsInput` · `TagsInputInput` · `TagsInputItem` · `TagsInputItemDelete` · `TagsInputItemText` · `Textarea` · `TimePicker` · `buttonGroupVariants` · `buttonVariants` · `currencyFractionDigits` · `minorUnitFactor` · `useFormField` · `useSmartOTP` |
| `layout` | 29 | `AspectRatio` · `Card` · `CardContent` · `CardDescription` · `CardFooter` · `CardHeader` · `CardTitle` · `KeyValue` · `KeyValueAdd` · `KeyValueError` · `KeyValueItem` · `KeyValueKeyInput` · `KeyValueList` · `KeyValueRemove` · `KeyValueValueInput` · `ResizableHandle` · `ResizablePanel` · `ResizablePanelGroup` · `ScrollArea` · `ScrollBar` · `Section` · `SectionHeader` · `Separator` · `Skeleton` · `Stack` · `StackItem` · `Sticky` · `useKeyValueStore` · `useResizableDragging` |
| `navigation` | 96 | `Accordion` · `AccordionContent` · `AccordionItem` · `AccordionTrigger` · `Collapsible` · `CollapsibleContent` · `CollapsibleTrigger` · `Command` · `CommandDialog` · `CommandEmpty` · `CommandGroup` · `CommandInput` · `CommandItem` · `CommandList` · `CommandSeparator` · `CommandShortcut` · `ContextMenu` · `ContextMenuCheckboxItem` · `ContextMenuContent` · `ContextMenuItem` · `ContextMenuLabel` · `ContextMenuRadioGroup` · `ContextMenuRadioItem` · `ContextMenuSeparator` · `ContextMenuShortcut` · `ContextMenuSub` · `ContextMenuSubContent` · `ContextMenuSubTrigger` · `ContextMenuTrigger` · `Disclosure` · `DropdownMenu` · `DropdownMenuCheckboxItem` · `DropdownMenuContent` · `DropdownMenuGroup` · `DropdownMenuItem` · `DropdownMenuLabel` · `DropdownMenuPortal` · `DropdownMenuRadioGroup` · `DropdownMenuRadioItem` · `DropdownMenuSeparator` · `DropdownMenuShortcut` · `DropdownMenuSub` · `DropdownMenuSubContent` · `DropdownMenuSubTrigger` · `DropdownMenuTrigger` · `Link` · `LinkComponentContext` · `LinkProvider` · `MenuBuilder` · `Menubar` · `MenubarCheckboxItem` · `MenubarContent` · `MenubarGroup` · `MenubarItem` · `MenubarLabel` · `MenubarMenu` · `MenubarPortal` · `MenubarRadioGroup` · `MenubarRadioItem` · `MenubarSeparator` · `MenubarShortcut` · `MenubarSub` · `MenubarSubContent` · `MenubarSubTrigger` · `MenubarTrigger` · `NavigationMenu` · `NavigationMenuContent` · `NavigationMenuIndicator` · `NavigationMenuItem` · `NavigationMenuLink` · `NavigationMenuList` · `NavigationMenuTrigger` · `NavigationMenuViewport` · `PopoverRowButton` · `Stepper` · `StepperContent` · `StepperDescription` · `StepperIndicator` · `StepperItem` · `StepperList` · `StepperNext` · `StepperPrev` · `StepperSeparator` · `StepperTitle` · `StepperTrigger` · `Tabs` · `TabsContent` · `TabsList` · `TabsTrigger` · `navigationMenuTriggerStyle` · `revealOnRowInteraction` · `useAccordionMultipleState` · `useAccordionSingleState` · `useLinkComponent` · `useStepper` · `useTabsState` |
| `overlay` | 68 | `AlertDialog` · `AlertDialogAction` · `AlertDialogCancel` · `AlertDialogContent` · `AlertDialogDescription` · `AlertDialogFooter` · `AlertDialogHeader` · `AlertDialogOverlay` · `AlertDialogPortal` · `AlertDialogTitle` · `AlertDialogTrigger` · `Dialog` · `DialogClose` · `DialogContent` · `DialogDescription` · `DialogFooter` · `DialogHeader` · `DialogOverlay` · `DialogPortal` · `DialogTitle` · `DialogTrigger` · `Drawer` · `DrawerClose` · `DrawerContent` · `DrawerDescription` · `DrawerFooter` · `DrawerHeader` · `DrawerOverlay` · `DrawerPortal` · `DrawerTitle` · `DrawerTrigger` · `HoverCard` · `HoverCardContent` · `HoverCardTrigger` · `Popover` · `PopoverAnchor` · `PopoverArrow` · `PopoverContent` · `PopoverTrigger` · `ResponsiveSheet` · `ResponsiveSheetContent` · `ResponsiveSheetDescription` · `ResponsiveSheetFooter` · `ResponsiveSheetHeader` · `ResponsiveSheetTitle` · `Sheet` · `SheetClose` · `SheetContent` · `SheetDescription` · `SheetFooter` · `SheetHeader` · `SheetOverlay` · `SheetPortal` · `SheetTitle` · `SheetTrigger` · `SidePanel` · `SidePanelBody` · `SidePanelClose` · `SidePanelContent` · `SidePanelDescription` · `SidePanelFooter` · `SidePanelHeader` · `SidePanelTitle` · `Tooltip` · `TooltipContent` · `TooltipProvider` · `TooltipTrigger` · `useDrawerSize` |
| `select` | 19 | `Combobox` · `ComboboxAsync` · `CountrySelect` · `LanguageSelect` · `MultiSelect` · `MultiSelectPro` · `MultiSelectProAsync` · `Select` · `SelectContent` · `SelectGroup` · `SelectItem` · `SelectLabel` · `SelectScrollDownButton` · `SelectScrollUpButton` · `SelectSeparator` · `SelectTrigger` · `SelectValue` · `createOption` · `createOptions` |
| `specialized` | 30 | `CopyButton` · `CopyField` · `FLAG_COMPONENTS` · `Flag` · `ImageWithFallback` · `Item` · `ItemActions` · `ItemContent` · `ItemDescription` · `ItemFooter` · `ItemGroup` · `ItemHeader` · `ItemMedia` · `ItemSeparator` · `ItemTitle` · `Kbd` · `KbdGroup` · `LANGUAGE_TO_COUNTRY` · `LanguageFlag` · `Portal` · `Presence` · `Primitive` · `TokenIcon` · `VisuallyHidden` · `VisuallyHiddenInput` · `dispatchDiscreteCustomEvent` · `getAllTokenSymbols` · `getLanguageCountryCode` · `getTokensByCategory` · `searchTokens` |
<!-- GENERATED:end -->

## Where to look next

The prop contract is the source. In the djangocfg checkout:
`projects/solution/frontend/packages/ui-core/src/components/<group>/<name>/`.
Several carry their own README — `forms/datetime-field/`, `forms/money-field/`,
`select/`, `boundary/`.

Every group also ships `Gallery.stories.tsx`; Storybook (port **6017** in the
djangocfg repo) renders them.
