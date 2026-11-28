"use client";

// ─────────────────────────────────────────────────────────────────────────────
// Primitives
// ─────────────────────────────────────────────────────────────────────────────
export { TouchSafeInput, TouchSafeTextarea, TouchSafeSelect } from './primitives/TouchSafeInput';
export type { TouchSafeInputProps, TouchSafeTextareaProps, TouchSafeSelectProps } from './primitives/TouchSafeInput';

// ─────────────────────────────────────────────────────────────────────────────
// Forms
// ─────────────────────────────────────────────────────────────────────────────
export { Button, ButtonLink, buttonVariants } from './forms/button';
export type { ButtonProps, ButtonLinkProps } from './forms/button';
export { Input } from './forms/input';
export { CONTROL_SIZE } from './forms/control-size';
export type { ControlSize, FieldControlSize } from './forms/control-size';
export { Textarea } from './forms/textarea';
export { Label } from './forms/label';
export { Checkbox } from './forms/checkbox';
export { CheckboxGroup, CheckboxGroupDescription, CheckboxGroupItem, CheckboxGroupLabel, CheckboxGroupList, CheckboxGroupMessage } from './forms/checkbox-group';
export type { CheckboxGroupProps, CheckboxGroupItemProps, CheckboxGroupListProps } from './forms/checkbox-group';
export { RadioGroup, RadioGroupItem } from './forms/radio-group';
export { Switch } from './forms/switch';
export { SettingRow, SettingsBlock } from './forms/setting-row';
export type { SettingRowProps, SettingsBlockProps } from './forms/setting-row';
export { Slider } from './forms/slider';
export { ButtonGroup, ButtonGroupSeparator, ButtonGroupText, buttonGroupVariants } from './forms/button-group';
export { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage, useFormField } from './forms/form';
export { InputGroup, InputGroupAddon, InputGroupButton, InputGroupText, InputGroupInput, InputGroupTextarea } from './forms/input-group';
export { InputAffix, type InputAffixProps } from './forms/input-affix';
export { InputOTP, InputOTPGroup, InputOTPSlot } from './forms/input-otp';
export { PhoneInput } from './forms/phone-input';
export type { PhoneInputProps } from './forms/phone-input';
export { OTPInput, InputOTPSeparator, useSmartOTP } from './forms/otp';
export type { SmartOTPProps as OTPInputProps, OTPValidationMode, OTPPasteBehavior, OTPValidator } from './forms/otp/types';
export { ButtonGroup as ButtonGroupComponent } from './forms/button-group';
export { DownloadButton } from './forms/button-download';
export type { DownloadButtonProps } from './forms/button-download';
export { PopoverActionButton } from './forms/popover-action-button';
export type { PopoverActionButtonProps } from './forms/popover-action-button';

// Money Field — amount in, minor units out.
export { MoneyField, minorUnitFactor, currencyFractionDigits } from './forms/money-field';
export type { MoneyFieldProps } from './forms/money-field';

// Mask Input
export { MaskInput } from './forms/mask-input';
export type { MaskInputProps, MaskDefinition } from './forms/mask-input';

// Segmented Input
export { SegmentedInput } from './forms/segmented-input';
export type { SegmentedInputProps } from './forms/segmented-input';

// Tags Input
export { TagsInput, TagsInputInput, TagsInputItem, TagsInputItemText, TagsInputItemDelete } from './forms/tags-input';
export type { TagsInputRootProps, TagsInputInputProps, TagsInputItemProps, TagsInputItemTextProps, TagsInputItemDeleteProps } from './forms/tags-input';

// Time Picker (click-only legacy; prefer the native-engine TimeField below).
export { TimePicker } from './forms/time-picker';
export type { TimePickerProps } from './forms/time-picker';

// Native-engine date/time fields — typeable, token-skinned, optional popover.
export {
  DateField,
  TimeField,
  DateTimeField,
  NativeFieldShell,
  NATIVE_FIELD_INPUT_CLASS,
  parseDateString,
  formatDateString,
  parseDateTimeString,
  splitDateTime,
  joinDateTime,
} from './forms/datetime-field';
export type {
  DateFieldProps,
  TimeFieldProps,
  DateTimeFieldProps,
  NativeFieldShellProps,
} from './forms/datetime-field';

// Editable
export { Editable, EditablePreview, EditableInput, EditableTextarea } from './forms/editable';
export type { EditableRootProps, EditablePreviewProps, EditableInputProps, EditableTextareaProps } from './forms/editable';

// ─────────────────────────────────────────────────────────────────────────────
// Field (advanced form layout)
// ─────────────────────────────────────────────────────────────────────────────
export { Field, FieldLabel, FieldDescription, FieldError, FieldGroup, FieldLegend, FieldSeparator, FieldSet, FieldContent, FieldTitle } from './forms/field';

// ─────────────────────────────────────────────────────────────────────────────
// Select Components (existing folder - untouched)
// ─────────────────────────────────────────────────────────────────────────────
export * from './select';

// ─────────────────────────────────────────────────────────────────────────────
// Overlay
// ─────────────────────────────────────────────────────────────────────────────
export { Dialog, DialogTrigger, DialogClose, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription, DialogPortal, DialogOverlay } from './overlay/dialog';
export { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger, AlertDialogPortal, AlertDialogOverlay } from './overlay/alert-dialog';
export { Popover, PopoverContent, PopoverTrigger, PopoverAnchor, PopoverArrow } from './overlay/popover';
export { Sheet, SheetTrigger, SheetClose, SheetContent, SheetHeader, SheetFooter, SheetTitle, SheetDescription, SheetPortal, SheetOverlay } from './overlay/sheet';
export { Drawer, DrawerTrigger, DrawerClose, DrawerContent, DrawerHeader, DrawerFooter, DrawerTitle, DrawerDescription, DrawerPortal, DrawerOverlay, useDrawerSize } from './overlay/drawer';
export { ResponsiveSheet, ResponsiveSheetContent, ResponsiveSheetHeader, ResponsiveSheetTitle, ResponsiveSheetDescription, ResponsiveSheetFooter } from './overlay/responsive-sheet';
export { SidePanel, SidePanelContent, SidePanelHeader, SidePanelTitle, SidePanelDescription, SidePanelBody, SidePanelFooter, SidePanelClose } from './overlay/side-panel';
export type { SidePanelProps, SidePanelContentProps, SidePanelCloseProps } from './overlay/side-panel';
export { HoverCard, HoverCardContent, HoverCardTrigger } from './overlay/hover-card';
export { Tooltip, TooltipContent, TooltipHint, TooltipProvider, TooltipTrigger } from './overlay/tooltip';
export type { TooltipConfig, TooltipProp } from './overlay/tooltip';

// ─────────────────────────────────────────────────────────────────────────────
// Navigation
// ─────────────────────────────────────────────────────────────────────────────
export { navigationMenuTriggerStyle, NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuContent, NavigationMenuTrigger, NavigationMenuLink, NavigationMenuIndicator, NavigationMenuViewport } from './navigation/navigation-menu';
export { Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem, MenubarSeparator, MenubarLabel, MenubarCheckboxItem, MenubarRadioGroup, MenubarRadioItem, MenubarPortal, MenubarSubContent, MenubarSubTrigger, MenubarGroup, MenubarSub, MenubarShortcut } from './navigation/menubar';
export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuCheckboxItem, DropdownMenuRadioItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuShortcut, DropdownMenuGroup, DropdownMenuPortal, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuRadioGroup, revealOnRowInteraction } from './navigation/dropdown-menu';
export { ContextMenu, ContextMenuCheckboxItem, ContextMenuContent, ContextMenuItem, ContextMenuLabel, ContextMenuRadioGroup, ContextMenuRadioItem, ContextMenuSeparator, ContextMenuShortcut, ContextMenuSub, ContextMenuSubContent, ContextMenuSubTrigger, ContextMenuTrigger } from './navigation/context-menu';
export { PopoverRowButton } from './navigation/popover-row-button';
export type { PopoverRowButtonProps } from './navigation/popover-row-button';
export { MenuBuilder } from './navigation/menu';
export type { MenuItem, MenuActionItem, MenuSubmenuItem, MenuCheckboxItem, MenuRadioGroup, MenuRadioOption, MenuSeparator, MenuLabel, MenuSection, MenuCustom, MenuRowBase, MenuBuilderProps } from './navigation/menu';
export { Tabs, TabsContent, TabsList, TabsTrigger } from './navigation/tabs';
export { useTabsState } from './navigation/tabs/useTabsState';
export type { UseTabsStateOptions, UseTabsStateResult } from './navigation/tabs/useTabsState';
export { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './navigation/accordion';
export { useAccordionSingleState, useAccordionMultipleState } from './navigation/accordion/useAccordionState';
export type { UseAccordionSingleResult, UseAccordionMultipleResult } from './navigation/accordion/useAccordionState';
export { Collapsible, CollapsibleContent, CollapsibleTrigger } from './navigation/collapsible';
export { Disclosure } from './navigation/disclosure';
export type { DisclosureProps, DisclosureTone, DisclosureSize } from './navigation/disclosure';
export { Command, CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator, CommandShortcut } from './navigation/command';
export { Link, LinkProvider, LinkComponentContext, useLinkComponent } from './navigation/link';
export type { LinkProps, LinkComponent, LinkComponentProps, LinkProviderProps } from './navigation/link';
export {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbNavigation,
} from './navigation/breadcrumb';
export type { BreadcrumbNavigationItem, BreadcrumbNavigationProps } from './navigation/breadcrumb';
export {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
  StaticPagination,
  SSRPagination,
  useDRFPagination,
  useDRFPaginationInfo,
} from './navigation/pagination';
export type { DRFPaginatedResponse } from './navigation/pagination';
export {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupAction,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInput,
  SidebarInset,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSkeleton,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  SidebarProvider,
  SidebarRail,
  SidebarSeparator,
  SidebarTrigger,
  SIDEBAR_KEYBOARD_SHORTCUT,
  useSidebar,
} from './navigation/sidebar';
export { Stepper, StepperContent, StepperDescription, StepperIndicator, StepperItem, StepperList, StepperNext, StepperPrev, StepperSeparator, StepperTitle, StepperTrigger, useStepper } from './navigation/stepper';
export type { StepperProps } from './navigation/stepper';

// ─────────────────────────────────────────────────────────────────────────────
// Layout
// ─────────────────────────────────────────────────────────────────────────────
export { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from './layout/card';
export { Separator } from './layout/separator';
export { Skeleton } from './layout/skeleton';
export { AspectRatio } from './layout/aspect-ratio';
export { ScrollArea, ScrollBar } from './layout/scroll-area';
export type { ScrollAreaHandle, ScrollAreaProps, ScrollAreaOrientation } from './layout/scroll-area';
export { ResizableHandle, ResizablePanel, ResizablePanelGroup, useResizableDragging } from './layout/resizable';
export type { ResizableHandleProps, ImperativePanelHandle } from './layout/resizable';
export { Sticky } from './layout/sticky';
export { Section, SectionHeader } from './layout/section';
export { Stack, StackItem } from './layout/stack';
export type { StackProps } from './layout/stack';
export { KeyValue, KeyValueAdd, KeyValueError, KeyValueItem, KeyValueKeyInput, KeyValueList, KeyValueRemove, KeyValueValueInput, useKeyValueStore } from './layout/key-value';
export type { KeyValueProps, KeyValueItemData } from './layout/key-value';

// ─────────────────────────────────────────────────────────────────────────────
// Data Display
// ─────────────────────────────────────────────────────────────────────────────
export { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableFooter, TableRow } from './data/table';
export { Badge, badgeVariants } from './data/badge';
export { Avatar, AvatarFallback, AvatarImage } from './data/avatar';
export { Progress } from './data/progress';
export { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from './data/carousel';
export type { CarouselApi } from './data/carousel';
export { Calendar, CalendarDayButton } from './data/calendar';
export { DatePicker, DateRangePicker } from './data/calendar';
export type { DatePickerProps, DateRangePickerProps, DateRange } from './data/calendar';
export { Toggle, toggleVariants } from './data/toggle';
export { FilterBar } from './layout/filter-bar';
export type { FilterBarProps } from './layout/filter-bar';
export { FilterButton } from './forms/filter-button';
export { FilterMenu } from './forms/filter-menu';
export type { FilterMenuProps, FilterMenuOption } from './forms/filter-menu';
export type { FilterButtonProps } from './forms/filter-button';
export { ToggleGroup, ToggleGroupItem } from './data/toggle-group';
export { AvatarGroup } from './data/avatar-group';
export type { AvatarGroupProps } from './data/avatar-group';
export { BadgeOverflow } from './data/badge-overflow';
export type { BadgeOverflowProps } from './data/badge-overflow';
export { Stat, StatDescription, StatIndicator, StatLabel, StatSeparator, StatTrend, StatValue, statIndicatorVariants } from './data/stat';
export type { StatIndicatorProps } from './data/stat';
export { Status, StatusIndicator, StatusLabel, statusVariants } from './data/status';
export type { StatusProps } from './data/status';
export { CircularProgress, CircularProgressCombined, CircularProgressIndicator, CircularProgressRange, CircularProgressTrack, CircularProgressValueText } from './data/circular-progress';
export type { CircularProgressProps } from './data/circular-progress';
export { RelativeTimeCard, relativeTimeCardVariants } from './data/relative-time-card';
export type { RelativeTimeCardProps } from './data/relative-time-card';
export { BalancedText, DEFAULT_BALANCED_FONT, DEFAULT_BALANCED_MAX_WIDTH } from './data/BalancedText';
export type { BalancedTextProps, BalancedFont } from './data/BalancedText';

// ─────────────────────────────────────────────────────────────────────────────
// Chart Components
// ─────────────────────────────────────────────────────────────────────────────
// Charts are NOT re-exported from this main barrel ON PURPOSE: they pull in the
// heavy `recharts` dependency (which imports CJS `lodash/get`), and dragging
// that into every `import { Button } from "@djangocfg/ui-core"` both bloats the
// graph and breaks Vite dev (native-ESM) CJS-interop on consumers that never use
// charts. Import charts from the dedicated subpath instead — same pay-for-what-
// you-use pattern as `@djangocfg/ui-core/lib/dialog-service`:
//   import { ChartContainer, ChartTooltip, … } from "@djangocfg/ui-core/chart";

// ─────────────────────────────────────────────────────────────────────────────
// Feedback
// ─────────────────────────────────────────────────────────────────────────────
export { Alert, AlertDescription, AlertTitle } from './feedback/alert';
export { Spinner } from './feedback/spinner';
export { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyContent, EmptyMedia } from './feedback/empty';
export { Preloader, PreloaderSkeleton } from './feedback/preloader';
export type { PreloaderProps, PreloaderSkeletonProps } from './feedback/preloader';
export { Toaster } from './feedback/sonner';
export { Banner, BannerActions, BannerClose, BannerContent, BannerDescription, BannerIcon, Banners, BannerTitle, useBanner, useBanners } from './feedback/banner';
export type { BannerProps, BannersProps, BannerVariant } from './feedback/banner';

// ─────────────────────────────────────────────────────────────────────────────
// Boundary
// ─────────────────────────────────────────────────────────────────────────────
export { Boundary, useBoundary } from './boundary';
export type {
  BoundaryProps,
  BoundaryVariant,
  BoundaryRenderProps,
  BoundaryResetReason,
  BoundaryResetDetails,
  BoundaryLogger,
} from './boundary';

// ─────────────────────────────────────────────────────────────────────────────
// Specialized
// ─────────────────────────────────────────────────────────────────────────────
export { Kbd, KbdGroup } from './specialized/kbd';
export type { KbdProps, KbdSize } from './specialized/kbd';
export { CopyButton, CopyField } from './specialized/copy';
export type { CopyButtonProps, CopyFieldProps } from './specialized/copy';
export { TokenIcon, getAllTokenSymbols, searchTokens, getTokensByCategory } from './specialized/token-icon';
export type { TokenIconProps, TokenSymbol, TokenCategory } from './specialized/token-icon';
export { Item, ItemMedia, ItemContent, ItemActions, ItemGroup, ItemSeparator, ItemTitle, ItemDescription, ItemHeader, ItemFooter } from './specialized/item';
export { Portal } from './specialized/portal';
export type { PortalProps } from './specialized/portal';
export { Presence } from './specialized/presence';
export type { PresenceProps } from './specialized/presence';
export { VisuallyHidden } from './specialized/visually-hidden';
export { VisuallyHiddenInput } from './specialized/visually-hidden-input';
export type { VisuallyHiddenInputProps, InputValue as VisuallyHiddenInputValue } from './specialized/visually-hidden-input';
export { Primitive, dispatchDiscreteCustomEvent } from './specialized/primitive';
export type { PrimitivePropsWithRef } from './specialized/primitive';
export { ImageWithFallback } from './specialized/image-with-fallback';
export type { ImageWithFallbackProps } from './specialized/image-with-fallback';
export { Flag, LanguageFlag, LANGUAGE_TO_COUNTRY, getLanguageCountryCode, FLAG_LOADERS } from './specialized/flag';
export type { FlagProps, LanguageFlagProps, FlagLoader } from './specialized/flag';

// ─────────────────────────────────────────────────────────────────────────────
// Effects
// ─────────────────────────────────────────────────────────────────────────────
export { GlowBackground } from './effects';
export type { GlowBackgroundProps } from './effects';
export { Swap, SwapOff, SwapOn, useSwap } from './effects/swap';
export type { SwapProps } from './effects/swap';
