# DjangoCFG UI v1.0.0

Comprehensive React UI library with 50+ components built with Radix UI, Tailwind CSS v4, and TypeScript

Total Components: 104

## 📋 Quick Reference - Available Components

### Interactive (8)
Interactive Button, Interactive Badge, Interactive Alert, Interactive Progress, Interactive Color Box, Toggle, ToggleGroup, Command

### Forms (18)
Button, Input, Label, Checkbox, RadioGroup, Select, Textarea, Switch, Slider, Combobox, MultiSelect, MultiSelectPro, InputOTP, PhoneInput, DownloadButton, Field, ButtonGroup, InputGroup

### Layout (9)
Card, Separator, Skeleton, AspectRatio, ScrollArea, Resizable, Sticky, Section, Sidebar

### Navigation (6)
Tabs, Breadcrumb, BreadcrumbNavigation, NavigationMenu, Pagination, Menubar

### Overlay (9)
Dialog, Sheet, Drawer, Popover, Tooltip, DropdownMenu, ContextMenu, AlertDialog, HoverCard

### Feedback (7)
Toast, Alert, Progress, Badge, Avatar, Empty, Spinner

### Data Display (9)
Table, Accordion, Collapsible, Calendar, Carousel, ChartContainer, Pagination, SSRPagination, StaticPagination

### Specialized (10)
Sidebar, ImageWithFallback, ButtonGroup, Empty, Spinner, Kbd, TokenIcon, Toaster (Sonner), InputGroup, Item

### Developer Tools (6)
JsonTree, PrettyCode, Mermaid, LottiePlayer, JsonSchemaForm, OpenapiViewer

### Blocks (7)
Hero, SuperHero, FeatureSection, CTASection, NewsletterSection, StatsSection, TestimonialSection

### Hooks (10)
useMediaQuery, useTheme, useCopy, useCountdown, useDebounce, useIsMobile, useLocalStorage, useSessionStorage, useEventListener, useImageLoader

### App Layouts (1)
Error Layout

### Authentication (1)
Auth Dialog

### Snippets (3)
Breadcrumbs, Video Player, Contact Form

---

## 🎨 Tailwind CSS v4.0 Guidelines

### Key Changes
- CSS-First Configuration: Theme is now defined using CSS custom properties in an @theme block instead of JavaScript
- New Import Syntax: Use @import "tailwindcss" instead of @tailwind directives
- Simplified PostCSS Setup: Use @tailwindcss/postcss plugin
- Performance Improvements: 10x faster build times, significantly smaller CSS bundles
- Modern Browser Support: Optimized for Safari 16.4+, Chrome 111+, Firefox 128+

### Best Practices
- Use standard Tailwind classes only: py-16 sm:py-20 md:py-24 lg:py-32
- Responsive patterns: px-4 sm:px-6 lg:px-8
- Container pattern: container max-w-7xl mx-auto
- IMPORTANT: Arbitrary values like h-[80px], z-[100] may NOT work in v4 - define tokens in @theme instead
- For fixed sizes: Use inline styles style={{ width: '80px', height: '80px' }} - always reliable
- Spacing utilities (h-20, p-4, etc.) require --spacing-* variables defined in @theme block
- Z-index utilities (z-50, z-100) require --z-* variables defined in @theme block
- OPACITY MODIFIERS: bg-background/80 does NOT work with HSL colors in v4! Use inline styles: style={{ backgroundColor: 'hsl(var(--background) / 0.8)' }}
- Border opacity: border-border/30 does NOT work - use style={{ borderColor: 'hsl(var(--border) / 0.3)' }}
- Import order is critical: theme variables MUST come before @import 'tailwindcss'
- Use aspect-square for maintaining 1:1 ratio (circles, squares)
- Use overflow-hidden with rounded-full for perfect circles
- Avoid custom utilities like: section-padding, animate-*, shadow-brand
- Mobile-first approach with breakpoints: sm: (640px), md: (768px), lg: (1024px), xl: (1280px)
- Use CSS variables: var(--color-primary), var(--font-family-sans)

### Examples

#### CSS-First Configuration
```tsx
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-family-sans: ui-sans-serif, system-ui, sans-serif;
  --spacing-20: 5rem; /* Required for h-20, w-20 to work */
}
```

#### Opacity with HSL Colors (BROKEN in v4)
```tsx
/* ❌ BROKEN - does not work in Tailwind v4 */
<nav className="bg-background/80 border-border/30">

/* ✅ WORKING - use inline styles for opacity */
<nav
  className="sticky top-0 z-100 backdrop-blur-xl"
  style={{
    backgroundColor: 'hsl(var(--background) / 0.8)',
    borderColor: 'hsl(var(--border) / 0.3)'
  }}
>
```

#### Fixed Sizes with Inline Styles
```tsx
<Avatar
  className="aspect-square rounded-full overflow-hidden"
  style={{ width: '80px', height: '80px' }}
>
  <AvatarImage src={avatar} alt="User" />
</Avatar>
```

---

## Interactive (8)

Interactive demos with live controls. Try changing props in real-time!

### Interactive Button

Interactive Button demo with live controls. Change variant, size, loading state, and more in the right panel.

**Import:**
```tsx
import { Button } from '@djangocfg/ui';
```

**Example:**
```tsx
// Use fixture hooks for interactive demos
import { useValue, useSelect, useBoolean } from '@djangocfg/demo';

function InteractiveButtonPreview() {
  const [label] = useValue('label', { defaultValue: 'Click me' });
  const [variant] = useSelect('variant', {
    options: ['default', 'secondary', 'destructive'],
    defaultValue: 'default',
  });
  const [disabled] = useBoolean('disabled', { defaultValue: false });

  return (
    <Button variant={variant} disabled={disabled}>
      {label}
    </Button>
  );
}
```

**Tags:** button, interactive, controls, live

---

### Interactive Badge

Interactive Badge demo with live variant and text controls.

**Import:**
```tsx
import { Badge } from '@djangocfg/ui';
```

**Example:**
```tsx
const [text] = useValue('text', { defaultValue: 'Badge' });
const [variant] = useSelect('variant', {
  options: ['default', 'secondary', 'destructive', 'outline'],
});

<Badge variant={variant}>{text}</Badge>
```

**Tags:** badge, interactive, controls

---

### Interactive Alert

Interactive Alert demo with customizable title, description, and variant.

**Import:**
```tsx
import { Alert, AlertTitle, AlertDescription } from '@djangocfg/ui';
```

**Example:**
```tsx
const [title] = useValue('title', { defaultValue: 'Heads up!' });
const [description] = useValue('description', { defaultValue: 'Important message.' });
const [variant] = useSelect('variant', { options: ['default', 'destructive'] });

<Alert variant={variant}>
  <AlertTitle>{title}</AlertTitle>
  <AlertDescription>{description}</AlertDescription>
</Alert>
```

**Tags:** alert, interactive, feedback

---

### Interactive Progress

Interactive Progress bar with slider control for the value.

**Import:**
```tsx
import { Progress } from '@djangocfg/ui';
```

**Example:**
```tsx
const [value] = useNumber('value', {
  defaultValue: 60,
  min: 0,
  max: 100,
  step: 5,
});

<Progress value={value} />
```

**Tags:** progress, interactive, number

---

### Interactive Color Box

Interactive demo showing color picker and number controls.

**Import:**
```tsx
// Custom component example
```

**Example:**
```tsx
const [bgColor] = useColor('backgroundColor', { defaultValue: '#3b82f6' });
const [borderRadius] = useNumber('borderRadius', { defaultValue: 8, max: 50 });
const [size] = useNumber('size', { defaultValue: 100, min: 50, max: 200 });

<div
  style={{
    backgroundColor: bgColor,
    borderRadius: `${borderRadius}px`,
    width: `${size}px`,
    height: `${size}px`,
  }}
/>
```

**Tags:** color, interactive, custom, number

---

### Toggle

Two-state toggle button

**Import:**
```tsx
import { Toggle } from '@djangocfg/ui';
```

**Example:**
```tsx
<Toggle aria-label="Toggle bold">
  <Bold className="h-4 w-4" />
</Toggle>
```

**Tags:** toggle, button, switch, state

---

### ToggleGroup

Group of toggle buttons with single or multiple selection

**Import:**
```tsx
import { ToggleGroup, ToggleGroupItem } from '@djangocfg/ui';
```

**Example:**
```tsx
<ToggleGroup type="multiple">
  <ToggleGroupItem value="bold" aria-label="Toggle bold">
    <Bold className="h-4 w-4" />
  </ToggleGroupItem>
  <ToggleGroupItem value="italic" aria-label="Toggle italic">
    <Italic className="h-4 w-4" />
  </ToggleGroupItem>
</ToggleGroup>
```

**Tags:** toggle, group, toolbar, selection

---

### Command

Command palette / search interface (cmdk)

**Import:**
```tsx
import { Command, CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '@djangocfg/ui';
```

**Example:**
```tsx
<Command className="rounded-lg border shadow-md">
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search Emoji</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

**Tags:** command, palette, search, cmdk, spotlight

---

## Forms (18)

Input fields, buttons, checkboxes, selects, and form validation

### Button

Interactive button with multiple variants, sizes, and loading state

**Import:**
```tsx
import { Button, ButtonLink } from '@djangocfg/ui';
```

**Example:**
```tsx
// Variants
<Button variant="default">Click me</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>

// Loading state
<Button loading={true}>Saving...</Button>

// ButtonLink for navigation
<ButtonLink href="/dashboard">Go to Dashboard</ButtonLink>
```

**Props:**
- `variant`: `'default' | 'destructive' | 'outline' | 'ghost' | 'secondary' | 'link'` - Visual variant
- `size`: `'default' | 'sm' | 'lg' | 'icon'` - Button size
- `loading`: `boolean` - Show loading spinner
- `disabled`: `boolean` - Disable interaction

**Tags:** button, action, click, submit, link

---

### Input

Text input field with validation support

**Import:**
```tsx
import { Input } from '@djangocfg/ui';
```

**Example:**
```tsx
<Input type="text" placeholder="Enter text..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" disabled />
```

**Tags:** input, text, field, form

---

### Label

Accessible label component for form inputs

**Import:**
```tsx
import { Label } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="space-y-2">
  <Label htmlFor="email">Email address</Label>
  <Input id="email" type="email" placeholder="Enter your email" />
</div>
```

**Tags:** label, form, accessibility

---

### Checkbox

Checkbox with label support

**Import:**
```tsx
import { Checkbox, Label } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex items-center gap-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Accept terms and conditions</Label>
</div>
```

**Tags:** checkbox, toggle, form, boolean

---

### RadioGroup

Radio button group for single selection

**Import:**
```tsx
import { RadioGroup, RadioGroupItem, Label } from '@djangocfg/ui';
```

**Example:**
```tsx
<RadioGroup defaultValue="option1">
  <div className="flex items-center gap-2">
    <RadioGroupItem value="option1" id="opt1" />
    <Label htmlFor="opt1">Option 1</Label>
  </div>
  <div className="flex items-center gap-2">
    <RadioGroupItem value="option2" id="opt2" />
    <Label htmlFor="opt2">Option 2</Label>
  </div>
</RadioGroup>
```

**Tags:** radio, selection, group, form

---

### Select

Dropdown select component

**Import:**
```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@djangocfg/ui';
```

**Example:**
```tsx
<Select>
  <SelectTrigger className="w-[200px]">
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
    <SelectItem value="2">Option 2</SelectItem>
    <SelectItem value="3">Option 3</SelectItem>
  </SelectContent>
</Select>
```

**Tags:** select, dropdown, form, choice

---

### Textarea

Multi-line text input

**Import:**
```tsx
import { Textarea } from '@djangocfg/ui';
```

**Example:**
```tsx
<Textarea placeholder="Enter your message..." rows={4} />
```

**Tags:** textarea, multiline, text, form

---

### Switch

Toggle switch component

**Import:**
```tsx
import { Switch, Label } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex items-center gap-2">
  <Switch id="notifications" />
  <Label htmlFor="notifications">Enable notifications</Label>
</div>
```

**Tags:** switch, toggle, boolean, form

---

### Slider

Range slider input

**Import:**
```tsx
import { Slider } from '@djangocfg/ui';
```

**Example:**
```tsx
<Slider defaultValue={[50]} max={100} step={1} className="w-[200px]" />
```

**Tags:** slider, range, number, form

---

### Combobox

Searchable dropdown with autocomplete

**Import:**
```tsx
import { Combobox } from '@djangocfg/ui';
```

**Example:**
```tsx
<Combobox
  options={[
    { value: "javascript", label: "JavaScript" },
    { value: "typescript", label: "TypeScript" },
    { value: "python", label: "Python" },
  ]}
  placeholder="Select language..."
  searchPlaceholder="Search..."
  emptyText="No language found."
/>
```

**Tags:** combobox, autocomplete, search, select

---

### MultiSelect

Multi-select dropdown with badges and search

**Import:**
```tsx
import { MultiSelect } from '@djangocfg/ui';
```

**Example:**
```tsx
<MultiSelect
  options={[
    { value: "react", label: "React" },
    { value: "vue", label: "Vue" },
    { value: "angular", label: "Angular" },
  ]}
  placeholder="Select frameworks..."
  maxDisplay={2}
/>
```

**Tags:** multiselect, multiple, tags, badges

---

### MultiSelectPro

Advanced multi-select with animations, variants, and grouped options

**Import:**
```tsx
import { MultiSelectPro } from '@djangocfg/ui';
```

**Example:**
```tsx
<MultiSelectPro
  options={[
    { value: "react", label: "React" },
    { value: "vue", label: "Vue.js" },
  ]}
  onValueChange={setSelected}
  defaultValue={selected}
  variant="secondary"
  maxCount={3}
/>
```

**Tags:** multiselect, pro, animations, grouped

---

### InputOTP

One-time password input component

**Import:**
```tsx
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@djangocfg/ui';
```

**Example:**
```tsx
<InputOTP maxLength={6}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
    <InputOTPSlot index={2} />
    <InputOTPSlot index={3} />
    <InputOTPSlot index={4} />
    <InputOTPSlot index={5} />
  </InputOTPGroup>
</InputOTP>
```

**Tags:** otp, verification, code, pin

---

### PhoneInput

International phone number input with country selector

**Import:**
```tsx
import { PhoneInput } from '@djangocfg/ui';
```

**Example:**
```tsx
<PhoneInput
  defaultCountry="US"
  placeholder="Enter phone number"
/>
```

**Tags:** phone, telephone, international, country

---

### DownloadButton

Button with download functionality and status indicators

**Import:**
```tsx
import { DownloadButton } from '@djangocfg/ui';
```

**Example:**
```tsx
<DownloadButton
  url="/api/files/report.pdf"
  filename="monthly-report.pdf"
>
  Download Report
</DownloadButton>
```

**Tags:** download, file, export, button

---

### Field

Field wrapper component for form inputs with label, description, and error handling

**Import:**
```tsx
import { Field, FieldLabel, FieldDescription, FieldError, FieldGroup, FieldContent } from '@djangocfg/ui';
```

**Example:**
```tsx
<FieldGroup>
  <Field>
    <FieldLabel>Email</FieldLabel>
    <FieldContent>
      <Input type="email" placeholder="Enter email" />
      <FieldDescription>We'll never share your email.</FieldDescription>
    </FieldContent>
  </Field>
  <Field>
    <FieldLabel>Password</FieldLabel>
    <FieldContent>
      <Input type="password" />
      <FieldError>Password is required</FieldError>
    </FieldContent>
  </Field>
</FieldGroup>
```

**Props:**
- `orientation`: `'vertical' | 'horizontal' | 'responsive'` - Field layout orientation

**Tags:** field, form, label, validation, error

---

### ButtonGroup

Group of buttons with connected styling

**Import:**
```tsx
import { ButtonGroup, Button } from '@djangocfg/ui';
```

**Example:**
```tsx
<ButtonGroup>
  <Button variant="outline">Left</Button>
  <Button variant="outline">Center</Button>
  <Button variant="outline">Right</Button>
</ButtonGroup>
```

**Tags:** button, group, connected, toolbar

---

### InputGroup

Input with prefix/suffix addons

**Import:**
```tsx
import { InputGroup, InputGroupAddon, InputGroupInput } from '@djangocfg/ui';
```

**Example:**
```tsx
<InputGroup>
  <InputGroupAddon>$</InputGroupAddon>
  <InputGroupInput type="number" placeholder="0.00" />
  <InputGroupAddon align="inline-end">USD</InputGroupAddon>
</InputGroup>
```

**Tags:** input, addon, prefix, suffix

---

## Layout (9)

Cards, separators, skeletons, and structural components

### Card

Container for related content and actions

**Import:**
```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@djangocfg/ui';
```

**Example:**
```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card Content</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

**Tags:** card, container, content, panel

---

### Separator

Visual separator between content sections

**Import:**
```tsx
import { Separator } from '@djangocfg/ui';
```

**Example:**
```tsx
<div>
  <div className="space-y-1">
    <h4 className="font-medium">Section One</h4>
    <p className="text-sm text-muted-foreground">Description here.</p>
  </div>
  <Separator className="my-4" />
  <div className="space-y-1">
    <h4 className="font-medium">Section Two</h4>
    <p className="text-sm text-muted-foreground">Description here.</p>
  </div>
</div>
```

**Tags:** separator, divider, line, hr

---

### Skeleton

Loading placeholder for content

**Import:**
```tsx
import { Skeleton } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex items-center space-x-4">
  <Skeleton className="h-12 w-12 rounded-full" />
  <div className="space-y-2">
    <Skeleton className="h-4 w-[250px]" />
    <Skeleton className="h-4 w-[200px]" />
  </div>
</div>
```

**Tags:** skeleton, loading, placeholder, shimmer

---

### AspectRatio

Maintain aspect ratio for responsive images

**Import:**
```tsx
import { AspectRatio } from '@djangocfg/ui';
```

**Example:**
```tsx
<AspectRatio ratio={16 / 9}>
  <img
    src="/image.jpg"
    alt="Image"
    className="rounded-md object-cover w-full h-full"
  />
</AspectRatio>
```

**Props:**
- `ratio`: `number` - Aspect ratio (e.g., 16/9)

**Tags:** aspect, ratio, image, responsive

---

### ScrollArea

Custom scrollable area with styled scrollbars

**Import:**
```tsx
import { ScrollArea } from '@djangocfg/ui';
```

**Example:**
```tsx
<ScrollArea className="h-[200px] w-[350px] rounded-md border p-4">
  <div className="space-y-4">
    {items.map((item) => (
      <div key={item}>{item}</div>
    ))}
  </div>
</ScrollArea>
```

**Tags:** scroll, overflow, scrollbar, container

---

### Resizable

Resizable panel layout with drag handles

**Import:**
```tsx
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@djangocfg/ui';
```

**Example:**
```tsx
<ResizablePanelGroup direction="horizontal" className="min-h-[200px]">
  <ResizablePanel defaultSize={50}>
    <div className="p-4">Left panel</div>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={50}>
    <div className="p-4">Right panel</div>
  </ResizablePanel>
</ResizablePanelGroup>
```

**Tags:** resizable, panel, split, drag

---

### Sticky

Sticky positioned element wrapper

**Import:**
```tsx
import { Sticky } from '@djangocfg/ui';
```

**Example:**
```tsx
<Sticky offsetTop={0} className="z-50">
  <header className="bg-background border-b p-4">
    Sticky Header
  </header>
</Sticky>
```

**Tags:** sticky, fixed, position, header

---

### Section

Content section with optional header

**Import:**
```tsx
import { Section, SectionHeader } from '@djangocfg/ui';
```

**Example:**
```tsx
<Section>
  <SectionHeader
    title="Section Title"
    subtitle="Optional subtitle text"
  />
  <div>Section content goes here</div>
</Section>
```

**Tags:** section, content, header, layout

---

### Sidebar

Full-featured sidebar navigation component with collapsible menu, groups, and mobile support

**Import:**
```tsx
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarTrigger, useSidebar } from '@djangocfg/ui';
```

**Example:**
```tsx
<SidebarProvider>
  <Sidebar>
    <SidebarHeader>
      <h2>App Name</h2>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Menu</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <a href="/dashboard">Dashboard</a>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <a href="/settings">Settings</a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter>
      <p>Footer content</p>
    </SidebarFooter>
  </Sidebar>
  <main>
    <SidebarTrigger />
    <div>Main content</div>
  </main>
</SidebarProvider>
```

**Tags:** sidebar, navigation, menu, drawer, collapsible

**Related:** NavigationMenu, Sheet

---

## Navigation (6)

Menus, breadcrumbs, tabs, and pagination

### Tabs

Tab-based navigation between content sections

**Import:**
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    Account settings content
  </TabsContent>
  <TabsContent value="password">
    Password settings content
  </TabsContent>
</Tabs>
```

**Tags:** tabs, navigation, switch, sections

---

### Breadcrumb

Breadcrumb navigation for page hierarchy

**Import:**
```tsx
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@djangocfg/ui';
```

**Example:**
```tsx
<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/docs">Docs</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Current</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

**Tags:** breadcrumb, navigation, hierarchy, path

---

### BreadcrumbNavigation

Simplified breadcrumb component with items array

**Import:**
```tsx
import { BreadcrumbNavigation } from '@djangocfg/ui';
```

**Example:**
```tsx
<BreadcrumbNavigation
  items={[
    { label: 'Home', href: '/' },
    { label: 'Products', href: '/products' },
    { label: 'Electronics', href: '/products/electronics' },
    { label: 'Phones' }, // No href = current page
  ]}
/>
```

**Tags:** breadcrumb, navigation, simple, array

---

### NavigationMenu

Main navigation menu with dropdowns

**Import:**
```tsx
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<NavigationMenu>
  <NavigationMenuList>
    <NavigationMenuItem>
      <NavigationMenuTrigger>Getting Started</NavigationMenuTrigger>
      <NavigationMenuContent>
        <ul className="grid gap-3 p-4 w-[400px]">
          <li>
            <NavigationMenuLink href="/docs">
              Documentation
            </NavigationMenuLink>
          </li>
        </ul>
      </NavigationMenuContent>
    </NavigationMenuItem>
  </NavigationMenuList>
</NavigationMenu>
```

**Tags:** navigation, menu, header, dropdown

---

### Pagination

Pagination controls for lists

**Import:**
```tsx
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@djangocfg/ui';
```

**Example:**
```tsx
<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#" isActive>2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">3</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

**Tags:** pagination, pages, navigation, list

---

### Menubar

Horizontal menu bar with dropdowns

**Import:**
```tsx
import { Menubar, MenubarContent, MenubarItem, MenubarMenu, MenubarSeparator, MenubarTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Menubar>
  <MenubarMenu>
    <MenubarTrigger>File</MenubarTrigger>
    <MenubarContent>
      <MenubarItem>New</MenubarItem>
      <MenubarItem>Open</MenubarItem>
      <MenubarSeparator />
      <MenubarItem>Save</MenubarItem>
    </MenubarContent>
  </MenubarMenu>
</Menubar>
```

**Tags:** menubar, menu, toolbar, application

---

## Overlay (9)

Dialogs, sheets, popovers, tooltips, and dropdowns

### Dialog

Modal dialog for focused interactions

**Import:**
```tsx
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>
        Dialog description goes here.
      </DialogDescription>
    </DialogHeader>
    <div className="py-4">Content here</div>
    <DialogFooter>
      <Button type="submit">Save</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**Tags:** dialog, modal, popup, overlay

---

### Sheet

Slide-out panel from screen edge

**Import:**
```tsx
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open Sheet</Button>
  </SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Sheet Title</SheetTitle>
      <SheetDescription>Sheet description</SheetDescription>
    </SheetHeader>
    <div className="py-4">Content here</div>
  </SheetContent>
</Sheet>
```

**Tags:** sheet, sidebar, panel

---

### Drawer

Mobile-friendly drawer with swipe gestures (vaul)

**Import:**
```tsx
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle, DrawerTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Drawer>
  <DrawerTrigger asChild>
    <Button variant="outline">Open Drawer</Button>
  </DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Drawer Title</DrawerTitle>
      <DrawerDescription>Drawer description</DrawerDescription>
    </DrawerHeader>
    <div className="p-4">Content here</div>
  </DrawerContent>
</Drawer>
```

**Tags:** drawer, mobile, swipe, vaul, bottom-sheet

---

### Popover

Floating content triggered by click

**Import:**
```tsx
import { Popover, PopoverContent, PopoverTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">Open Popover</Button>
  </PopoverTrigger>
  <PopoverContent>
    <p>Popover content here</p>
  </PopoverContent>
</Popover>
```

**Tags:** popover, popup, dropdown, float

---

### Tooltip

Hover tooltip for additional information

**Import:**
```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Tooltip content</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

**Tags:** tooltip, hover, hint, help

---

### DropdownMenu

Accessible dropdown menu

**Import:**
```tsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open Menu</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
    <DropdownMenuItem>Logout</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

**Tags:** dropdown, menu, actions, options

---

### ContextMenu

Right-click context menu

**Import:**
```tsx
import { ContextMenu, ContextMenuContent, ContextMenuItem, ContextMenuTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<ContextMenu>
  <ContextMenuTrigger className="flex h-[150px] w-[300px] items-center justify-center rounded-md border border-dashed">
    Right click here
  </ContextMenuTrigger>
  <ContextMenuContent>
    <ContextMenuItem>Edit</ContextMenuItem>
    <ContextMenuItem>Duplicate</ContextMenuItem>
    <ContextMenuItem>Delete</ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>
```

**Tags:** context, rightclick, menu

---

### AlertDialog

Confirmation dialog for destructive actions

**Import:**
```tsx
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<AlertDialog>
  <AlertDialogTrigger asChild>
    <Button variant="destructive">Delete</Button>
  </AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

**Tags:** alert, confirm, dialog, destructive

---

### HoverCard

Preview card on hover

**Import:**
```tsx
import { HoverCard, HoverCardContent, HoverCardTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<HoverCard>
  <HoverCardTrigger asChild>
    <Button variant="link">@username</Button>
  </HoverCardTrigger>
  <HoverCardContent>
    <p>User information preview</p>
  </HoverCardContent>
</HoverCard>
```

**Tags:** hover, card, preview, popup

---

## Feedback (7)

Toasts, alerts, progress bars, and status indicators

### Toast

Toast notifications for user feedback

**Import:**
```tsx
import { useToast, Toaster } from '@djangocfg/ui';
```

**Example:**
```tsx
function Component() {
  const { toast } = useToast();

  return (
    <Button
      onClick={() => {
        toast({
          title: "Success!",
          description: "Your changes have been saved.",
        });
      }}
    >
      Show Toast
    </Button>
  );
}
```

**Tags:** toast, notification, alert, message

**Related:** Alert, Toaster

---

### Alert

Alert messages for important information

**Import:**
```tsx
import { Alert, AlertDescription, AlertTitle } from '@djangocfg/ui';
```

**Example:**
```tsx
<Alert>
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components to your app using the cli.
  </AlertDescription>
</Alert>

<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired. Please log in again.
  </AlertDescription>
</Alert>
```

**Props:**
- `variant`: `'default' | 'destructive'` - Alert variant

**Tags:** alert, warning, info, error

---

### Progress

Progress bar for showing completion status

**Import:**
```tsx
import { Progress } from '@djangocfg/ui';
```

**Example:**
```tsx
<Progress value={25} />
<Progress value={50} />
<Progress value={75} />
```

**Props:**
- `value`: `number` - Progress percentage (0-100)

**Tags:** progress, loading, percentage, status

---

### Badge

Status badges for labels and categories

**Import:**
```tsx
import { Badge } from '@djangocfg/ui';
```

**Example:**
```tsx
<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
```

**Props:**
- `variant`: `'default' | 'secondary' | 'destructive' | 'outline'` - Badge variant

**Tags:** badge, tag, label, status

---

### Avatar

User avatar with fallback support

**Import:**
```tsx
import { Avatar, AvatarFallback, AvatarImage } from '@djangocfg/ui';
```

**Example:**
```tsx
<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
```

**Tags:** avatar, user, profile, image

---

### Empty

Empty state component for showing when there is no data

**Import:**
```tsx
import { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyContent, EmptyMedia } from '@djangocfg/ui';
```

**Example:**
```tsx
<Empty>
  <EmptyHeader>
    <EmptyMedia variant="icon">
      <Inbox className="size-6" />
    </EmptyMedia>
    <EmptyTitle>No messages</EmptyTitle>
    <EmptyDescription>
      You don't have any messages yet.
    </EmptyDescription>
  </EmptyHeader>
  <EmptyContent>
    <Button>Create message</Button>
  </EmptyContent>
</Empty>
```

**Props:**
- `variant`: `'default' | 'icon'` - Media variant for icon styling

**Tags:** empty, state, no-data, placeholder

---

### Spinner

Loading spinner animation

**Import:**
```tsx
import { Spinner } from '@djangocfg/ui';
```

**Example:**
```tsx
<Spinner />
<Spinner className="size-8" />
```

**Tags:** spinner, loading, animation, progress

---

## Data Display (9)

Tables, accordions, and data visualization

### Table

Data table with headers and rows

**Import:**
```tsx
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from '@djangocfg/ui';
```

**Example:**
```tsx
<Table>
  <TableCaption>A list of your recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>INV001</TableCell>
      <TableCell>Paid</TableCell>
      <TableCell>$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

**Tags:** table, data, grid, list

---

### Accordion

Collapsible content sections

**Import:**
```tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>
      Yes. It comes with default styles that match.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

**Tags:** accordion, collapse, expand, faq

---

### Collapsible

Simple collapsible content block

**Import:**
```tsx
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@djangocfg/ui';
```

**Example:**
```tsx
<Collapsible>
  <CollapsibleTrigger asChild>
    <Button variant="ghost">
      Toggle content
      <ChevronsUpDown className="h-4 w-4" />
    </Button>
  </CollapsibleTrigger>
  <CollapsibleContent>
    <p>Hidden content here</p>
  </CollapsibleContent>
</Collapsible>
```

**Tags:** collapsible, toggle, expand, hide

---

### Calendar

Date picker calendar component

**Import:**
```tsx
import { Calendar } from '@djangocfg/ui';
```

**Example:**
```tsx
const [date, setDate] = useState<Date | undefined>(new Date());

<Calendar
  mode="single"
  selected={date}
  onSelect={setDate}
  className="rounded-md border"
/>
```

**Tags:** calendar, date, picker, datepicker

---

### Carousel

Touch-friendly carousel/slider component

**Import:**
```tsx
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@djangocfg/ui';
```

**Example:**
```tsx
<Carousel className="w-full max-w-xs">
  <CarouselContent>
    {items.map((_, index) => (
      <CarouselItem key={index}>
        <Card>
          <CardContent className="flex aspect-square items-center justify-center p-6">
            <span className="text-4xl font-semibold">{index + 1}</span>
          </CardContent>
        </Card>
      </CarouselItem>
    ))}
  </CarouselContent>
  <CarouselPrevious />
  <CarouselNext />
</Carousel>
```

**Tags:** carousel, slider, gallery, swipe

---

### ChartContainer

Wrapper for Recharts components with theme-aware styling

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@djangocfg/ui';
```

**Example:**
```tsx
const chartConfig = {
  desktop: { label: "Desktop", color: "hsl(var(--chart-1))" },
  mobile: { label: "Mobile", color: "hsl(var(--chart-2))" },
};

<ChartContainer config={chartConfig} className="h-[200px]">
  <BarChart data={data}>
    <XAxis dataKey="month" />
    <YAxis />
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="desktop" fill="var(--color-desktop)" />
    <Bar dataKey="mobile" fill="var(--color-mobile)" />
  </BarChart>
</ChartContainer>
```

**Props:**
- `config`: `ChartConfig` (required) - Chart configuration with colors and labels
- `children`: `ReactNode` (required) - Recharts chart components

**Tags:** chart, recharts, visualization, graph

**Related:** Progress

---

### Pagination

Basic pagination component with navigation controls

**Import:**
```tsx
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@djangocfg/ui';
```

**Example:**
```tsx
<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#" isActive>2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">3</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

**Tags:** pagination, navigation, pages

**Related:** SSRPagination, StaticPagination

---

### SSRPagination

Server-side rendered pagination with URL-based navigation

**Import:**
```tsx
import { SSRPagination } from '@djangocfg/ui';
```

**Example:**
```tsx
<SSRPagination
  currentPage={1}
  totalPages={10}
  totalItems={100}
  itemsPerPage={10}
  hasNextPage={true}
  hasPreviousPage={false}
  showInfo={true}
  maxVisiblePages={7}
/>
```

**Props:**
- `currentPage`: `number` (required)
- `totalPages`: `number` (required)
- `totalItems`: `number` (required)
- `itemsPerPage`: `number` (required)
- `hasNextPage`: `boolean` (required)
- `hasPreviousPage`: `boolean` (required)

**Tags:** pagination, ssr, navigation

**Related:** Pagination, StaticPagination

---

### StaticPagination

Client-side pagination for DRF paginated responses

**Import:**
```tsx
import { StaticPagination, useDRFPagination } from '@djangocfg/ui';
```

**Example:**
```tsx
const pagination = useDRFPagination();
const { data } = useMyAPI(pagination.params);

<StaticPagination
  data={data}
  onPageChange={pagination.setPage}
  showInfo={true}
/>
```

**Props:**
- `data`: `DRFPaginatedResponse` - DRF paginated response
- `onPageChange`: `(page: number) => void` (required)
- `showInfo`: `boolean`

**Tags:** pagination, drf, django, client-side

**Related:** Pagination, SSRPagination

---

## Specialized (10)

Advanced components like sidebar and image handling

### Sidebar

Full-featured sidebar navigation with collapsible groups, icons, and Next.js router support

**Import:**
```tsx
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@djangocfg/ui';
```

**Example:**
```tsx
<Sidebar>
  <SidebarContent>
    <SidebarGroup>
      <SidebarGroupLabel>Main</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton href="/" isActive tooltip="Dashboard">
              <HomeIcon />
              <span>Dashboard</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>
</Sidebar>
```

**Tags:** navigation, menu, layout

**Related:** NavigationMenu, Menubar

---

### ImageWithFallback

Enhanced image component with loading states and fallback support

**Import:**
```tsx
import { ImageWithFallback } from '@djangocfg/ui';
```

**Example:**
```tsx
<ImageWithFallback
  src="/images/example.jpg"
  alt="Example image"
  width={300}
  height={200}
  fallbackSrc="/images/placeholder.jpg"
  className="rounded-md"
/>
```

**Tags:** image, media, fallback

**Related:** Avatar

---

### ButtonGroup

Group buttons together with shared borders

**Import:**
```tsx
import { ButtonGroup, Button } from '@djangocfg/ui';
```

**Example:**
```tsx
<ButtonGroup orientation="horizontal">
  <Button variant="outline">Left</Button>
  <Button variant="outline">Center</Button>
  <Button variant="outline">Right</Button>
</ButtonGroup>
```

**Props:**
- `orientation`: `'horizontal' | 'vertical'`
- `children`: `ReactNode` (required)

**Tags:** button, group, toolbar

**Related:** Button

---

### Empty

Empty state component for no data scenarios

**Import:**
```tsx
import {
  Empty,
  EmptyHeader,
  EmptyTitle,
  EmptyDescription,
  EmptyContent,
  EmptyMedia,
} from '@djangocfg/ui';
```

**Example:**
```tsx
<Empty>
  <EmptyHeader>
    <EmptyMedia variant="icon">
      <InboxIcon />
    </EmptyMedia>
    <EmptyTitle>No results found</EmptyTitle>
    <EmptyDescription>
      Try adjusting your search or filter.
    </EmptyDescription>
  </EmptyHeader>
  <EmptyContent>
    <Button>Clear filters</Button>
  </EmptyContent>
</Empty>
```

**Tags:** empty, state, placeholder

---

### Spinner

Loading spinner indicator

**Import:**
```tsx
import { Spinner } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex gap-4 items-center">
  <Spinner />
  <Spinner className="size-6" />
  <Spinner className="size-8" />
</div>
```

**Props:**
- `className`: `string` - Custom size via size-* classes

**Tags:** loading, spinner, indicator

**Related:** Progress, Skeleton

---

### Kbd

Keyboard key display component

**Import:**
```tsx
import { Kbd } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex gap-2 items-center">
  <span>Press</span>
  <Kbd>⌘</Kbd>
  <Kbd>K</Kbd>
  <span>to open</span>
</div>
```

**Tags:** keyboard, shortcut, key

---

### TokenIcon

Cryptocurrency token icon component

**Import:**
```tsx
import { TokenIcon } from '@djangocfg/ui';
```

**Example:**
```tsx
<div className="flex gap-4">
  <TokenIcon symbol="btc" size={32} />
  <TokenIcon symbol="eth" size={32} />
  <TokenIcon symbol="usdt" size={32} />
</div>
```

**Props:**
- `symbol`: `string` (required) - Token symbol (btc, eth, etc.)
- `size`: `number` - Icon size in pixels

**Tags:** crypto, token, icon, currency

---

### Toaster (Sonner)

Toast notifications powered by Sonner library

**Import:**
```tsx
import { Toaster } from '@djangocfg/ui';
import { toast } from 'sonner';
```

**Example:**
```tsx
// Add Toaster to your app layout
<Toaster />

// Then use toast anywhere in your app
toast.success('Operation completed!');
toast.error('Something went wrong');
toast.info('New message received');
toast.promise(fetchData(), {
  loading: 'Loading...',
  success: 'Data loaded!',
  error: 'Failed to load',
});
```

**Tags:** toast, notification, sonner

**Related:** Alert

---

### InputGroup

Enhanced input with prefix/suffix addons

**Import:**
```tsx
import { InputGroup, Input } from '@djangocfg/ui';
```

**Example:**
```tsx
<InputGroup>
  <InputGroupAddon align="inline-start">
    <SearchIcon className="size-4" />
  </InputGroupAddon>
  <Input placeholder="Search..." />
  <InputGroupAddon align="inline-end">
    <Kbd>⌘K</Kbd>
  </InputGroupAddon>
</InputGroup>
```

**Tags:** input, group, addon

**Related:** Input

---

### Item

List item component with variants and layouts

**Import:**
```tsx
import { Item, ItemGroup } from '@djangocfg/ui';
```

**Example:**
```tsx
<ItemGroup>
  <Item variant="outline" size="default">
    <ItemIcon>
      <FileIcon />
    </ItemIcon>
    <ItemContent>
      <ItemTitle>Document.pdf</ItemTitle>
      <ItemDescription>Updated 2 hours ago</ItemDescription>
    </ItemContent>
    <ItemAction>
      <Button variant="ghost" size="sm">View</Button>
    </ItemAction>
  </Item>
</ItemGroup>
```

**Props:**
- `variant`: `'default' | 'outline' | 'muted'`
- `size`: `'default' | 'sm' | 'lg'`

**Tags:** list, item, row

**Related:** Card, Table

---

## Developer Tools (6)

JSON viewer, code highlighting, Mermaid diagrams

### JsonTree

Interactive JSON tree viewer with expand/collapse, search, and export functionality

**Import:**
```tsx
import { JsonTree } from '@djangocfg/ui';
```

**Example:**
```tsx
<JsonTree
  title="User Data"
  data={{
    user: {
      id: 1,
      name: "John Doe",
      profile: {
        bio: "Software engineer",
        interests: ["coding", "music"]
      }
    }
  }}
  config={{
    maxAutoExpandDepth: 2,
    showCollectionInfo: true,
    showExpandControls: true,
    showActionButtons: true,
  }}
/>
```

**Props:**
- `data`: `object | array` (required) - JSON data to display
- `title`: `string` - Header title
- `config`: `JsonTreeConfig` - Configuration options

**Tags:** json, tree, viewer, debug

**Related:** PrettyCode

---

### PrettyCode

Syntax-highlighted code display with automatic language detection and theme support

**Import:**
```tsx
import { PrettyCode } from '@djangocfg/ui';
```

**Example:**
```tsx
// Code as string
<PrettyCode
  data={pythonCode}
  language="python"
/>

// JSON object (auto-formatted)
<PrettyCode
  data={{ user: "John", age: 30 }}
  language="json"
/>

// Inline code
<PrettyCode
  data="const x = 42;"
  language="javascript"
  inline
/>
```

**Props:**
- `data`: `string | object` (required) - Code to display
- `language`: `string` - Language for syntax highlighting
- `inline`: `boolean` - Inline code display

**Tags:** code, syntax, highlight, prism

**Related:** JsonTree

---

### Mermaid

Interactive Mermaid diagram renderer with fullscreen view and theme support

**Import:**
```tsx
import { Mermaid } from '@djangocfg/ui';
```

**Example:**
```tsx
<Mermaid
  chart={`
    graph TD
      A[Start] --> B{Is it?}
      B -->|Yes| C[OK]
      C --> D[Rethink]
      D --> B
      B -->|No| E[End]
  `}
/>

// Sequence diagram
<Mermaid
  chart={`
    sequenceDiagram
      participant A as Alice
      participant B as Bob
      A->>B: Hello Bob!
      B->>A: Hello Alice!
  `}
/>
```

**Props:**
- `chart`: `string` (required) - Mermaid diagram code

**Tags:** diagram, mermaid, flowchart, chart

---

### LottiePlayer

Lottie animation player with size presets and playback controls

**Import:**
```tsx
import { LottiePlayer } from '@djangocfg/ui';
```

**Example:**
```tsx
<LottiePlayer
  src="https://lottie.host/embed/animation.json"
  size="md"
  autoplay
  loop
/>

// Custom size and speed
<LottiePlayer
  src={animationData}
  width={300}
  height={300}
  speed={1.5}
/>
```

**Props:**
- `src`: `string | object` (required) - Animation URL or JSON data
- `size`: `'sm' | 'md' | 'lg'` - Size preset
- `autoplay`: `boolean` - Auto-start animation
- `loop`: `boolean` - Loop animation
- `speed`: `number` - Playback speed

**Tags:** animation, lottie, motion

---

### JsonSchemaForm

Dynamic form generator from JSON Schema with validation and custom widgets

**Import:**
```tsx
import { JsonSchemaForm } from '@djangocfg/ui';
```

**Example:**
```tsx
const schema = {
  type: "object",
  properties: {
    name: { type: "string", title: "Name" },
    email: { type: "string", format: "email", title: "Email" },
    age: { type: "number", title: "Age", minimum: 0 }
  },
  required: ["name", "email"]
};

<JsonSchemaForm
  schema={schema}
  onSubmit={(data) => console.log(data)}
/>
```

**Props:**
- `schema`: `JSONSchema7` (required) - JSON Schema object
- `onSubmit`: `(data) => void` - Submit handler
- `widgets`: `object` - Custom widget components

**Tags:** form, json-schema, generator, dynamic

**Related:** Form

---

### OpenapiViewer

Interactive OpenAPI/Swagger documentation viewer with API playground

**Import:**
```tsx
import { OpenapiViewer } from '@djangocfg/ui';
```

**Example:**
```tsx
<OpenapiViewer
  spec="https://api.example.com/openapi.json"
  config={{
    baseUrl: "https://api.example.com",
    headers: { "Authorization": "Bearer token" },
  }}
/>

// Or with inline spec
<OpenapiViewer
  spec={openapiSpec}
/>
```

**Props:**
- `spec`: `string | object` (required) - OpenAPI spec URL or object
- `config`: `PlaygroundConfig` - Playground configuration

**Tags:** openapi, swagger, api, documentation

---

## Blocks (7)

Pre-built landing page sections

### Hero

Hero section with title, description, and CTAs

**Import:**
```tsx
import { Hero } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<Hero
  title="Build Your Next Project"
  description="The best way to create modern web applications with React and TypeScript"
  primaryAction={{ label: "Get Started", href: "/docs" }}
  secondaryAction={{ label: "View Demo", href: "/demo" }}
/>
```

**Props:**
- `title`: `string` (required)
- `description`: `string`
- `primaryAction`: `{ label: string; href: string }`
- `secondaryAction`: `{ label: string; href: string }`

**Tags:** hero, landing, section

**Related:** SuperHero, CTASection

---

### SuperHero

Enhanced hero with badge, gradient title, features, and stats

**Import:**
```tsx
import { SuperHero } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<SuperHero
  badge={{ icon: <Sparkles />, text: "New in v2.0" }}
  title="Next-Generation"
  titleGradient="Development Platform"
  subtitle="Build faster with our comprehensive UI library"
  features={[
    { icon: <span>⚛️</span>, text: "React 19" },
    { icon: <span>📘</span>, text: "TypeScript" },
    { icon: <span>🎨</span>, text: "Tailwind CSS 4" },
  ]}
  primaryAction={{ label: "Start Building", href: "/start" }}
  stats={[
    { number: "56+", label: "Components" },
    { number: "7", label: "Blocks" },
  ]}
  backgroundVariant="waves"
/>
```

**Props:**
- `badge`: `{ icon: ReactNode; text: string }`
- `title`: `string` (required)
- `titleGradient`: `string`
- `features`: `Array<{ icon: ReactNode; text: string }>`
- `stats`: `Array<{ number: string; label: string }>`
- `backgroundVariant`: `'none' | 'waves' | 'dots' | 'grid'`

**Tags:** hero, landing, gradient, animated

**Related:** Hero, StatsSection

---

### FeatureSection

Grid of features with icons and descriptions

**Import:**
```tsx
import { FeatureSection } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<FeatureSection
  title="Everything You Need"
  subtitle="All the tools to build modern applications"
  features={[
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Lightning Fast",
      description: "Optimized for performance"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure",
      description: "Built with security in mind"
    }
  ]}
/>
```

**Props:**
- `title`: `string` (required)
- `subtitle`: `string`
- `features`: `Array<{ icon: ReactNode; title: string; description: string }>` (required)

**Tags:** features, grid, landing

**Related:** Hero, StatsSection

---

### CTASection

Call-to-action section to drive conversions

**Import:**
```tsx
import { CTASection } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<CTASection
  title="Ready to Get Started?"
  subtitle="Join thousands of developers building amazing products"
  primaryCTA={{ label: "Start Free Trial", href: "/signup" }}
  secondaryCTA={{ label: "Contact Sales", href: "/contact" }}
/>
```

**Props:**
- `title`: `string` (required)
- `subtitle`: `string`
- `primaryCTA`: `{ label: string; href: string }` (required)
- `secondaryCTA`: `{ label: string; href: string }`

**Tags:** cta, call-to-action, landing

**Related:** Hero, NewsletterSection

---

### NewsletterSection

Email capture section for newsletters

**Import:**
```tsx
import { NewsletterSection } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<NewsletterSection
  title="Stay Updated"
  description="Get the latest news delivered to your inbox"
  placeholder="Enter your email"
  buttonText="Subscribe"
  onSubmit={(email) => console.log(email)}
/>
```

**Props:**
- `title`: `string` (required)
- `description`: `string`
- `placeholder`: `string`
- `buttonText`: `string`
- `onSubmit`: `(email: string) => void` (required)

**Tags:** newsletter, email, subscription, landing

**Related:** CTASection

---

### StatsSection

Display key metrics and statistics

**Import:**
```tsx
import { StatsSection } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<StatsSection
  title="Our Impact"
  stats={[
    { icon: <Users className="w-6 h-6" />, number: "10K+", label: "Active Users" },
    { icon: <Building2 className="w-6 h-6" />, number: "500+", label: "Companies" },
    { icon: <TrendingUp className="w-6 h-6" />, number: "99.9%", label: "Uptime" },
  ]}
/>
```

**Props:**
- `title`: `string`
- `stats`: `Array<{ icon?: ReactNode; number: string; label: string }>` (required)

**Tags:** stats, metrics, numbers, landing

**Related:** FeatureSection

---

### TestimonialSection

Customer testimonials and reviews

**Import:**
```tsx
import { TestimonialSection } from '@djangocfg/ui/blocks';
```

**Example:**
```tsx
<TestimonialSection
  title="What Our Customers Say"
  testimonials={[{
    content: "This product changed how we work!",
    author: {
      name: "John Doe",
      title: "CEO",
      company: "Company",
      avatar: "/avatar.jpg"
    }
  }]}
/>
```

**Props:**
- `title`: `string`
- `testimonials`: `Array<{ content: string; author: { name: string; title: string; company: string; avatar?: string } }>` (required)

**Tags:** testimonials, reviews, social-proof, landing

**Related:** StatsSection

---

## Hooks (10)

Custom React hooks for common functionality

### useMediaQuery

Responsive media query hook for conditional rendering

**Import:**
```tsx
import { useMediaQuery } from '@djangocfg/ui';
```

**Example:**
```tsx
const isMobile = useMediaQuery('(max-width: 768px)');
const isDesktop = useMediaQuery('(min-width: 1024px)');
const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');

return isMobile ? <MobileView /> : <DesktopView />;
```

**Props:**
- `query`: `string` (required) - CSS media query string

**Tags:** responsive, media-query, viewport

**Related:** useIsMobile

---

### useTheme

Theme management hook for light/dark mode

**Import:**
```tsx
import { useTheme } from '@djangocfg/ui';
```

**Example:**
```tsx
const theme = useTheme(); // Returns 'light' | 'dark'

// Check current theme
if (theme === 'dark') {
  // Dark mode specific logic
}

// Toggle theme manually
document.documentElement.classList.toggle('dark');
```

**Tags:** theme, dark-mode, light-mode

---

### useCopy

Copy to clipboard hook with async support

**Import:**
```tsx
import { useCopy } from '@djangocfg/ui';
```

**Example:**
```tsx
const { copyToClipboard } = useCopy();
const [copied, setCopied] = useState(false);

const handleCopy = async () => {
  await copyToClipboard('text to copy');
  setCopied(true);
  setTimeout(() => setCopied(false), 2000);
};

return (
  <Button onClick={handleCopy}>
    {copied ? 'Copied!' : 'Copy'}
  </Button>
);
```

**Tags:** clipboard, copy, paste

**Related:** Kbd

---

### useCountdown

Countdown timer hook with days, hours, minutes, seconds

**Import:**
```tsx
import { useCountdown } from '@djangocfg/ui';
```

**Example:**
```tsx
const targetDate = new Date('2025-12-31').toISOString();
const { days, hours, minutes, seconds, isExpired } = useCountdown(targetDate);

return (
  <div>
    {isExpired ? (
      <span>Timer expired!</span>
    ) : (
      <span>
        {days}d {hours}h {minutes}m {seconds}s
      </span>
    )}
  </div>
);
```

**Props:**
- `targetDate`: `string` (required) - ISO date string for countdown target

**Tags:** countdown, timer, time

---

### useDebounce

Debounce value changes to reduce API calls and improve performance

**Import:**
```tsx
import { useDebounce } from '@djangocfg/ui';
```

**Example:**
```tsx
const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 300); // Default 300ms

useEffect(() => {
  if (debouncedSearch) {
    // API call only fires 300ms after user stops typing
    fetchResults(debouncedSearch);
  }
}, [debouncedSearch]);

return (
  <Input
    value={search}
    onChange={(e) => setSearch(e.target.value)}
    placeholder="Search..."
  />
);
```

**Props:**
- `value`: `T` (required) - Value to debounce
- `delay`: `number` - Delay in milliseconds

**Tags:** debounce, performance, search

**Related:** Input

---

### useIsMobile

Check if device is mobile (viewport < 768px)

**Import:**
```tsx
import { useIsMobile } from '@djangocfg/ui';
```

**Example:**
```tsx
const isMobile = useIsMobile(); // Boolean

return isMobile ? <MobileMenu /> : <DesktopMenu />;

// Or conditionally render
{isMobile && <MobileNavigation />}
{!isMobile && <DesktopNavigation />}
```

**Tags:** mobile, responsive, viewport

**Related:** useMediaQuery

---

### useLocalStorage

Persist state to localStorage with automatic serialization

**Import:**
```tsx
import { useLocalStorage } from '@djangocfg/ui';
```

**Example:**
```tsx
const [settings, setSettings] = useLocalStorage('user-settings', {
  theme: 'dark',
  notifications: true
});

// Updates both state and localStorage
setSettings({ ...settings, theme: 'light' });
```

**Props:**
- `key`: `string` (required) - localStorage key
- `initialValue`: `T` (required) - Initial value if key not found

**Tags:** storage, persist, state

**Related:** useSessionStorage

---

### useSessionStorage

Persist state to sessionStorage (cleared on tab close)

**Import:**
```tsx
import { useSessionStorage } from '@djangocfg/ui';
```

**Example:**
```tsx
const [cart, setCart] = useSessionStorage('shopping-cart', []);

// Add item
setCart([...cart, newItem]);
```

**Props:**
- `key`: `string` (required) - sessionStorage key
- `initialValue`: `T` (required) - Initial value if key not found

**Tags:** storage, session, state

**Related:** useLocalStorage

---

### useEventListener

Subscribe to custom events with type-safe event bus

**Import:**
```tsx
import { useEventListener, events } from '@djangocfg/ui';
```

**Example:**
```tsx
// Listen to custom events
useEventListener('user-login', (data) => {
  console.log('User logged in:', data);
});

// Emit events from anywhere
events.emit('user-login', { userId: '123' });
```

**Props:**
- `eventName`: `string` (required) - Name of the event to listen for
- `handler`: `(data: T) => void` (required) - Event handler callback

**Tags:** events, pubsub, communication

---

### useImageLoader

Preload images and track loading state

**Import:**
```tsx
import { useImageLoader } from '@djangocfg/ui';
```

**Example:**
```tsx
const { loaded, error } = useImageLoader('/path/to/image.jpg');

return (
  <div>
    {!loaded && <Skeleton className="h-48 w-full" />}
    {loaded && <img src="/path/to/image.jpg" />}
    {error && <span>Failed to load image</span>}
  </div>
);
```

**Props:**
- `src`: `string` (required) - Image URL to preload

**Tags:** image, loading, preload

**Related:** ImageWithFallback, Skeleton

---

## App Layouts (1)

Application layout templates

### Error Layout

Universal error page layout with auto-configured content for common HTTP errors.

**Import:**
```tsx
import { ErrorLayout } from '@djangocfg/layouts';
```

**Example:**
```tsx
import { ErrorLayout } from '@djangocfg/layouts';

// Auto-configure from error code
<ErrorLayout code="404" />

// Custom content
<ErrorLayout
  code="500"
  title="Oops!"
  description="Something went wrong."
  supportEmail="help@example.com"
/>

// In Next.js pages/404.tsx
export default function NotFound() {
  return <ErrorLayout code="404" />;
}
```

**Tags:** layout, error, 404, 500, 403, page

---

## Authentication (1)

Login, signup, and auth components

### Auth Dialog

Authentication prompt dialog triggered via events when user needs to sign in.

**Import:**
```tsx
import { AuthDialog, openAuthDialog } from '@djangocfg/layouts';
```

**Example:**
```tsx
import { AuthDialog, openAuthDialog } from '@djangocfg/layouts';

// Add to layout
<AuthDialog authPath="/auth" />

// Trigger from anywhere
openAuthDialog({ message: 'Sign in to continue' });
```

**Tags:** auth, dialog, login, signin

---

## Snippets (3)

Ready-to-use code snippets

### Breadcrumbs

Navigation breadcrumbs with automatic path generation or custom items.

**Import:**
```tsx
import Breadcrumbs from '@djangocfg/layouts';
```

**Example:**
```tsx
import Breadcrumbs from '@djangocfg/layouts';

// Auto-generate from current path
<Breadcrumbs />

// Or provide custom items
<Breadcrumbs
  items={[
    { path: '/', label: 'Home', isActive: false },
    { path: '/products', label: 'Products', isActive: true },
  ]}
/>
```

**Tags:** navigation, breadcrumbs, path

---

### Video Player

Professional video player with Vidstack. Supports YouTube, Vimeo, MP4, HLS.

**Import:**
```tsx
import { VideoPlayer } from '@djangocfg/layouts';
```

**Example:**
```tsx
import { VideoPlayer } from '@djangocfg/layouts';

<VideoPlayer
  source={{
    url: 'https://youtube.com/watch?v=...',
    title: 'My Video',
    poster: '/thumbnail.jpg',
  }}
  theme="modern"
  controls
  onPlay={() => console.log('Playing')}
/>
```

**Tags:** video, player, youtube, vimeo, media

---

### Contact Form

Contact form with validation, localStorage draft saving, and API integration.

**Import:**
```tsx
import { ContactForm } from '@djangocfg/layouts';
```

**Example:**
```tsx
import { ContactForm } from '@djangocfg/layouts';

<ContactForm
  apiUrl="https://api.example.com"
  texts={{
    title: 'Get in Touch',
    submitText: 'Send Message',
  }}
  onSuccess={(result) => console.log('Sent!', result)}
/>
```

**Tags:** form, contact, lead, email

---

