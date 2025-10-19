# 🧩 LLM-Optimized Documentation for UI Package (Single File, No Glossary, No Schemas)

## 🎯 Goal

Create a **single-file**, **token-efficient**, **machine-readable** documentation format that:

- Integrates smoothly with LLMs in Cursor IDE.
- Enables structured code generation and API understanding.
- Captures architecture, logic, and usage flows clearly.

---

## 🧱 Structure

Use the following structure in a single `.md` file:

```
# Overview
# Modules
# APIs (ReadMe.LLM format)
# Flows
# Terms (inline, where needed)
```

Each section should be concise and semantically organized using headings (`##`, `###`).

---

## 📖 Overview

This documentation provides LLM-readable references for UI package hooks, components, and blocks in the landings project.
It is optimized for use inside Cursor IDE and for retrieval-augmented prompting (RAG).

---

## 📦 Modules

### @hooks/useToast

**Purpose**:
Toast notification system with state management and auto-dismiss functionality.

**Dependencies**:
- React
- `@/components/toast`

**Exports**:
- `useToast`
- `toast`

**Used in**:
- Landing pages
- Form submissions
- User feedback

---

### @hooks/useAuthDialog

**Purpose**:
Authentication dialog management with event-driven architecture.

**Dependencies**:
- `@repo/auth`
- `useEventsBus`
- `DIALOG_EVENTS`

**Exports**:
- `useAuthDialog`

**Used in**:
- Protected content areas
- User authentication flows

---

### @hooks/useCountdown

**Purpose**:
Real-time countdown timer with moment.js integration.

**Dependencies**:
- `moment`
- React hooks

**Exports**:
- `useCountdown`

**Used in**:
- Limited-time offers
- Event countdowns
- Promotional campaigns

---

### @hooks/useDebouncedCallback

**Purpose**:
Debounced function execution to optimize performance.

**Dependencies**:
- React hooks

**Exports**:
- `useDebouncedCallback`

**Used in**:
- Search inputs
- Form validation
- API calls

---

### @hooks/useEventsBus

**Purpose**:
Event-driven communication system for component interaction.

**Dependencies**:
- React hooks

**Exports**:
- `events`
- `useEventListener`

**Used in**:
- Cross-component communication
- Dialog management
- State synchronization

---

### @hooks/useLocalStorage

**Purpose**:
Enhanced localStorage management with error handling and quota management.

**Dependencies**:
- React hooks
- Browser localStorage API

**Exports**:
- `useLocalStorage`

**Used in**:
- User preferences
- Form persistence
- Cache management

---

### @hooks/useSessionStorage

**Purpose**:
Enhanced sessionStorage management with error handling and quota management.

**Dependencies**:
- React hooks
- Browser sessionStorage API

**Exports**:
- `useSessionStorage`

**Used in**:
- Session data
- Temporary form data
- User session state

---

### @hooks/useMobile

**Purpose**:
Responsive design hook for mobile detection.

**Dependencies**:
- React hooks
- Browser matchMedia API

**Exports**:
- `useIsMobile`

**Used in**:
- Responsive layouts
- Mobile-specific features
- Adaptive UI

---

### @hooks/useDebugTools

**Purpose**:
React DevTools integration for debugging component state.

**Dependencies**:
- React `useDebugValue`

**Exports**:
- `useDebugTools`

**Used in**:
- Development debugging
- Component state inspection
- Performance monitoring

---

### @blocks/Hero

**Purpose**:
Landing page hero section with customizable actions and backgrounds.

**Dependencies**:
- `@/components/button`
- `@/lib/utils`
- Next.js Link

**Props**:
- `title`: string
- `subtitle?`: string
- `description?`: string
- `primaryAction?`: ActionConfig
- `secondaryAction?`: ActionConfig
- `background?`: 'gradient' | 'solid' | 'image' | 'dark'
- `className?`: string
- `children?`: ReactNode

**Used in**:
- Landing pages
- Marketing pages
- Product introductions

---

### @blocks/FeatureSection

**Purpose**:
Feature showcase section with grid layout and card-based presentation.

**Dependencies**:
- `@/components/card`
- `@/lib/utils`

**Props**:
- `title`: string
- `subtitle?`: string
- `features`: Feature[]
- `columns?`: 1 | 2 | 3 | 4
- `className?`: string
- `background?`: 'dark' | 'card' | 'gradient'

**Used in**:
- Product features
- Service descriptions
- Feature comparisons

---

### @components/Button

**Purpose**:
Versatile button component with multiple variants and link support.

**Dependencies**:
- `@radix-ui/react-slot`
- `class-variance-authority`
- `@/lib/utils`
- Next.js Link

**Variants**:
- `default`: Primary button
- `destructive`: Danger button
- `outline`: Bordered button
- `secondary`: Secondary button
- `ghost`: Transparent button
- `link`: Link-style button

**Sizes**:
- `default`: Standard size
- `sm`: Small size
- `lg`: Large size
- `icon`: Icon-only size

**Used in**:
- Forms
- Navigation
- Actions
- CTAs

---

### @components/Card

**Purpose**:
Card container with header, content, and footer sections.

**Dependencies**:
- `@/lib/utils`

**Exports**:
- `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`

**Props**:
- `className?`: string
- All HTML div attributes

**Used in**:
- Feature sections
- Product cards
- Content containers

---

### @components/Input

**Purpose**:
Form input component with consistent styling.

**Dependencies**:
- `@/lib/utils`

**Props**:
- `type?`: string
- `className?`: string
- All HTML input attributes

**Used in**:
- Forms
- Search inputs
- Data entry

---

### @components/Dialog

**Purpose**:
Modal dialog component with overlay and content sections.

**Dependencies**:
- `@radix-ui/react-dialog`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogFooter`, `DialogTitle`, `DialogDescription`, `DialogClose`, `DialogOverlay`, `DialogPortal`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `className?`: string
- All Radix Dialog props

**Used in**:
- Modals
- Confirmations
- Forms in dialogs

---

### @components/Select

**Purpose**:
Dropdown select component with options and groups.

**Dependencies**:
- `@radix-ui/react-select`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Select`, `SelectGroup`, `SelectValue`, `SelectTrigger`, `SelectContent`, `SelectLabel`, `SelectItem`, `SelectSeparator`, `SelectScrollUpButton`, `SelectScrollDownButton`

**Props**:
- `value?`: string
- `onValueChange?`: (value: string) => void
- `defaultValue?`: string
- `disabled?`: boolean
- `className?`: string
- All Radix Select props

**Used in**:
- Form selects
- Filter dropdowns
- Option selection

---

### @components/Accordion

**Purpose**:
Collapsible content sections with smooth animations.

**Dependencies**:
- `@radix-ui/react-accordion`
- `@/lib/utils`

**Exports**:
- `Accordion`, `AccordionItem`, `AccordionTrigger`, `AccordionContent`

**Props**:
- `type?`: 'single' | 'multiple'
- `collapsible?`: boolean
- `value?`: string | string[]
- `onValueChange?`: (value: string | string[]) => void
- `className?`: string

**Used in**:
- FAQs
- Collapsible sections
- Expandable content

---

### @components/Alert

**Purpose**:
Alert component for notifications and warnings.

**Dependencies**:
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Alert`, `AlertTitle`, `AlertDescription`

**Props**:
- `variant?`: 'default' | 'destructive'
- `className?`: string
- All HTML div attributes

**Used in**:
- Error messages
- Success notifications
- Warning alerts

---

### @components/AlertDialog

**Purpose**:
Confirmation dialog with destructive actions.

**Dependencies**:
- `@radix-ui/react-alert-dialog`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `AlertDialog`, `AlertDialogTrigger`, `AlertDialogContent`, `AlertDialogHeader`, `AlertDialogFooter`, `AlertDialogTitle`, `AlertDialogDescription`, `AlertDialogAction`, `AlertDialogCancel`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `className?`: string
- All Radix AlertDialog props

**Used in**:
- Delete confirmations
- Destructive actions
- Critical confirmations

---

### @components/Avatar

**Purpose**:
User avatar component with fallback and image support.

**Dependencies**:
- `@radix-ui/react-avatar`
- `@/lib/utils`

**Exports**:
- `Avatar`, `AvatarImage`, `AvatarFallback`

**Props**:
- `src?`: string
- `alt?`: string
- `fallback?`: ReactNode
- `className?`: string
- All Radix Avatar props

**Used in**:
- User profiles
- Comment sections
- User lists

---

### @components/Badge

**Purpose**:
Small status indicator with variants.

**Dependencies**:
- `@/lib/utils`

**Props**:
- `variant?`: 'default' | 'secondary' | 'destructive' | 'outline'
- `className?`: string
- All HTML span attributes

**Used in**:
- Status indicators
- Tags
- Labels

---

### @components/Breadcrumb

**Purpose**:
Navigation breadcrumb component.

**Dependencies**:
- `@radix-ui/react-navigation-menu`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Breadcrumb`, `BreadcrumbList`, `BreadcrumbItem`, `BreadcrumbLink`, `BreadcrumbPage`, `BreadcrumbSeparator`

**Props**:
- `className?`: string
- All Radix NavigationMenu props

**Used in**:
- Page navigation
- Site structure
- Breadcrumb trails

---

### @components/Calendar

**Purpose**:
Date picker calendar component.

**Dependencies**:
- `react-day-picker`
- `@/lib/utils`
- `date-fns`

**Props**:
- `mode?`: 'single' | 'multiple' | 'range'
- `selected?`: Date | Date[] | DateRange
- `onSelect?`: (date: Date | Date[] | DateRange | undefined) => void
- `disabled?`: Date[] | ((date: Date) => boolean)
- `className?`: string

**Used in**:
- Date selection
- Date range pickers
- Event scheduling

---

### @components/Carousel

**Purpose**:
Image carousel with navigation and indicators.

**Dependencies**:
- `embla-carousel-react`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Carousel`, `CarouselContent`, `CarouselItem`, `CarouselPrevious`, `CarouselNext`

**Props**:
- `opts?`: EmblaOptionsType
- `plugins?`: EmblaPluginType[]
- `orientation?`: 'horizontal' | 'vertical'
- `className?`: string

**Used in**:
- Image galleries
- Product showcases
- Content sliders

---

### @components/Checkbox

**Purpose**:
Checkbox input component.

**Dependencies**:
- `@radix-ui/react-checkbox`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Checkbox`

**Props**:
- `checked?`: boolean
- `onCheckedChange?`: (checked: boolean) => void
- `disabled?`: boolean
- `className?`: string
- All Radix Checkbox props

**Used in**:
- Form checkboxes
- Settings toggles
- Multi-select lists

---

### @components/Collapsible

**Purpose**:
Simple collapsible content component.

**Dependencies**:
- `@radix-ui/react-collapsible`
- `@/lib/utils`

**Exports**:
- `Collapsible`, `CollapsibleTrigger`, `CollapsibleContent`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `className?`: string
- All Radix Collapsible props

**Used in**:
- Expandable content
- Collapsible sections
- Toggle content

---

### @components/Command

**Purpose**:
Command palette component with search and navigation.

**Dependencies**:
- `cmdk`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Command`, `CommandDialog`, `CommandInput`, `CommandList`, `CommandEmpty`, `CommandGroup`, `CommandItem`, `CommandSeparator`, `CommandShortcut`

**Props**:
- `value?`: string
- `onValueChange?`: (value: string) => void
- `className?`: string
- All cmdk props

**Used in**:
- Command palettes
- Search interfaces
- Keyboard navigation

---

### @components/ContextMenu

**Purpose**:
Right-click context menu component.

**Dependencies**:
- `@radix-ui/react-context-menu`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `ContextMenu`, `ContextMenuTrigger`, `ContextMenuContent`, `ContextMenuItem`, `ContextMenuCheckboxItem`, `ContextMenuRadioItem`, `ContextMenuLabel`, `ContextMenuSeparator`, `ContextMenuShortcut`, `ContextMenuGroup`, `ContextMenuPortal`, `ContextMenuSub`, `ContextMenuSubContent`, `ContextMenuSubTrigger`, `ContextMenuRadioGroup`

**Props**:
- `className?`: string
- All Radix ContextMenu props

**Used in**:
- Right-click menus
- Context actions
- Quick actions

---

### @components/DropdownMenu

**Purpose**:
Dropdown menu component with items and submenus.

**Dependencies**:
- `@radix-ui/react-dropdown-menu`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `DropdownMenu`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`, `DropdownMenuCheckboxItem`, `DropdownMenuRadioItem`, `DropdownMenuLabel`, `DropdownMenuSeparator`, `DropdownMenuShortcut`, `DropdownMenuGroup`, `DropdownMenuPortal`, `DropdownMenuSub`, `DropdownMenuSubContent`, `DropdownMenuSubTrigger`, `DropdownMenuRadioGroup`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `className?`: string
- All Radix DropdownMenu props

**Used in**:
- User menus
- Action dropdowns
- Settings menus

---

### @components/Drawer

**Purpose**:
Slide-out drawer component for mobile navigation.

**Dependencies**:
- `vaul`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Drawer`, `DrawerTrigger`, `DrawerClose`, `DrawerContent`, `DrawerDescription`, `DrawerFooter`, `DrawerHeader`, `DrawerTitle`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `shouldScaleBackground?`: boolean
- `className?`: string
- All vaul props

**Used in**:
- Mobile navigation
- Slide-out panels
- Mobile menus

---

### @components/Form

**Purpose**:
Form component with validation and field management.

**Dependencies**:
- `react-hook-form`
- `@hookform/resolvers`
- `zod`
- `@/lib/utils`

**Exports**:
- `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormDescription`, `FormMessage`, `useFormField`

**Props**:
- `form`: UseFormReturn
- `className?`: string
- All react-hook-form props

**Used in**:
- Form validation
- Data entry forms
- User input handling

---

### @components/HoverCard

**Purpose**:
Hover card component for additional information.

**Dependencies**:
- `@radix-ui/react-hover-card`
- `@/lib/utils`

**Exports**:
- `HoverCard`, `HoverCardTrigger`, `HoverCardContent`

**Props**:
- `openDelay?`: number
- `closeDelay?`: number
- `className?`: string
- All Radix HoverCard props

**Used in**:
- Tooltips
- User previews
- Additional info

---

### @components/InputOTP

**Purpose**:
One-time password input component.

**Dependencies**:
- `input-otp`
- `@/lib/utils`

**Exports**:
- `InputOTP`, `InputOTPGroup`, `InputOTPSlot`, `InputOTPSeparator`

**Props**:
- `value?`: string
- `onChange?`: (value: string) => void
- `maxLength?`: number
- `pattern?`: RegExp
- `className?`: string

**Used in**:
- 2FA codes
- Verification codes
- PIN inputs

---

### @components/Label

**Purpose**:
Form label component with accessibility.

**Dependencies**:
- `@radix-ui/react-label`
- `@/lib/utils`

**Props**:
- `htmlFor?`: string
- `className?`: string
- All Radix Label props

**Used in**:
- Form labels
- Input associations
- Accessibility

---

### @components/Menubar

**Purpose**:
Application menubar component.

**Dependencies**:
- `@radix-ui/react-menubar`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Menubar`, `MenubarTrigger`, `MenubarContent`, `MenubarItem`, `MenubarCheckboxItem`, `MenubarRadioItem`, `MenubarLabel`, `MenubarSeparator`, `MenubarShortcut`, `MenubarGroup`, `MenubarPortal`, `MenubarSub`, `MenubarSubContent`, `MenubarSubTrigger`, `MenubarRadioGroup`

**Props**:
- `className?`: string
- All Radix Menubar props

**Used in**:
- Application menus
- Desktop navigation
- Menu systems

---

### @components/NavigationMenu

**Purpose**:
Navigation menu component with dropdowns.

**Dependencies**:
- `@radix-ui/react-navigation-menu`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `NavigationMenu`, `NavigationMenuList`, `NavigationMenuItem`, `NavigationMenuContent`, `NavigationMenuTrigger`, `NavigationMenuLink`, `NavigationMenuIndicator`, `NavigationMenuViewport`

**Props**:
- `value?`: string
- `onValueChange?`: (value: string) => void
- `orientation?`: 'horizontal' | 'vertical'
- `className?`: string
- All Radix NavigationMenu props

**Used in**:
- Main navigation
- Site menus
- Navigation systems

---

### @components/Pagination

**Purpose**:
Pagination component for data lists.

**Dependencies**:
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Pagination`, `PaginationContent`, `PaginationEllipsis`, `PaginationItem`, `PaginationLink`, `PaginationNext`, `PaginationPrevious`

**Props**:
- `pageCount`: number
- `currentPage?`: number
- `onPageChange?`: (page: number) => void
- `className?`: string

**Used in**:
- Data tables
- Search results
- Content pagination

---

### @components/Popover

**Purpose**:
Popover component for floating content.

**Dependencies**:
- `@radix-ui/react-popover`
- `@/lib/utils`

**Exports**:
- `Popover`, `PopoverTrigger`, `PopoverContent`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `className?`: string
- All Radix Popover props

**Used in**:
- Floating content
- Information overlays
- Quick actions

---

### @components/Progress

**Purpose**:
Progress bar component.

**Dependencies**:
- `@radix-ui/react-progress`
- `@/lib/utils`

**Props**:
- `value?`: number
- `max?`: number
- `className?`: string
- All Radix Progress props

**Used in**:
- Loading indicators
- Progress tracking
- Status bars

---

### @components/RadioGroup

**Purpose**:
Radio button group component.

**Dependencies**:
- `@radix-ui/react-radio-group`
- `@/lib/utils`

**Exports**:
- `RadioGroup`, `RadioGroupItem`

**Props**:
- `value?`: string
- `onValueChange?`: (value: string) => void
- `disabled?`: boolean
- `className?`: string
- All Radix RadioGroup props

**Used in**:
- Form selections
- Option groups
- Single choice inputs

---

### @components/Resizable

**Purpose**:
Resizable panel component.

**Dependencies**:
- `react-resizable-panels`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `ResizablePanelGroup`, `ResizablePanel`, `ResizableHandle`

**Props**:
- `defaultSize?`: number
- `minSize?`: number
- `maxSize?`: number
- `collapsible?`: boolean
- `collapsedSize?`: number
- `className?`: string

**Used in**:
- Split views
- Resizable layouts
- Panel systems

---

### @components/ScrollArea

**Purpose**:
Custom scrollable area component.

**Dependencies**:
- `@radix-ui/react-scroll-area`
- `@/lib/utils`

**Props**:
- `type?`: 'auto' | 'always' | 'scroll' | 'hover'
- `scrollHideDelay?`: number
- `className?`: string
- All Radix ScrollArea props

**Used in**:
- Custom scrollbars
- Scrollable content
- Overflow handling

---

### @components/Section

**Purpose**:
Page section component with consistent spacing.

**Dependencies**:
- `@/lib/utils`

**Props**:
- `className?`: string
- `children?`: ReactNode
- All HTML section attributes

**Used in**:
- Page sections
- Content blocks
- Layout structure

---

### @components/Sheet

**Purpose**:
Slide-out sheet component.

**Dependencies**:
- `@radix-ui/react-dialog`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Sheet`, `SheetTrigger`, `SheetClose`, `SheetContent`, `SheetDescription`, `SheetFooter`, `SheetHeader`, `SheetTitle`

**Props**:
- `open?`: boolean
- `onOpenChange?`: (open: boolean) => void
- `side?`: 'top' | 'right' | 'bottom' | 'left'
- `className?`: string
- All Radix Dialog props

**Used in**:
- Mobile menus
- Slide-out panels
- Side navigation

---

### @components/Sidebar

**Purpose**:
Sidebar navigation component.

**Dependencies**:
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Sidebar`, `SidebarHeader`, `SidebarContent`, `SidebarFooter`, `SidebarGroup`, `SidebarGroupContent`, `SidebarGroupLabel`, `SidebarGroupSeparator`, `SidebarMenu`, `SidebarMenuButton`, `SidebarMenuItem`, `SidebarMenuLabel`, `SidebarMenuSeparator`, `SidebarMenuSub`, `SidebarMenuSubButton`, `SidebarMenuSubContent`, `SidebarMenuSubLabel`, `SidebarMenuSubSeparator`, `SidebarMenuSubTrigger`

**Props**:
- `collapsed?`: boolean
- `collapsible?`: boolean
- `className?`: string

**Used in**:
- Application navigation
- Side navigation
- Collapsible menus

---

### @components/Skeleton

**Purpose**:
Loading skeleton component.

**Dependencies**:
- `@/lib/utils`

**Props**:
- `className?`: string
- All HTML div attributes

**Used in**:
- Loading states
- Content placeholders
- Loading indicators

---

### @components/Slider

**Purpose**:
Range slider component.

**Dependencies**:
- `@radix-ui/react-slider`
- `@/lib/utils`

**Props**:
- `value?`: number[]
- `onValueChange?`: (value: number[]) => void
- `min?`: number
- `max?`: number
- `step?`: number
- `disabled?`: boolean
- `className?`: string
- All Radix Slider props

**Used in**:
- Range selection
- Volume controls
- Price filters

---

### @components/Sonner

**Purpose**:
Toast notification component.

**Dependencies**:
- `sonner`

**Props**:
- `position?`: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center'
- `toastOptions?`: ToastOptions
- `className?`: string

**Used in**:
- Notifications
- Toast messages
- User feedback

---

### @components/Switch

**Purpose**:
Toggle switch component.

**Dependencies**:
- `@radix-ui/react-switch`
- `@/lib/utils`

**Props**:
- `checked?`: boolean
- `onCheckedChange?`: (checked: boolean) => void
- `disabled?`: boolean
- `className?`: string
- All Radix Switch props

**Used in**:
- Toggle switches
- Settings
- Boolean inputs

---

### @components/Table

**Purpose**:
Data table component.

**Dependencies**:
- `@/lib/utils`

**Exports**:
- `Table`, `TableHeader`, `TableBody`, `TableFooter`, `TableHead`, `TableRow`, `TableCell`, `TableCaption`

**Props**:
- `className?`: string
- All HTML table attributes

**Used in**:
- Data tables
- Lists
- Information display

---

### @components/Tabs

**Purpose**:
Tab navigation component.

**Dependencies**:
- `@radix-ui/react-tabs`
- `@/lib/utils`

**Exports**:
- `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`

**Props**:
- `value?`: string
- `onValueChange?`: (value: string) => void
- `defaultValue?`: string
- `orientation?`: 'horizontal' | 'vertical'
- `className?`: string
- All Radix Tabs props

**Used in**:
- Tab navigation
- Content organization
- Multi-panel interfaces

---

### @components/Textarea

**Purpose**:
Multi-line text input component.

**Dependencies**:
- `@/lib/utils`

**Props**:
- `className?`: string
- All HTML textarea attributes

**Used in**:
- Long text input
- Comments
- Descriptions

---

### @components/Toast

**Purpose**:
Toast notification component.

**Dependencies**:
- `@radix-ui/react-toast`
- `@/lib/utils`
- `lucide-react`

**Exports**:
- `Toast`, `ToastAction`, `ToastClose`, `ToastDescription`, `ToastProvider`, `ToastTitle`, `ToastViewport`

**Props**:
- `variant?`: 'default' | 'destructive'
- `className?`: string
- All Radix Toast props

**Used in**:
- Notifications
- User feedback
- Status messages

---

### @components/Toaster

**Purpose**:
Toast container component.

**Dependencies**:
- `@/components/toast`

**Props**:
- `className?`: string

**Used in**:
- Toast management
- Notification system
- User feedback

---

### @components/Toggle

**Purpose**:
Toggle button component.

**Dependencies**:
- `@radix-ui/react-toggle`
- `@/lib/utils`

**Props**:
- `pressed?`: boolean
- `onPressedChange?`: (pressed: boolean) => void
- `disabled?`: boolean
- `className?`: string
- All Radix Toggle props

**Used in**:
- Toggle buttons
- State toggles
- Action buttons

---

### @components/ToggleGroup

**Purpose**:
Toggle button group component.

**Dependencies**:
- `@radix-ui/react-toggle-group`
- `@/lib/utils`

**Props**:
- `type?`: 'single' | 'multiple'
- `value?`: string | string[]
- `onValueChange?`: (value: string | string[]) => void
- `disabled?`: boolean
- `className?`: string
- All Radix ToggleGroup props

**Used in**:
- Filter groups
- Option groups
- Multi-select toggles

---

### @components/Tooltip

**Purpose**:
Tooltip component for additional information.

**Dependencies**:
- `@radix-ui/react-tooltip`
- `@/lib/utils`

**Exports**:
- `Tooltip`, `TooltipTrigger`, `TooltipContent`, `TooltipProvider`

**Props**:
- `delayDuration?`: number
- `skipDelayDuration?`: number
- `className?`: string
- All Radix Tooltip props

**Used in**:
- Help text
- Additional info
- Hover explanations

---

### @components/AspectRatio

**Purpose**:
Aspect ratio container component.

**Dependencies**:
- `@radix-ui/react-aspect-ratio`

**Props**:
- `ratio?`: number
- `className?`: string
- All Radix AspectRatio props

**Used in**:
- Image containers
- Video containers
- Responsive media

---

### @components/Chart

**Purpose**:
Chart component for data visualization.

**Dependencies**:
- `recharts`
- `@/lib/utils`

**Props**:
- `data`: any[]
- `type?`: 'line' | 'bar' | 'area' | 'pie'
- `width?`: number
- `height?`: number
- `className?`: string

**Used in**:
- Data visualization
- Analytics
- Charts and graphs

---

## 🧾 APIs (ReadMe.LLM Format)

````markdown
%%README.LLM id=useToast%%

## 🧭 Library Description

Toast notification system with state management, auto-dismiss, and queue management.

## ✅ Rules

- Always use `useToast` hook for toast management.
- Toast limit is 1 concurrent toast.
- Auto-dismiss after 1000000ms (configurable).
- Use `toast()` function for direct toast creation.

## 🧪 Functions

### useToast(): ToastState

**Returns toast state and management functions.**

```ts
const { toasts, toast, dismiss } = useToast();
```

### toast(props: ToastProps): ToastController

**Creates a new toast notification.**

```ts
const controller = toast({
  title: "Success",
  description: "Operation completed",
  variant: "default"
});
```

### dismiss(toastId?: string): void

**Dismisses specific toast or all toasts.**

```ts
dismiss(); // Dismiss all
dismiss("toast-id"); // Dismiss specific
```

%%END%%
````

````markdown
%%README.LLM id=useAuthDialog%%

## 🧭 Library Description

Authentication dialog management with event-driven architecture and callback support.

## ✅ Rules

- Always use `requireAuth` for protected content.
- Set up event listeners for auth success/failure.
- Clean up listeners automatically.
- Use `showAuthDialog` for manual dialog display.

## 🧪 Functions

### useAuthDialog(): AuthDialogState

**Returns authentication dialog management functions.**

```ts
const { isAuthenticated, showAuthDialog, requireAuth } = useAuthDialog();
```

### requireAuth(message?, onSuccess?, onFailure?): boolean

**Requires authentication with optional callbacks.**

```ts
const isAuth = requireAuth(
  "Please sign in",
  () => console.log("Success"),
  () => console.log("Failed")
);
```

### showAuthDialog(message?: string): void

**Shows authentication dialog with custom message.**

```ts
showAuthDialog("Please sign in to continue");
```

%%END%%
````

````markdown
%%README.LLM id=useCountdown%%

## 🧭 Library Description

Real-time countdown timer with moment.js integration and UTC support.

## ✅ Rules

- Always pass UTC date string.
- Updates every second automatically.
- Returns structured countdown object.
- Handles expired state automatically.

## 🧪 Functions

### useCountdown(targetDate: string | null): CountdownState

**Returns countdown state with time units.**

```ts
const countdown = useCountdown("2024-12-31T23:59:59Z");
// Returns: { days, hours, minutes, seconds, isExpired, totalSeconds }
```

%%END%%
````

````markdown
%%README.LLM id=useDebouncedCallback%%

## 🧭 Library Description

Debounced function execution to optimize performance and reduce API calls.

## ✅ Rules

- Always provide delay in milliseconds.
- Function includes cancel method.
- Automatically cleans up on unmount.
- Preserves function reference stability.

## 🧪 Functions

### useDebouncedCallback<T>(callback: T, delay: number): DebouncedFunction<T>

**Returns debounced version of callback function.**

```ts
const debouncedSearch = useDebouncedCallback(
  (query: string) => searchAPI(query),
  300
);
```

### cancel(): void

**Cancels pending debounced execution.**

```ts
debouncedSearch.cancel();
```

%%END%%
````

````markdown
%%README.LLM id=useLocalStorage%%

## 🧭 Library Description

Enhanced localStorage management with error handling, quota management, and data size limits.

## ✅ Rules

- Always provide initial value.
- Data size limited to 1MB per item.
- Automatic cleanup of old data.
- Graceful fallback on quota errors.

## 🧪 Functions

### useLocalStorage<T>(key: string, initialValue: T): [T, Setter, Remover]

**Returns localStorage value with setter and remover.**

```ts
const [value, setValue, removeValue] = useLocalStorage("key", "default");
```

### setValue(value: T | (val: T) => T): void

**Sets localStorage value with error handling.**

```ts
setValue("new value");
setValue(prev => prev + " updated");
```

### removeValue(): void

**Removes localStorage value and resets to initial.**

```ts
removeValue();
```

%%END%%
````

````markdown
%%README.LLM id=useSessionStorage%%

## 🧭 Library Description

Enhanced sessionStorage management with error handling, quota management, and data size limits.

## ✅ Rules

- Always provide initial value.
- Data size limited to 1MB per item.
- Automatic cleanup of old data.
- Graceful fallback on quota errors.

## 🧪 Functions

### useSessionStorage<T>(key: string, initialValue: T): [T, Setter, Remover]

**Returns sessionStorage value with setter and remover.**

```ts
const [value, setValue, removeValue] = useSessionStorage("key", "default");
```

### setValue(value: T | (val: T) => T): void

**Sets sessionStorage value with error handling.**

```ts
setValue("new value");
setValue(prev => prev + " updated");
```

### removeValue(): void

**Removes sessionStorage value and resets to initial.**

```ts
removeValue();
```

%%END%%
````

````markdown
%%README.LLM id=useMobile%%

## 🧭 Library Description

Responsive design hook for mobile detection using matchMedia API.

## ✅ Rules

- Uses 768px breakpoint for mobile detection.
- Updates automatically on window resize.
- Returns boolean for mobile state.
- Handles SSR gracefully.

## 🧪 Functions

### useIsMobile(): boolean

**Returns true if screen width is below 768px.**

```ts
const isMobile = useIsMobile();
```

%%END%%
````

````markdown
%%README.LLM id=useDebugTools%%

## 🧭 Library Description

React DevTools integration for debugging component state and values.

## ✅ Rules

- Only use in development mode.
- Accepts objects, arrays, or primitives.
- Provides formatted debug labels.
- Handles circular references gracefully.

## 🧪 Functions

### useDebugTools(values: DebugValue, prefix?: string): void

**Registers values for React DevTools debugging.**

```ts
useDebugTools({ count, name }, "UserState");
```

%%END%%
````

````markdown
%%README.LLM id=Hero%%

## 🧭 Library Description

Landing page hero section with customizable actions, backgrounds, and animations.

## ✅ Rules

- Always provide title prop.
- Use semantic HTML structure.
- Supports multiple background types.
- Includes built-in animations.

## 🧪 Props

### title: string (required)

**Main hero heading text.**

```tsx
<Hero title="Welcome to Our Platform" />
```

### subtitle?: string

**Optional subtitle text.**

```tsx
<Hero title="Main Title" subtitle="Supporting text" />
```

### description?: string

**Optional description paragraph.**

```tsx
<Hero 
  title="Title" 
  description="Detailed explanation of the value proposition"
/>
```

### primaryAction?: ActionConfig

**Primary call-to-action button.**

```tsx
<Hero 
  title="Title"
  primaryAction={{
    label: "Get Started",
    href: "/signup",
    variant: "default"
  }}
/>
```

### secondaryAction?: ActionConfig

**Secondary call-to-action button.**

```tsx
<Hero 
  title="Title"
  secondaryAction={{
    label: "Learn More",
    href: "/docs",
    variant: "outline"
  }}
/>
```

### background?: 'gradient' | 'solid' | 'image' | 'dark'

**Background style variant.**

```tsx
<Hero title="Title" background="gradient" />
```

%%END%%
````

````markdown
%%README.LLM id=FeatureSection%%

## 🧭 Library Description

Feature showcase section with grid layout, card-based presentation, and customizable columns.

## ✅ Rules

- Always provide title and features array.
- Features array cannot be empty.
- Supports 1-4 column layouts.
- Includes hover animations.

## 🧪 Props

### title: string (required)

**Section heading text.**

```tsx
<FeatureSection title="Our Features" features={[]} />
```

### subtitle?: string

**Optional section subtitle.**

```tsx
<FeatureSection 
  title="Features" 
  subtitle="Discover what makes us special"
  features={[]}
/>
```

### features: Feature[] (required)

**Array of feature objects.**

```tsx
<FeatureSection 
  title="Features"
  features={[
    {
      icon: <Icon />,
      title: "Feature Name",
      description: "Feature description",
      gradient: "bg-gradient-to-r from-blue-500 to-purple-500"
    }
  ]}
/>
```

### columns?: 1 | 2 | 3 | 4

**Number of columns in grid layout.**

```tsx
<FeatureSection title="Features" features={[]} columns={2} />
```

### background?: 'dark' | 'card' | 'gradient'

**Background style variant.**

```tsx
<FeatureSection title="Features" features={[]} background="gradient" />
```

%%END%%
````

````markdown
%%README.LLM id=Button%%

## 🧭 Library Description

Versatile button component with multiple variants, sizes, and link support.

## ✅ Rules

- Use semantic variants for different purposes.
- Support both button and link modes.
- Include proper accessibility attributes.
- Handle loading states gracefully.

## 🧪 Props

### variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'

**Button style variant.**

```tsx
<Button variant="destructive">Delete</Button>
```

### size?: 'default' | 'sm' | 'lg' | 'icon'

**Button size variant.**

```tsx
<Button size="lg">Large Button</Button>
```

### asChild?: boolean

**Render as child component (for links).**

```tsx
<Button asChild>
  <Link href="/page">Link Button</Link>
</Button>
```

### disabled?: boolean

**Disable button interaction.**

```tsx
<Button disabled>Disabled Button</Button>
```

%%END%%
````

---

## 🔁 Flows

### Toast Notification Flow

1. User triggers action → calls `toast()` function.
2. Toast added to state → renders in UI.
3. Auto-dismiss timer starts → removes after delay.
4. User can manually dismiss → calls `dismiss()`.

**Modules**:
- `@hooks/useToast`
- `@components/toast`
- `@components/toaster`

---

### Authentication Dialog Flow

1. User accesses protected content → `requireAuth()` called.
2. Check authentication status → show dialog if needed.
3. User completes auth → event published.
4. Success callback executed → content unlocked.

**Modules**:
- `@hooks/useAuthDialog`
- `@hooks/useEventsBus`
- `@events/dialogEvents`

---

### Responsive Design Flow

1. Component mounts → `useMobile()` initializes.
2. MatchMedia listener set up → monitors screen size.
3. Window resize detected → state updates.
4. Component re-renders → responsive layout applied.

**Modules**:
- `@hooks/useMobile`
- Responsive components
- Layout components

---

### Form Persistence Flow

1. User inputs data → `useLocalStorage` updates.
2. Data saved to localStorage → with error handling.
3. Page refresh → data restored from storage.
4. Form submission → data cleared from storage.

**Modules**:
- `@hooks/useLocalStorage`
- Form components
- Validation hooks

---

### Landing Page Flow

1. Page loads → Hero section renders.
2. User scrolls → FeatureSection animates in.
3. User clicks CTA → navigation occurs.
4. Toast notification → confirms action.

**Modules**:
- `@blocks/Hero`
- `@blocks/FeatureSection`
- `@components/Button`
- `@hooks/useToast`

---

## 🧠 Notes

- Terms like "RAG" and "LLM-first" are explained inline where used.
- Avoid external references or multi-file links.
- All content in this single `.md` is optimized for token-friendly usage.
- Component variants follow consistent naming patterns.
- Hooks include proper cleanup and error handling.
- Blocks are designed for landing page use cases. 