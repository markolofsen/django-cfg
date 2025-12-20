# DjangoCFG UI v1.0.0

Comprehensive React UI library with 50+ components built with Radix UI, Tailwind CSS v4, and TypeScript

Total Components: 133

## 📋 Quick Reference - Available Components

### Interactive (3)
Command, Toggle, ToggleGroup

### Forms (23)
Button, ButtonGroup, ButtonLink, Checkbox, Combobox, CopyButton, CopyField, DownloadButton, Field, Form, Input, InputGroup, OTPInput, Label, MultiSelect, MultiSelectPro, MultiSelectProAsync, PhoneInput, RadioGroup, Select, Slider, Switch, Textarea

### Layout (14)
AspectRatio, Card, ImageWithFallback, Item, Kbd, Portal, Preloader, Resizable, ScrollArea, Section, Separator, Sidebar, Skeleton, Sticky

### Navigation (6)
Breadcrumb, BreadcrumbNavigation, Menubar, NavigationMenu, Pagination, Tabs

### Overlay (9)
AlertDialog, ContextMenu, Dialog, Drawer, DropdownMenu, HoverCard, Popover, Sheet, Tooltip

### Feedback (4)
Alert, Badge, Progress, Toast

### Data Display (9)
Accordion, Calendar, Carousel, Collapsible, DatePicker, DateRangePicker, SSRPagination, StaticPagination, Table

### Specialized (4)
Empty, OgImage, Spinner, Toaster

### Developer Tools (11)
Interactive JsonSchemaForm, JsonTree, LottiePlayer, MarkdownMessage with Mermaid, MarkdownMessage, Mermaid, OgImageTemplate, OpenapiViewer, PrettyCode, UseQueryParams, VideoPlayer

### Blocks (8)
CTASection, FeatureSection, Hero, NewsletterSection, SplitHero, StatsSection, SuperHero, TestimonialSection

### Hooks (15)
useBrowserDetect, useCopy, useCountdown, useDebounce, useDebouncedCallback, useDebugTools, useDeviceDetect, useEventListener, useHotkey, useImageLoader, useIsMobile, useLocalStorage, useMediaQuery, useSessionStorage, useThemeContext

### Charts (7)
Area Chart, Bar Chart, ChartContainer, Donut Chart, Line Chart, Pie Chart, Radial Bar Chart

### Animations (8)
Aurora Borealis, Color Schemes, Floating Orbs, Geometric Flow, AnimatedBackground, Liquid Gradient, Mesh Gradient, Spotlight

### Layouts (10)
AIChatWidget, AdminLayout, Analytics, AppLayout, AuthDialog, AuthLayout, BaseApp, PrivateLayout, PublicFooter, PublicLayout

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

## Interactive (3)

Interactive demos with live controls. Try changing props in real-time!

### Command

Command palette / search interface (cmdk)

**Import:**
```tsx
import { Command, CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from '@djangocfg/ui-nextjs';
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

### Toggle

Two-state toggle button

**Import:**
```tsx
import { Toggle } from '@djangocfg/ui-nextjs';
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
import { ToggleGroup, ToggleGroupItem } from '@djangocfg/ui-nextjs';
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

## Forms (23)

Input fields, buttons, checkboxes, selects, and form validation

### Button

Interactive button with multiple variants, sizes, and loading state

**Import:**
```tsx
import { Button, ButtonLink } from '@djangocfg/ui-nextjs';
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

**Tags:** button, action, click, submit, link

---

### ButtonGroup

Group of buttons with connected styling

**Import:**
```tsx
import { ButtonGroup, Button } from '@djangocfg/ui-nextjs';
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

### ButtonLink

Link styled as a button with all button variants

**Import:**
```tsx
import { ButtonLink } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Navigation link styled as button
<ButtonLink href="/dashboard">Go to Dashboard</ButtonLink>

// With variants
<ButtonLink href="/docs" variant="outline">Documentation</ButtonLink>
<ButtonLink href="/settings" variant="ghost">Settings</ButtonLink>

// External link
<ButtonLink href="https://github.com" target="_blank">
  GitHub
</ButtonLink>
```

**Tags:** button, link, navigation, anchor, href

---

### Checkbox

Checkbox with label support

**Import:**
```tsx
import { Checkbox, Label } from '@djangocfg/ui-nextjs';
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

### Combobox

Searchable dropdown with autocomplete

**Import:**
```tsx
import { Combobox } from '@djangocfg/ui-nextjs';
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

### CopyButton

Button to copy text to clipboard

**Import:**
```tsx
import { CopyButton } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<CopyButton value="Text to copy" />
```

**Tags:** copy, clipboard, button

---

### CopyField

Field with copy button to copy value to clipboard

**Import:**
```tsx
import { CopyField } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<CopyField label="API Key" value="sk-1234567890abcdef" mono={true} />
```

**Tags:** copy, clipboard, field

---

### DownloadButton

Button with download functionality and status indicators

**Import:**
```tsx
import { DownloadButton } from '@djangocfg/ui-nextjs';
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
import { Field, FieldLabel, FieldDescription, FieldError, FieldGroup, FieldContent } from '@djangocfg/ui-nextjs';
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

**Tags:** field, form, label, validation, error

---

### Form

Form component built on react-hook-form with accessible form controls and validation

**Import:**
```tsx
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@djangocfg/ui-nextjs';
import { useForm } from 'react-hook-form';
```

**Example:**
```tsx
const form = useForm({
  defaultValues: {
    username: '',
    email: '',
  },
});

<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
    <FormField
      control={form.control}
      name="username"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Username</FormLabel>
          <FormControl>
            <Input placeholder="johndoe" {...field} />
          </FormControl>
          <FormDescription>
            This is your public display name.
          </FormDescription>
          <FormMessage />
        </FormItem>
      )}
    />
    <Button type="submit">Submit</Button>
  </form>
</Form>
```

**Tags:** form, validation, react-hook-form, zod

---

### Input

Text input field with validation support

**Import:**
```tsx
import { Input } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Input type="text" placeholder="Enter text..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" disabled />
```

**Tags:** input, text, field, form

---

### InputGroup

Input with prefix/suffix addons

**Import:**
```tsx
import { InputGroup, InputGroupAddon, InputGroupInput } from '@djangocfg/ui-nextjs';
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

### OTPInput

Smart one-time password input with validation, paste handling, and auto-submit

**Import:**
```tsx
import { OTPInput } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Basic numeric OTP
<OTPInput
  length={6}
  value={code}
  onChange={setCode}
/>

// With separator and alphanumeric
<OTPInput
  length={6}
  validationMode="alphanumeric"
  showSeparator
  separatorIndex={3}
  value={code}
  onChange={setCode}
/>

// Custom validation (hex only)
<OTPInput
  length={4}
  validationMode="custom"
  customValidator={(char) => /[A-F0-9]/i.test(char)}
  value={code}
  onChange={setCode}
/>

// Auto-submit when complete
<OTPInput
  length={6}
  autoSubmit
  onComplete={(code) => verifyCode(code)}
  value={code}
  onChange={setCode}
/>
```

**Tags:** otp, verification, code, pin, validation, smart, paste

---

### Label

Accessible label component for form inputs

**Import:**
```tsx
import { Label } from '@djangocfg/ui-nextjs';
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

### MultiSelect

Multi-select dropdown with badges and search

**Import:**
```tsx
import { MultiSelect } from '@djangocfg/ui-nextjs';
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
import { MultiSelectPro } from '@djangocfg/ui-nextjs';
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

### MultiSelectProAsync

Async multi-select with debounced search and remote data loading

**Import:**
```tsx
import { MultiSelectProAsync } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const searchUsers = async (query: string) => {
  const response = await fetch(`/api/users?search=${query}`);
  return response.json();
};

<MultiSelectProAsync
  loadOptions={searchUsers}
  onValueChange={setSelected}
  defaultValue={[]}
  placeholder="Search users..."
  debounceMs={300}
/>
```

**Tags:** multiselect, async, search, remote, api

---

### PhoneInput

International phone number input with country selector

**Import:**
```tsx
import { PhoneInput } from '@djangocfg/ui-nextjs';
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

### RadioGroup

Radio button group for single selection

**Import:**
```tsx
import { RadioGroup, RadioGroupItem, Label } from '@djangocfg/ui-nextjs';
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@djangocfg/ui-nextjs';
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

### Slider

Range slider input

**Import:**
```tsx
import { Slider } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Slider defaultValue={[50]} max={100} step={1} className="w-[200px]" />
```

**Tags:** slider, range, number, form

---

### Switch

Toggle switch component

**Import:**
```tsx
import { Switch, Label } from '@djangocfg/ui-nextjs';
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

### Textarea

Multi-line text input

**Import:**
```tsx
import { Textarea } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Textarea placeholder="Enter your message..." rows={4} />
```

**Tags:** textarea, multiline, text, form

---

## Layout (14)

Cards, separators, skeletons, and structural components

### AspectRatio

Maintain aspect ratio for responsive images

**Import:**
```tsx
import { AspectRatio } from '@djangocfg/ui-nextjs';
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

**Tags:** aspect, ratio, image, responsive

---

### Card

Container for related content and actions

**Import:**
```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@djangocfg/ui-nextjs';
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

### ImageWithFallback

Image component with automatic fallback icons when image fails to load

**Import:**
```tsx
import { ImageWithFallback } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Basic usage with default car icon fallback
<ImageWithFallback
  src="/car-image.jpg"
  alt="Car image"
  className="w-24 h-24 rounded-lg"
/>

// With specific fallback icon
<ImageWithFallback
  src="/user-avatar.jpg"
  fallbackIcon="user"
  alt="User avatar"
  className="w-16 h-16 rounded-full"
/>

// With custom fallback content
<ImageWithFallback
  src="/product.jpg"
  fallbackContent={<div className="bg-muted p-4">No image</div>}
  alt="Product"
/>

// Available fallback icons: 'car' | 'image' | 'user' | 'package' | 'location'
```

**Tags:** image, fallback, error, placeholder, loading

---

### Item

Flexible list item component with media, content, and actions

**Import:**
```tsx
import { Item, ItemMedia, ItemContent, ItemTitle, ItemDescription, ItemActions, ItemGroup, ItemSeparator } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<ItemGroup>
  <Item>
    <ItemMedia variant="icon">
      <FileText className="size-4" />
    </ItemMedia>
    <ItemContent>
      <ItemTitle>Document Title</ItemTitle>
      <ItemDescription>Description of the document</ItemDescription>
    </ItemContent>
    <ItemActions>
      <Button variant="ghost" size="sm">Edit</Button>
    </ItemActions>
  </Item>
  <ItemSeparator />
  <Item variant="muted">
    <ItemMedia variant="image">
      <img src="/avatar.jpg" alt="User" />
    </ItemMedia>
    <ItemContent>
      <ItemTitle>User Name <Badge>New</Badge></ItemTitle>
      <ItemDescription>user@example.com</ItemDescription>
    </ItemContent>
  </Item>
</ItemGroup>
```

**Tags:** item, list, row, media, content

---

### Kbd

Keyboard key representation for shortcuts and documentation

**Import:**
```tsx
import { Kbd, KbdGroup } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Single key with size
<Kbd size="sm">Ctrl</Kbd>
<Kbd size="default">Ctrl</Kbd>
<Kbd size="lg">Ctrl</Kbd>

// Key combination with KbdGroup
<KbdGroup>
  <Kbd>Ctrl</Kbd>
  <Kbd>C</Kbd>
</KbdGroup>

// Multiple shortcuts
<KbdGroup>
  <Kbd>⌘</Kbd>
  <Kbd>Shift</Kbd>
  <Kbd>P</Kbd>
</KbdGroup>
```

**Tags:** keyboard, shortcut, key, hotkey, documentation, size

---

### Portal

Renders children into a different part of the DOM (similar to MUI Portal)

**Import:**
```tsx
import { Portal } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Render to document.body (default)
<Portal>
  <div className="fixed inset-0 z-50 bg-black/50">
    Modal content rendered at body
  </div>
</Portal>

// Render to custom container
<Portal container={document.getElementById('modal-root')}>
  <div>Content in custom container</div>
</Portal>

// Disable portal (render in place)
<Portal disablePortal>
  <div>Rendered normally in DOM hierarchy</div>
</Portal>

// With ref container
const containerRef = useRef<HTMLDivElement>(null);
<div ref={containerRef} />
<Portal container={containerRef}>
  <div>Content in ref container</div>
</Portal>
```

**Tags:** portal, modal, overlay, teleport, render

---

### Preloader

Universal loading indicator with multiple variants

**Import:**
```tsx
import { Preloader, PreloaderSkeleton } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Inline loading
<Preloader text="Loading..." />

// Fullscreen with backdrop
<Preloader variant="fullscreen" text="Loading data..." />

// Different sizes
<Preloader size="sm" text="Small" />
<Preloader size="lg" text="Large" />

// Skeleton variant
<PreloaderSkeleton lines={3} showAvatar />
```

**Tags:** loading, spinner, preloader, skeleton, indicator

---

### Resizable

Resizable panel layout with smart drag handles. Supports size variants, hover indicators, and classic dots handle.

**Import:**
```tsx
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<ResizablePanelGroup direction="horizontal" className="min-h-[200px]">
  <ResizablePanel defaultSize={50}>
    <div className="p-4">Left panel</div>
  </ResizablePanel>
  <ResizableHandle size="md" showIndicator />
  <ResizablePanel defaultSize={50}>
    <div className="p-4">Right panel</div>
  </ResizablePanel>
</ResizablePanelGroup>
```

**Props:**
- `size`: `"sm" | "md" | "lg"` - Handle size variant - controls hit area width
- `showIndicator`: `boolean` - Show visual pill indicator on hover
- `indicatorHeight`: `number` - Custom indicator height in pixels (default: 32)
- `withHandle`: `boolean` - Show classic dots handle icon

**Tags:** resizable, panel, split, drag, resize

---

### ScrollArea

Custom scrollable area with styled scrollbars

**Import:**
```tsx
import { ScrollArea } from '@djangocfg/ui-nextjs';
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

### Section

Content section with optional header

**Import:**
```tsx
import { Section, SectionHeader } from '@djangocfg/ui-nextjs';
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

### Separator

Visual separator between content sections

**Import:**
```tsx
import { Separator } from '@djangocfg/ui-nextjs';
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

### Sidebar

Full-featured sidebar navigation component with collapsible menu, groups, and mobile support

**Import:**
```tsx
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarTrigger, useSidebar } from '@djangocfg/ui-nextjs';
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

---

### Skeleton

Loading placeholder for content

**Import:**
```tsx
import { Skeleton } from '@djangocfg/ui-nextjs';
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

### Sticky

Sticky positioned element wrapper

**Import:**
```tsx
import { Sticky } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Sticky offsetTop={0} className="z-50">
  <header className="bg-background border-b p-4">
    Sticky Header
  </header>
</Sticky>
```

**Tags:** sticky, fixed, position, header, footer

---

## Navigation (6)

Menus, breadcrumbs, tabs, and pagination

### Breadcrumb

Breadcrumb navigation for page hierarchy

**Import:**
```tsx
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@djangocfg/ui-nextjs';
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
import { BreadcrumbNavigation } from '@djangocfg/ui-nextjs';
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

### Menubar

Horizontal menu bar with dropdowns

**Import:**
```tsx
import { Menubar, MenubarContent, MenubarItem, MenubarMenu, MenubarSeparator, MenubarTrigger } from '@djangocfg/ui-nextjs';
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

### NavigationMenu

Main navigation menu with dropdowns

**Import:**
```tsx
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from '@djangocfg/ui-nextjs';
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
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@djangocfg/ui-nextjs';
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

### Tabs

Tab-based navigation between content sections

**Import:**
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui-nextjs';
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

## Overlay (9)

Dialogs, sheets, popovers, tooltips, and dropdowns

### AlertDialog

Confirmation dialog for destructive actions

**Import:**
```tsx
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@djangocfg/ui-nextjs';
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

### ContextMenu

Right-click context menu

**Import:**
```tsx
import { ContextMenu, ContextMenuContent, ContextMenuItem, ContextMenuTrigger } from '@djangocfg/ui-nextjs';
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

### Dialog

Modal dialog for focused interactions

**Import:**
```tsx
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@djangocfg/ui-nextjs';
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

### Drawer

Mobile-friendly drawer with swipe gestures (vaul)

**Import:**
```tsx
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle, DrawerTrigger } from '@djangocfg/ui-nextjs';
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

### DropdownMenu

Accessible dropdown menu

**Import:**
```tsx
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@djangocfg/ui-nextjs';
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

### HoverCard

Preview card on hover

**Import:**
```tsx
import { HoverCard, HoverCardContent, HoverCardTrigger } from '@djangocfg/ui-nextjs';
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

### Popover

Floating content triggered by click

**Import:**
```tsx
import { Popover, PopoverContent, PopoverTrigger } from '@djangocfg/ui-nextjs';
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

### Sheet

Slide-out panel from screen edge

**Import:**
```tsx
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@djangocfg/ui-nextjs';
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

### Tooltip

Hover tooltip for additional information

**Import:**
```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@djangocfg/ui-nextjs';
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

## Feedback (4)

Toasts, alerts, progress bars, and status indicators

### Alert

Alert messages for important information

**Import:**
```tsx
import { Alert, AlertDescription, AlertTitle } from '@djangocfg/ui-nextjs';
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

**Tags:** alert, warning, info, error

---

### Badge

Status badges for labels and categories

**Import:**
```tsx
import { Badge } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
```

**Tags:** badge, tag, label, status

---

### Progress

Progress bar for showing completion status

**Import:**
```tsx
import { Progress } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<Progress value={25} />
<Progress value={50} />
<Progress value={75} />
```

**Tags:** progress, loading, percentage, status

---

### Toast

Toast notifications with auto-dismiss support

**Import:**
```tsx
import { useToast, Toaster } from '@djangocfg/ui-nextjs';
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
          duration: 5000, // Auto-dismiss after 5s (default)
        });
      }}
    >
      Show Toast
    </Button>
  );
}

// Destructive toast
toast({
  variant: "destructive",
  title: "Error",
  description: "Something went wrong.",
});

// Persistent toast (no auto-dismiss)
toast({
  title: "Important",
  description: "This won't auto-dismiss.",
  duration: 0,
});
```

**Tags:** toast, notification, alert, message, feedback

---

## Data Display (9)

Tables, accordions, and data visualization

### Accordion

Collapsible content sections

**Import:**
```tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@djangocfg/ui-nextjs';
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

### Calendar

Base calendar component for date display. For input with popover, use DatePicker.

**Import:**
```tsx
import { Calendar } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Basic calendar
const [date, setDate] = useState<Date | undefined>(new Date());

<Calendar
  mode="single"
  selected={date}
  onSelect={setDate}
  className="rounded-md border"
/>

// With dropdown year/month navigation
<Calendar
  mode="single"
  captionLayout="dropdown"
/>

// Multiple months
<Calendar
  mode="single"
  numberOfMonths={2}
/>
```

**Tags:** calendar, date, display

---

### Carousel

Touch-friendly carousel/slider component

**Import:**
```tsx
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@djangocfg/ui-nextjs';
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

### Collapsible

Simple collapsible content block

**Import:**
```tsx
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@djangocfg/ui-nextjs';
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

### DatePicker

Input field with popover calendar for selecting a single date

**Import:**
```tsx
import { DatePicker } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const [date, setDate] = useState<Date | undefined>();

<DatePicker
  value={date}
  onChange={setDate}
  placeholder="Select date"
/>

// With date limits
<DatePicker
  value={date}
  onChange={setDate}
  fromDate={new Date()}
  toDate={addDays(new Date(), 30)}
/>

// Custom format
<DatePicker
  value={date}
  onChange={setDate}
  dateFormat="yyyy-MM-dd"
/>
```

**Tags:** date, picker, input, popover, form

---

### DateRangePicker

Input field with popover calendar for selecting a date range

**Import:**
```tsx
import { DateRangePicker, type DateRange } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const [range, setRange] = useState<DateRange | undefined>({
  from: new Date(),
  to: addDays(new Date(), 7),
});

<DateRangePicker
  value={range}
  onChange={setRange}
  placeholder="Select dates"
/>

// With more months
<DateRangePicker
  value={range}
  onChange={setRange}
  numberOfMonths={3}
/>

// Custom format
<DateRangePicker
  value={range}
  onChange={setRange}
  dateFormat="yyyy-MM-dd"
/>
```

**Tags:** date, range, picker, input, popover, form

---

### SSRPagination

Server-side rendered pagination with URL-based navigation for Next.js SSR/SSG

**Import:**
```tsx
import { SSRPagination } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// In your Next.js page component
import { SSRPagination } from '@djangocfg/ui-nextjs';

export default function ProductsPage({ searchParams }: { searchParams: { page?: string } }) {
  const currentPage = Number(searchParams.page) || 1;
  const itemsPerPage = 20;

  // Fetch data from database/API
  const { items, total } = await getProducts({ page: currentPage, limit: itemsPerPage });

  const totalPages = Math.ceil(total / itemsPerPage);

  return (
    <div>
      <ProductList items={items} />

      <SSRPagination
        currentPage={currentPage}
        totalPages={totalPages}
        totalItems={total}
        itemsPerPage={itemsPerPage}
        hasNextPage={currentPage < totalPages}
        hasPreviousPage={currentPage > 1}
        showInfo={true}
        maxVisiblePages={7}
      />
    </div>
  );
}
```

**Tags:** pagination, ssr, navigation, nextjs, seo

---

### StaticPagination

Client-side pagination for Django REST Framework paginated API responses

**Import:**
```tsx
import { StaticPagination, useDRFPagination } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Client component with API calls

import { StaticPagination, useDRFPagination } from '@djangocfg/ui-nextjs';
import { useQuery } from '@tanstack/react-query';

function UserList() {
  const pagination = useDRFPagination();

  const { data, isLoading } = useQuery({
    queryKey: ['users', pagination.params],
    queryFn: () => fetchUsers(pagination.params),
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <ul>
        {data.results.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>

      <StaticPagination
        data={data}
        onPageChange={pagination.setPage}
        showInfo={true}
      />
    </div>
  );
}

// API response format (DRF standard):
// {
//   count: 100,
//   next: "https://api.example.com/users/?page=2",
//   previous: null,
//   results: [...]
// }
```

**Tags:** pagination, drf, django, client-side, api

---

### Table

Data table with headers and rows

**Import:**
```tsx
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from '@djangocfg/ui-nextjs';
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

## Specialized (4)

Advanced components like sidebar and image handling

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
} from '@djangocfg/ui-nextjs';
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

### OgImage

Dynamic Open Graph image component using the OG Image API

**Import:**
```tsx
import { OgImage } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<OgImage
  params={{
    title: 'My Page Title',
    description: 'Page description text',
    siteName: 'My Site',
  }}
  className="rounded-lg"
/>
```

**Tags:** image, og, seo, meta

---

### Spinner

Loading spinner indicator

**Import:**
```tsx
import { Spinner } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<div className="flex gap-4 items-center">
  <Spinner />
  <Spinner className="size-6" />
  <Spinner className="size-8" />
</div>
```

**Tags:** loading, spinner, indicator

---

### Toaster

Toast notifications powered by Sonner library

**Import:**
```tsx
import { Toaster } from '@djangocfg/ui-nextjs';
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

---

## Developer Tools (11)

JSON viewer, code highlighting, Mermaid diagrams

### Interactive JsonSchemaForm

Interactive JSON Schema Form playground - try different schemas and see live form generation

**Import:**
```tsx
import { JsonSchemaForm } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const schema = {
  type: "object",
  title: "User Profile",
  required: ["name", "email"],
  properties: {
    name: { type: "string", title: "Full Name", minLength: 2 },
    email: { type: "string", title: "Email", format: "email" },
    age: { type: "integer", title: "Age", minimum: 0, maximum: 150 },
    notifications: { type: "boolean", title: "Enable Notifications" }
  }
};

<JsonSchemaForm
  schema={schema}
  onSubmit={(data) => console.log(data.formData)}
  onChange={(data) => setFormData(data.formData)}
  liveValidate={true}
  showSubmitButton={true}
  submitButtonText="Save"
/>
```

**Tags:** form, json-schema, generator, dynamic, interactive

---

### JsonTree

Interactive JSON tree viewer with expand/collapse, search, and export functionality

**Import:**
```tsx
import { JsonTree } from '@djangocfg/ui-nextjs';
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

**Tags:** json, tree, viewer, debug

---

### LottiePlayer

Lottie animation player with size presets and playback controls

**Import:**
```tsx
import { LottiePlayer } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<LottiePlayer
  src="https://djangocfg.com/static/lottie/coding.json"
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

**Tags:** animation, lottie, motion

---

### MarkdownMessage with Mermaid

Example of MarkdownMessage rendering Mermaid diagrams inline

**Import:**
```tsx
import { MarkdownMessage } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<MarkdownMessage
  content={`
# Mermaid Diagram

Here's a flowchart:

\`\`\`mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
\`\`\`
  `}
/>
```

**Tags:** markdown, mermaid, diagram, flowchart

---

### MarkdownMessage

Markdown renderer with GFM support, syntax highlighting, Mermaid diagrams, and chat-optimized styling

**Import:**
```tsx
import { MarkdownMessage } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
<MarkdownMessage
  content="# Hello World\n\nThis is **bold** text with `code`."
/>

// User message styling (inverted colors)
<MarkdownMessage
  content="Some user message"
  isUser
/>

// With code blocks and mermaid
<MarkdownMessage
  content={`
## Code Example

\`\`\`typescript
const greeting = "Hello!";
\`\`\`

\`\`\`mermaid
graph TD
  A --> B
\`\`\`
  `}
/>
```

**Tags:** markdown, gfm, syntax, mermaid, chat, message, interactive

---

### Mermaid

Interactive Mermaid diagram renderer with fullscreen view and theme support

**Import:**
```tsx
import { Mermaid } from '@djangocfg/ui-nextjs';
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

**Tags:** diagram, mermaid, flowchart, chart

---

### OgImageTemplate

Interactive OG Image template with customizable design and live preview

**Import:**
```tsx
import { DefaultTemplate } from '@djangocfg/nextjs/og-image/components';
```

**Example:**
```tsx
import { createOgImageDynamicRoute } from '@djangocfg/nextjs/og-image';
import { DefaultTemplate } from '@djangocfg/nextjs/og-image/components';

const handler = createOgImageDynamicRoute({
  template: DefaultTemplate,
  defaultProps: {
    siteName: "Django CFG",
    logo: "https://djangocfg.com/logo.svg",
  },
  fonts: [
    { family: 'Manrope', weight: 700 },
    { family: 'Manrope', weight: 500 },
  ],
  size: { width: 1200, height: 630 },
});
```

**Tags:** og-image, metadata, seo, nextjs, template

---

### OpenapiViewer

Interactive OpenAPI/Swagger documentation viewer with API playground

**Import:**
```tsx
import { OpenapiViewer } from '@djangocfg/ui-nextjs';
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

**Tags:** openapi, swagger, api, documentation, playground

---

### PrettyCode

Syntax-highlighted code display with automatic language detection and theme support

**Import:**
```tsx
import { PrettyCode } from '@djangocfg/ui-nextjs';
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

**Tags:** code, syntax, highlight, prism

---

### UseQueryParams

Hook for safely accessing URL query parameters without Suspense boundary

**Import:**
```tsx
import { useQueryParams } from '@djangocfg/ui-nextjs/hooks';
```

**Example:**
```tsx
const queryParams = useQueryParams();
const flow = queryParams.get('flow');
const page = queryParams.get('page');
const tags = queryParams.getAll('tags');
const hasFlow = queryParams.has('flow');
```

**Tags:** hooks, query-params, url, router

---

### VideoPlayer

Professional video player with YouTube, Vimeo, MP4, HLS support

**Import:**
```tsx
import { VideoPlayer } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// YouTube video
<VideoPlayer
  source={{
    url: 'youtube/dQw4w9WgXcQ',
    title: 'Video Title',
    description: 'Video description',
  }}
  aspectRatio={16 / 9}
  theme="modern"
/>

// Direct MP4
<VideoPlayer
  source={{
    url: 'https://example.com/video.mp4',
    poster: 'https://example.com/poster.jpg',
  }}
  autoplay
  muted
/>
```

**Tags:** video, player, youtube, vimeo, media, vidstack

---

## Blocks (8)

Pre-built landing page sections

### CTASection

Call-to-action section to drive conversions

**Import:**
```tsx
import { CTASection } from '@djangocfg/ui-nextjs/blocks';
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

**Tags:** cta, call-to-action, landing

---

### FeatureSection

Grid of features with icons and descriptions. Supports default (cards) and compact (minimal) variants.

**Import:**
```tsx
import { FeatureSection } from '@djangocfg/ui-nextjs/blocks';
```

**Example:**
```tsx
// Default variant - with cards
<FeatureSection
  title="Everything You Need"
  subtitle="All the tools to build modern applications"
  features={[
    { icon: <Zap className="w-6 h-6" />, title: "Fast", description: "Optimized" },
    { icon: <Shield className="w-6 h-6" />, title: "Secure", description: "Protected" }
  ]}
/>

// Compact variant - minimal, no cards
<FeatureSection
  features={features}
  columns={6}
  variant="compact"
  background="none"
/>
```

**Tags:** features, grid, landing, compact

---

### Hero

Hero section with title, description, and CTAs

**Import:**
```tsx
import { Hero } from '@djangocfg/ui-nextjs/blocks';
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

**Tags:** hero, landing, section

---

### NewsletterSection

Email capture section for newsletters

**Import:**
```tsx
import { NewsletterSection } from '@djangocfg/ui-nextjs/blocks';
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

**Tags:** newsletter, email, subscription, landing

---

### SplitHero

Split-layout hero with text on one side and image/video/custom component on the other. Supports left/right layouts and responsive mobile ordering.

**Import:**
```tsx
import { SplitHero } from '@djangocfg/ui-nextjs/blocks';
```

**Example:**
```tsx
// With image
<SplitHero
  badge={{ text: 'New' }}
  title="Build faster with"
  titleGradient="modern tools"
  subtitle="Ship your next project in minutes."
  primaryAction={{ label: 'Get Started', href: '#' }}
  media={{ type: 'image', src: '/hero.jpg', alt: 'Hero' }}
  layout="text-left"
/>

// With video
<SplitHero
  title="See it in action"
  media={{ type: 'video', url: 'youtube/VIDEO_ID' }}
  layout="text-right"
/>

// With custom component
<SplitHero
  title="Your product"
  media={{ type: 'custom', content: <YourComponent /> }}
/>
```

**Tags:** hero, split, landing, video, image

---

### StatsSection

Display key metrics and statistics

**Import:**
```tsx
import { StatsSection } from '@djangocfg/ui-nextjs/blocks';
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

**Tags:** stats, metrics, numbers, landing

---

### SuperHero

Enhanced hero with badge, gradient title, code commands, features, and stats

**Import:**
```tsx
import { SuperHero } from '@djangocfg/ui-nextjs/blocks';
```

**Example:**
```tsx
<SuperHero
  badge={{ icon: <Sparkles />, text: "New in v2.0" }}
  title="Next-Generation"
  titleGradient="Development Platform"
  subtitle="Build faster with our comprehensive UI library"
  codeCommands={[
    "pip install django-cfg",
    "django-cfg create-project my_app"
  ]}
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

**Tags:** hero, landing, gradient, animated, commands

---

### TestimonialSection

Customer testimonials and reviews

**Import:**
```tsx
import { TestimonialSection } from '@djangocfg/ui-nextjs/blocks';
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

**Tags:** testimonials, reviews, social-proof, landing

---

## Hooks (15)

Custom React hooks for common functionality

### useBrowserDetect

Advanced browser detection that correctly identifies Chromium-based browsers (Arc, Brave, Comet, Vivaldi) vs real Safari

**Import:**
```tsx
import { useBrowserDetect } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
import { useBrowserDetect } from '@djangocfg/ui-nextjs';

function MyComponent() {
  const browser = useBrowserDetect();

  // Real Safari (not Chromium browsers like Arc, Comet)
  if (browser.isSafari && !browser.isChromium) {
    return <SafariSpecificFeature />;
  }

  // Any Chromium browser
  if (browser.isChromium) {
    return <ChromiumOptimizedView />;
  }

  // Specific browsers
  if (browser.isBrave) return <BraveFeature />;
  if (browser.isArc) return <ArcFeature />;

  return <DefaultView />;
}
```

**Tags:** hook, browser, detection, chromium, safari, arc, brave, vivaldi, comet, engine, webkit, blink

---

### useCopy

Copy to clipboard hook with async support

**Import:**
```tsx
import { useCopy } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, clipboard, copy, paste

---

### useCountdown

Countdown timer hook with days, hours, minutes, seconds

**Import:**
```tsx
import { useCountdown } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, countdown, timer, time

---

### useDebounce

Debounce value changes to reduce API calls and improve performance

**Import:**
```tsx
import { useDebounce } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, debounce, performance, search

---

### useDebouncedCallback

Create a debounced version of a callback function

**Import:**
```tsx
import { useDebouncedCallback } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const debouncedSearch = useDebouncedCallback((term: string) => {
  // This function will only run 300ms after the user stops typing
  searchAPI(term);
}, 300);

// Use in event handler
<Input onChange={(e) => debouncedSearch(e.target.value)} />
```

**Tags:** hook, debounce, callback, performance, function

---

### useDebugTools

Debug utilities for development environment

**Import:**
```tsx
import { useDebugTools } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const debug = useDebugTools('MyComponent');

// Log component state changes
debug.log('State updated:', state);

// Measure performance
debug.time('expensive-operation');
doExpensiveWork();
debug.timeEnd('expensive-operation');

// Log only in development
debug.info('Component mounted');
debug.warn('Deprecated prop used');
debug.error('Something went wrong');
```

**Tags:** hook, debug, logging, development, performance

---

### useDeviceDetect

Comprehensive device detection using react-device-detect with SSR support

**Import:**
```tsx
import { useDeviceDetect } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
import { useDeviceDetect } from '@djangocfg/ui-nextjs';

function MyComponent() {
  const device = useDeviceDetect();

  // Device type checks
  if (device.isMobile) {
    return <MobileView />;
  }

  // OS checks
  if (device.isIOS) {
    return <IOSSpecificFeature />;
  }

  // Browser checks
  if (device.isChrome) {
    return <ChromeOptimizedView />;
  }

  // Orientation
  if (device.isPortrait) {
    return <PortraitLayout />;
  }

  return <DefaultView />;
}
```

**Tags:** hook, device, detection, mobile, tablet, desktop, browser, os, orientation, react-device-detect, ssr

---

### useEventListener

Subscribe to custom events with type-safe event bus

**Import:**
```tsx
import { useEventListener, events } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, events, pubsub, communication

---

### useHotkey

Keyboard shortcuts hook - wrapper for react-hotkeys-hook

**Import:**
```tsx
import { useHotkey } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Simple key (Escape is always safe)
useHotkey('escape', () => closeModal());

// 'mod' = ⌘ on Mac, Ctrl on Windows
// Use mod+shift to avoid browser conflicts
useHotkey('mod+shift+s', (e) => {
  e.preventDefault();
  saveDocument();
});

// Arrow keys are safe
useHotkey('ArrowUp', () => moveUp());

// Alt combinations are usually safe
useHotkey('alt+n', () => newItem());

// With options
useHotkey('/', () => focusSearch(), {
  preventDefault: true,
  enableOnFormTags: false,
});
```

**Tags:** hook, keyboard, shortcuts, hotkeys, a11y

---

### useImageLoader

Preload images and track loading state

**Import:**
```tsx
import { useImageLoader } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, image, loading, preload

---

### useIsMobile

Check if device is mobile (viewport < 768px)

**Import:**
```tsx
import { useIsMobile } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const isMobile = useIsMobile(); // Boolean

return isMobile ? <MobileMenu /> : <DesktopMenu />;

// Or conditionally render
{isMobile && <MobileNavigation />}
{!isMobile && <DesktopNavigation />}
```

**Tags:** hook, mobile, responsive, viewport

---

### useLocalStorage

Persist state to localStorage with automatic serialization

**Import:**
```tsx
import { useLocalStorage } from '@djangocfg/ui-nextjs';
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

**Tags:** hook, storage, persist, state

---

### useMediaQuery

Responsive media query hook for conditional rendering

**Import:**
```tsx
import { useMediaQuery } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const isMobile = useMediaQuery('(max-width: 768px)');
const isDesktop = useMediaQuery('(min-width: 1024px)');
const prefersDark = useMediaQuery('(prefers-color-scheme: dark)');

return isMobile ? <MobileView /> : <DesktopView />;
```

**Tags:** hook, responsive, media-query, viewport

---

### useSessionStorage

Persist state to sessionStorage (cleared on tab close)

**Import:**
```tsx
import { useSessionStorage } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
const [cart, setCart] = useSessionStorage('shopping-cart', []);

// Add item
setCart([...cart, newItem]);
```

**Tags:** hook, storage, session, state

---

### useThemeContext

Theme hooks: useThemeContext (full control) and useResolvedTheme (read-only)

**Import:**
```tsx
import { useThemeContext, useResolvedTheme } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Full control (requires ThemeProvider)
const { theme, setTheme, resolvedTheme, toggleTheme } = useThemeContext();
setTheme('dark');     // Set to dark
setTheme('system');   // Use system preference
toggleTheme();        // Toggle light/dark

// Read-only (standalone, no provider)
const theme = useResolvedTheme(); // 'light' | 'dark'
```

**Tags:** hook, theme, dark-mode, light-mode, system

---

## Charts (7)

Data visualization with Area, Bar, Line, Pie, and Radar charts

### Area Chart

Filled area chart for visualizing volume over time

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@djangocfg/ui-nextjs';
import { Area, AreaChart, XAxis, YAxis, CartesianGrid } from 'recharts';
```

**Example:**
```tsx
const chartConfig = {
  revenue: { label: "Revenue", color: "hsl(var(--chart-1))" },
  expenses: { label: "Expenses", color: "hsl(var(--chart-2))" },
};

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <AreaChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="month" />
    <YAxis />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Area
      type="monotone"
      dataKey="revenue"
      fill="var(--color-revenue)"
      fillOpacity={0.4}
      stroke="var(--color-revenue)"
    />
    <Area
      type="monotone"
      dataKey="expenses"
      fill="var(--color-expenses)"
      fillOpacity={0.4}
      stroke="var(--color-expenses)"
    />
  </AreaChart>
</ChartContainer>
```

**Tags:** chart, area, stacked, volume, analytics

---

### Bar Chart

Vertical bar chart for comparing categorical data

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@djangocfg/ui-nextjs';
import { Bar, BarChart, XAxis, YAxis, CartesianGrid } from 'recharts';
```

**Example:**
```tsx
const chartConfig = {
  desktop: { label: "Desktop", color: "hsl(var(--chart-1))" },
  mobile: { label: "Mobile", color: "hsl(var(--chart-2))" },
};

const data = [
  { month: "Jan", desktop: 186, mobile: 80 },
  { month: "Feb", desktop: 305, mobile: 200 },
  // ...
];

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <BarChart data={data}>
    <CartesianGrid strokeDasharray="3 3" vertical={false} />
    <XAxis dataKey="month" tickLine={false} axisLine={false} />
    <YAxis tickLine={false} axisLine={false} />
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
  </BarChart>
</ChartContainer>
```

**Tags:** chart, bar, comparison, analytics, recharts

---

### ChartContainer

Base wrapper component for all chart types with theme-aware styling

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// ChartConfig type
type ChartConfig = {
  [key: string]: {
    label?: ReactNode;
    icon?: ComponentType;
    color?: string;
    // or use theme-aware colors:
    theme?: {
      light: string;
      dark: string;
    };
  };
};

// Basic usage
const chartConfig: ChartConfig = {
  sales: {
    label: "Sales",
    color: "hsl(var(--chart-1))",
  },
  revenue: {
    label: "Revenue",
    color: "hsl(var(--chart-2))",
  },
};

<ChartContainer config={chartConfig} className="h-[300px]">
  {/* Any Recharts component */}
  <BarChart data={data}>
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="sales" fill="var(--color-sales)" />
    <Bar dataKey="revenue" fill="var(--color-revenue)" />
  </BarChart>
</ChartContainer>
```

**Tags:** chart, container, wrapper, recharts, config

---

### Donut Chart

Donut chart with center label for showing progress or distribution

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@djangocfg/ui-nextjs';
import { Pie, PieChart, Label } from 'recharts';
```

**Example:**
```tsx
<ChartContainer config={chartConfig} className="h-[250px] w-full">
  <PieChart>
    <ChartTooltip content={<ChartTooltipContent />} />
    <Pie
      data={data}
      dataKey="value"
      nameKey="name"
      innerRadius={60}
      outerRadius={80}
    >
      <Label
        content={({ viewBox }) => (
          <text x={viewBox.cx} y={viewBox.cy} textAnchor="middle">
            <tspan
              style={{ fill: 'hsl(var(--foreground))', fontSize: '30px', fontWeight: 'bold' }}
              x={viewBox.cx}
              y={viewBox.cy}
            >
              65%
            </tspan>
            <tspan
              x={viewBox.cx}
              y={viewBox.cy + 20}
              style={{ fill: 'hsl(var(--muted-foreground))', fontSize: '14px' }}
            >
              Completed
            </tspan>
          </text>
        )}
      />
    </Pie>
  </PieChart>
</ChartContainer>
```

**Tags:** chart, donut, progress, ring, analytics

---

### Line Chart

Line chart for showing trends over time

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@djangocfg/ui-nextjs';
import { Line, LineChart, XAxis, YAxis, CartesianGrid } from 'recharts';
```

**Example:**
```tsx
const chartConfig = {
  visitors: { label: "Visitors", color: "hsl(var(--chart-1))" },
  pageViews: { label: "Page Views", color: "hsl(var(--chart-2))" },
};

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <LineChart data={data}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Line
      type="monotone"
      dataKey="visitors"
      stroke="var(--color-visitors)"
      strokeWidth={2}
      dot={false}
    />
    <Line
      type="monotone"
      dataKey="pageViews"
      stroke="var(--color-pageViews)"
      strokeWidth={2}
      dot={false}
    />
  </LineChart>
</ChartContainer>
```

**Tags:** chart, line, trend, time-series, analytics

---

### Pie Chart

Pie chart for showing proportions of a whole

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@djangocfg/ui-nextjs';
import { Pie, PieChart, Cell } from 'recharts';
```

**Example:**
```tsx
const chartConfig = {
  Chrome: { label: "Chrome", color: "hsl(var(--chart-1))" },
  Safari: { label: "Safari", color: "hsl(var(--chart-2))" },
  Firefox: { label: "Firefox", color: "hsl(var(--chart-3))" },
};

const data = [
  { name: "Chrome", value: 275, fill: "hsl(var(--chart-1))" },
  { name: "Safari", value: 200, fill: "hsl(var(--chart-2))" },
  { name: "Firefox", value: 187, fill: "hsl(var(--chart-3))" },
];

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <PieChart>
    <ChartTooltip content={<ChartTooltipContent />} />
    <Pie
      data={data}
      dataKey="value"
      nameKey="name"
      cx="50%"
      cy="50%"
      outerRadius={100}
    />
    <ChartLegend content={<ChartLegendContent />} />
  </PieChart>
</ChartContainer>
```

**Tags:** chart, pie, proportion, distribution, analytics

---

### Radial Bar Chart

Radial bar chart for comparing values in a circular format

**Import:**
```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@djangocfg/ui-nextjs';
import { RadialBar, RadialBarChart, PolarGrid, PolarAngleAxis } from 'recharts';
```

**Example:**
```tsx
const chartConfig = {
  visitors: { label: "Visitors" },
  Chrome: { label: "Chrome", color: "hsl(var(--chart-1))" },
  Safari: { label: "Safari", color: "hsl(var(--chart-2))" },
  Firefox: { label: "Firefox", color: "hsl(var(--chart-3))" },
};

<ChartContainer config={chartConfig} className="h-[300px] w-full">
  <RadialBarChart data={data} innerRadius={30} outerRadius={100}>
    <ChartTooltip content={<ChartTooltipContent />} />
    <PolarGrid gridType="circle" />
    <RadialBar dataKey="visitors" background />
  </RadialBarChart>
</ChartContainer>
```

**Tags:** chart, radial, circular, gauge, analytics

---

## Animations (8)

Animated backgrounds and visual effects for hero sections

### Aurora Borealis

Flowing northern lights effect with multi-color bands

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="aurora-borealis" intensity="medium" colorScheme="vibrant" />
```

**Tags:** aurora, borealis, northern lights, wave, colorful

---

### Color Schemes

Comparison of different color schemes

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
// Vibrant - all chart colors
<AnimatedBackground variant="mesh-gradient" colorScheme="vibrant" />

// Cool - blue and purple tones
<AnimatedBackground variant="mesh-gradient" colorScheme="cool" />

// Warm - orange and red tones
<AnimatedBackground variant="mesh-gradient" colorScheme="warm" />

// Monochrome - primary color only
<AnimatedBackground variant="mesh-gradient" colorScheme="monochrome" />
```

**Tags:** color, scheme, palette, theme

---

### Floating Orbs

Animated glowing spheres with various colors

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="floating-orbs" intensity="medium" colorScheme="vibrant" />
```

**Tags:** orbs, spheres, floating, glow, particles

---

### Geometric Flow

Clean geometric grid patterns with animated lines

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="geometric-flow" intensity="medium" colorScheme="cool" />
```

**Tags:** grid, lines, geometric, tech, pattern

---

### AnimatedBackground

Animated background effects for hero sections and landing pages with multi-color gradients

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<div className="relative h-[500px]">
  <AnimatedBackground
    variant="mesh-gradient"
    intensity="medium"
    colorScheme="vibrant"
  />
  <div className="relative z-10 flex items-center justify-center h-full">
    <h1>Your Content Here</h1>
  </div>
</div>

// Available variants:
// - aurora-borealis: Flowing northern lights effect
// - mesh-gradient: Modern Apple-style gradient mesh
// - floating-orbs: Animated glowing spheres
// - geometric-flow: Clean geometric patterns
// - liquid-gradient: Smooth flowing liquid effect
// - spotlight: Dramatic spotlight effect
// - none: No background

// Color schemes:
// - vibrant: Multi-color (blue, green, purple, orange, red)
// - cool: Blue and purple tones
// - warm: Orange and red tones
// - monochrome: Primary color only
```

**Tags:** animation, background, hero, landing, effects, gradient

---

### Liquid Gradient

Smooth flowing liquid effect with bubbles

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="liquid-gradient" intensity="medium" colorScheme="warm" />
```

**Tags:** liquid, waves, flow, bubbles, ocean

---

### Mesh Gradient

Modern Apple-style floating gradient orbs

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="mesh-gradient" intensity="medium" colorScheme="vibrant" />
```

**Tags:** gradient, mesh, orbs, floating, apple

---

### Spotlight

Dramatic rotating conic gradient spotlight

**Import:**
```tsx
import { AnimatedBackground } from '@djangocfg/ui-nextjs/animations';
```

**Example:**
```tsx
<AnimatedBackground variant="spotlight" intensity="medium" colorScheme="vibrant" />
```

**Tags:** spotlight, conic, rotating, dramatic, hero

---

## Layouts (10)

Full-page layouts, providers, and layout components from @djangocfg/layouts

### AIChatWidget

MCP-powered AI chat widget with semantic search and documentation assistance

**Import:**
```tsx
import { AIChatWidget, AIChatProvider } from '@djangocfg/layouts/snippets';
```

**Example:**
```tsx
// Wrap your app with provider
<AIChatProvider
  config={{
    apiUrl: '/api/ai/chat',
    welcomeMessage: 'Hi! How can I help you?'
  }}
>
  {children}

  {/* Add widget */}
  <AIChatWidget position="bottom-right" />
</AIChatProvider>

// Or use in BaseApp (already included)
<BaseApp
  mcpChat={{
    enabled: true,
    position: 'bottom-right',
    config: {
      apiUrl: '/api/ai/chat',
      welcomeMessage: 'Hi! How can I help you?'
    }
  }}
>
  {children}
</BaseApp>

// Control programmatically
window.dispatchEvent(new CustomEvent('mcp:chat:open'));
window.dispatchEvent(new CustomEvent('mcp:chat:close'));
```

**Tags:** chat, ai, mcp, widget, floating, interactive, documentation, assistant

---

### AdminLayout

Admin dashboard layout with sidebar and monitoring tools

**Import:**
```tsx
import { AdminLayout } from '@djangocfg/layouts';
```

**Example:**
```tsx
<AdminLayout
  sidebar={{
    items: [
      { label: 'Overview', href: '/admin', icon: LayoutDashboard },
      { label: 'Users', href: '/admin/users', icon: Users }
    ],
    homeHref: '/admin'
  }}
  header={{
    title: 'Admin Dashboard',
    groups: [
      {
        title: 'Admin',
        items: [
          { label: 'Profile', href: '/profile' },
          { label: 'Settings', href: '/settings' }
        ]
      }
    ],
    authPath: '/auth'
  }}
>
  <div>Your admin content</div>
</AdminLayout>
```

**Tags:** layout, admin, dashboard, management, sidebar, monitoring

---

### Analytics

Google Analytics 4 integration with auto page tracking

**Import:**
```tsx
import { AnalyticsProvider, Analytics, AnalyticsEvent } from '@djangocfg/layouts/snippets';
```

**Example:**
```tsx
// Wrap your app
<AnalyticsProvider trackingId="G-XXXXXXXXXX">
  {children}
</AnalyticsProvider>

// Track events anywhere
import { Analytics, AnalyticsEvent } from '@djangocfg/layouts/snippets';

// Track page view
Analytics.pageview('/page-url');

// Track theme change event
Analytics.event(AnalyticsEvent.THEME_CHANGE, {
  category: 'engagement',
  label: 'Theme Button',
  value: 1
});

// Track custom event
Analytics.event('custom_event', {
  category: 'custom',
  label: 'Custom Action'
});
```

**Tags:** analytics, google-analytics, ga4, tracking, events, pageview

---

### AppLayout

Smart layout router that auto-detects route and applies correct layout

**Import:**
```tsx
import { AppLayout } from '@djangocfg/layouts';
```

**Example:**
```tsx
<AppLayout
  // Provider configs (passed to BaseApp)
  theme={{ defaultTheme: 'system' }}
  auth={{ loginPath: '/auth' }}
  analytics={{ googleTrackingId: 'G-XXX' }}
  pwaInstall={{ enabled: true }}
  pushNotifications={{
    enabled: true,
    vapidPublicKey: process.env.NEXT_PUBLIC_VAPID_KEY || ''
  }}

  // Layout components
  publicLayout={{
    component: PublicLayout,
    enabledPath: ['/']
  }}
  privateLayout={{
    component: PrivateLayout,
    enabledPath: ['/dashboard', '/profile']
  }}
  adminLayout={{
    component: AdminLayout,
    enabledPath: '/admin'
  }}

  // Fullscreen pages without layout wrapper
  noLayoutPaths={['/private/terminal', '/embed']}
>
  {children}
</AppLayout>
```

**Tags:** layout, router, smart, auto-detect, public, private, admin, fullscreen, noLayoutPaths

---

### AuthDialog

Event-driven dialog that prompts users to authenticate

**Import:**
```tsx
import { AuthDialog, DIALOG_EVENTS } from '@djangocfg/layouts/snippets';
import { events } from '@djangocfg/ui-nextjs';
```

**Example:**
```tsx
// Add to your layout
<AuthDialog authPath="/auth" />

// Events - Trigger from anywhere
import { events } from '@djangocfg/ui-nextjs';

events.publish({
  type: DIALOG_EVENTS.OPEN_AUTH_DIALOG,
  payload: { message: 'Please sign in to continue' }
});

// Close dialog
events.publish({
  type: DIALOG_EVENTS.CLOSE_AUTH_DIALOG
});

// Or use the hook
import { useAuthDialog } from '@djangocfg/layouts/snippets';

function MyComponent() {
  const { openAuthDialog } = useAuthDialog();

  return (
    <button onClick={() => openAuthDialog('Custom message')}>
      Sign In
    </button>
  );
}
```

**Tags:** dialog, auth, authentication, modal, overlay, event-driven

---

### AuthLayout

Authentication layout with OTP and OAuth support

**Import:**
```tsx
import { AuthLayout } from '@djangocfg/layouts';
```

**Example:**
```tsx
<AuthLayout
  sourceUrl="https://example.com"
  supportUrl="/support"
  termsUrl="/terms"
  privacyUrl="/privacy"
  enablePhoneAuth={false}
  enableGithubAuth={true}
  redirectUrl="/dashboard"
  onOTPSuccess={() => {
    console.log('OTP authentication successful');
  }}
  onOAuthSuccess={(user, isNewUser, provider) => {
    console.log(provider + ' auth:', user);
  }}
  onError={(error) => {
    console.error('Auth error:', error);
  }}
>
  <div className="text-center mb-8">
    <h1>Welcome to My App</h1>
    <p>Sign in to continue</p>
  </div>
</AuthLayout>
```

**Tags:** layout, auth, authentication, login, otp, oauth, github

---

### BaseApp

Core providers wrapper with theme, auth, analytics, PWA, push, and more

**Import:**
```tsx
import { BaseApp } from '@djangocfg/layouts';
```

**Example:**
```tsx
<BaseApp
  theme={{
    defaultTheme: 'system',
    storageKey: 'app-theme'
  }}
  auth={{
    loginPath: '/auth'
  }}
  analytics={{
    googleTrackingId: process.env.NEXT_PUBLIC_GA_ID
  }}
  centrifugo={{
    enabled: true,
    autoConnect: false,
    url: process.env.NEXT_PUBLIC_CENTRIFUGO_URL
  }}
  pwaInstall={{
    enabled: true,
    showInstallHint: true,
    resetAfterDays: 3,
    logo: '/logo192.png'
  }}
  pushNotifications={{
    enabled: true,
    vapidPublicKey: process.env.NEXT_PUBLIC_VAPID_KEY || '',
    subscribeEndpoint: '/api/push/subscribe',
    requirePWA: true
  }}
  errorBoundary={{
    enabled: true
  }}
  mcpChat={{
    enabled: true,
    autoDetectEnvironment: true,
    position: 'bottom-right'
  }}
  swr={{
    revalidateOnFocus: true,
    revalidateOnReconnect: true
  }}
>
  {children}
</BaseApp>
```

**Tags:** layout, provider, theme, auth, analytics, centrifugo, pwa, push, error-boundary, mcp, chat, core

---

### PrivateLayout

Authenticated user layout with sidebar and header

**Import:**
```tsx
import { PrivateLayout } from '@djangocfg/layouts';
```

**Example:**
```tsx
<PrivateLayout
  sidebar={{
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Profile', href: '/profile', icon: User }
    ],
    homeHref: '/dashboard'
  }}
  header={{
    title: 'Dashboard',
    groups: [
      {
        title: 'Account',
        items: [
          { label: 'Profile', href: '/profile' },
          { label: 'Settings', href: '/settings' }
        ]
      }
    ],
    authPath: '/auth'
  }}
  contentPadding="default"
>
  <div>Your protected content</div>
</PrivateLayout>
```

**Tags:** layout, private, authenticated, sidebar, dashboard, responsive

---

### PublicFooter

Professional footer for public pages with social links and menu sections

**Import:**
```tsx
import { PublicFooter } from '@djangocfg/layouts';
```

**Example:**
```tsx
<PublicFooter
  siteName="My App"
  description="App description"
  variant="full"
  badge={{
    icon: Sparkles,
    text: 'Open Source'
  }}
  socialLinks={{
    github: 'https://github.com/...',
    twitter: 'https://twitter.com/...',
    linkedin: 'https://linkedin.com/...'
  }}
  menuSections={[
    {
      title: 'Product',
      items: [
        { label: 'Features', path: '/features' },
        { label: 'Pricing', path: '/pricing' }
      ]
    }
  ]}
  links={[
    { label: 'Privacy', path: '/privacy' },
    { label: 'Terms', path: '/terms' }
  ]}
  copyright="© 2024 My Company"
  credits={{
    text: 'Built with DjangoCFG',
    url: 'https://djangocfg.com'
  }}
/>
```

**Tags:** footer, navigation, public, social, links, menu, responsive

---

### PublicLayout

Complete public page layout with navigation and footer

**Import:**
```tsx
import { PublicLayout, PublicFooter } from '@djangocfg/layouts';
```

**Example:**
```tsx
<PublicLayout
  siteName="My App"
  navigation={[
    { label: 'Home', href: '/' },
    { label: 'Docs', href: '/docs' }
  ]}
>
  <main>Your content</main>
</PublicLayout>

<PublicFooter
  siteName="My App"
  description="App description"
  variant="full"
  socialLinks={{
    github: 'https://github.com/...',
    twitter: 'https://twitter.com/...'
  }}
  menuSections={[
    {
      title: 'Product',
      items: [
        { label: 'Features', path: '/features' }
      ]
    }
  ]}
/>
```

**Tags:** layout, public, navigation, footer, responsive

---

