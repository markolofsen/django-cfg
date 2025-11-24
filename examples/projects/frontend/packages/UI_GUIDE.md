# Django CFG UI v1.0.0

Comprehensive React UI library with 56+ components, 7 blocks, and 11 hooks built with Radix UI, Tailwind CSS v4, and TypeScript

## Tailwind CSS v4.0 Guidelines

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
- IMPORTANT: Arbitrary values like h-[80px] may NOT work in v4 due to changed syntax
- For fixed sizes: Use inline styles style={{ width: '80px', height: '80px' }} - always reliable
- Spacing utilities (h-20, p-4, etc.) require --spacing-* variables defined in @theme block before Tailwind import
- Import order is critical but hard to fix: changing order breaks other styles
- Use aspect-square for maintaining 1:1 ratio (circles, squares)
- Use overflow-hidden with rounded-full for perfect circles
- Avoid custom utilities like: section-padding, animate-*, shadow-brand
- Mobile-first approach with breakpoints: sm: (640px), md: (768px), lg: (1024px), xl: (1280px)
- Use CSS variables: var(--color-primary), var(--font-family-sans)

### Migration Steps
1. Update dependencies: npm install tailwindcss@latest postcss@latest
2. Replace JavaScript config with CSS @theme block
3. Update import directives: @import "tailwindcss"
4. Configure PostCSS: use @tailwindcss/postcss plugin
5. Test and refactor: remove custom utilities and use standard Tailwind classes

### Examples

#### CSS-First Configuration
Define theme using CSS custom properties

```css
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-family-sans: ui-sans-serif, system-ui, sans-serif;
  --spacing-20: 5rem; /* Required for h-20, w-20 to work */
}
```

#### Responsive Spacing
Mobile-first responsive padding and spacing

```css
<section className="py-16 sm:py-20 md:py-24 lg:py-32">
  <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl">
      Title
    </h1>
  </div>
</section>
```

#### Fixed Sizes with Inline Styles
Most reliable way to set exact dimensions in v4

```css
<Avatar
  className="aspect-square rounded-full overflow-hidden ring-1 ring-foreground/20"
  style={{ width: '80px', height: '80px' }}
>
  <AvatarImage src={avatar} alt="User" />
</Avatar>
```

#### Component Styling
Standard Tailwind classes for components

```css
<button className="px-6 py-3 bg-primary text-primary-foreground rounded-md shadow-lg hover:shadow-xl transition-all duration-300">
  Click me
</button>
```

## Forms (19)

### Label
Accessible label component for form inputs

```tsx
import { Label } from '@djangocfg/ui';

<div className="space-y-2">
  <Label htmlFor="email">Email address</Label>
  <Input id="email" type="email" placeholder="Enter your email" />
</div>
```

### Button
Interactive button with multiple variants, sizes, and loading state. Use ButtonLink for navigation.

```tsx
import { Button, ButtonLink } from '@djangocfg/ui';

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
<Button loading={false}>Save</Button>

// ButtonLink for navigation with Next.js Link
<ButtonLink href="/dashboard">Go to Dashboard</ButtonLink>
<ButtonLink href="/settings" variant="outline">Settings</ButtonLink>
```

### DownloadButton
Button with download functionality, status indicators, and authentication support

```tsx
import { DownloadButton } from '@djangocfg/ui';

// Simple download
<DownloadButton
  url="/api/files/report.pdf"
  filename="monthly-report.pdf"
>
  Download Report
</DownloadButton>

// With callbacks
<DownloadButton
  url="/api/export/users"
  method="POST"
  body={{ format: "csv" }}
  onDownloadStart={() => console.log("Starting...")}
  onDownloadComplete={(filename) => console.log("Done:", filename)}
  onDownloadError={(error) => console.error("Error:", error)}
>
  Export Users
</DownloadButton>

// Different variants
<DownloadButton url="/api/data" variant="outline" size="sm">
  Download Data
</DownloadButton>
```

### Input
Text input field with validation support

```tsx
import { Input } from '@djangocfg/ui';

<Input type="text" placeholder="Enter text..." />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" disabled />
```

### Checkbox
Checkbox with label support

```tsx
import { Checkbox, Label } from '@djangocfg/ui';

<div className="flex items-center gap-2">
  <Checkbox id="terms" />
  <Label htmlFor="terms">Accept terms and conditions</Label>
</div>
```

### RadioGroup
Radio button group for single selection

```tsx
import { RadioGroup, RadioGroupItem, Label } from '@djangocfg/ui';

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

### Select
Dropdown select component

```tsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@djangocfg/ui';

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

### Textarea
Multi-line text input

```tsx
import { Textarea } from '@djangocfg/ui';

<Textarea placeholder="Enter your message..." rows={4} />
```

### Switch
Toggle switch component

```tsx
import { Switch, Label } from '@djangocfg/ui';

<div className="flex items-center gap-2">
  <Switch id="notifications" />
  <Label htmlFor="notifications">Enable notifications</Label>
</div>
```

### Slider
Range slider input

```tsx
import { Slider } from '@djangocfg/ui';

<Slider defaultValue={[50]} max={100} step={1} className="w-[200px]" />
```

### Combobox
Searchable dropdown with autocomplete

```tsx
import { Combobox } from '@djangocfg/ui';

<Combobox
  options={[
    { value: "javascript", label: "JavaScript" },
    { value: "typescript", label: "TypeScript" },
    { value: "python", label: "Python" },
    { value: "rust", label: "Rust" },
  ]}
  placeholder="Select language..."
  searchPlaceholder="Search language..."
  emptyText="No language found."
/>
```

### MultiSelect
Multi-select dropdown with badges and search functionality

```tsx
import { MultiSelect } from '@djangocfg/ui';

<MultiSelect
  options={[
    { value: "react", label: "React", description: "A JavaScript library for building user interfaces" },
    { value: "vue", label: "Vue", description: "The Progressive JavaScript Framework" },
    { value: "angular", label: "Angular", description: "Platform for building web applications" },
    { value: "svelte", label: "Svelte", description: "Cybernetically enhanced web apps" },
    { value: "next", label: "Next.js", description: "The React Framework for Production" },
  ]}
  placeholder="Select frameworks..."
  searchPlaceholder="Search frameworks..."
  emptyText="No framework found."
  maxDisplay={2}
  onChange={(value) => console.log('Selected:', value)}
/>
```

### MultiSelectPro
Advanced multi-select with animations, custom styling, grouped options, and comprehensive accessibility. Supports variants, icons, gradients, responsive design, and imperative control via ref.

```tsx
import { MultiSelectPro } from '@djangocfg/ui';

import { MultiSelectPro } from '@djangocfg/ui';
import type { MultiSelectProOption } from '@djangocfg/ui';
import { useState } from 'react';

// Basic usage
const [selected, setSelected] = useState<string[]>([]);

<MultiSelectPro
  options={[
    { value: "react", label: "React" },
    { value: "vue", label: "Vue.js" },
    { value: "angular", label: "Angular" },
  ]}
  onValueChange={setSelected}
  defaultValue={selected}
  placeholder="Select frameworks..."
/>

// With custom styling and icons
const styledOptions = [
  {
    value: "react",
    label: "React",
    style: {
      badgeColor: "#61DAFB",
      iconColor: "#282C34",
    },
  },
  {
    value: "vue",
    label: "Vue.js",
    style: {
      gradient: "linear-gradient(135deg, #4FC08D 0%, #42B883 100%)",
    },
  },
];

<MultiSelectPro
  options={styledOptions}
  onValueChange={setSelected}
  variant="secondary"
  animationConfig={{
    badgeAnimation: "bounce",
    popoverAnimation: "scale",
    duration: 0.3,
  }}
  maxCount={3}
  closeOnSelect={false}
/>

// With grouped options
const groupedOptions = [
  {
    heading: "Frontend Frameworks",
    options: [
      { value: "react", label: "React" },
      { value: "vue", label: "Vue.js" },
      { value: "angular", label: "Angular", disabled: true },
    ],
  },
  {
    heading: "Backend Technologies",
    options: [
      { value: "node", label: "Node.js" },
      { value: "python", label: "Python" },
    ],
  },
];

<MultiSelectPro
  options={groupedOptions}
  onValueChange={setSelected}
  placeholder="Select technologies..."
  searchable={true}
  responsive={true}
  minWidth="200px"
  maxWidth="500px"
/>

// With imperative control via ref
import { useRef } from 'react';
import type { MultiSelectProRef } from '@djangocfg/ui';

const ref = useRef<MultiSelectProRef>(null);

// Later in code:
ref.current?.clear();
ref.current?.reset();
ref.current?.setSelectedValues(['react', 'vue']);
const values = ref.current?.getSelectedValues();
```

### MultiSelectProAsync
Async multi-select with external API search, debouncing, and loading states. Perfect for large datasets and server-side filtering.

```tsx
import { MultiSelectProAsync, useDebounce } from '@djangocfg/ui';

import { MultiSelectProAsync, useDebounce } from '@djangocfg/ui';
import { useState, useEffect } from 'react';

// Mock API function (replace with your actual API)
const searchAPI = async (query: string) => {
  const response = await fetch(`/api/search?q=${query}`);
  return response.json();
};

function AsyncExample() {
  const [searchValue, setSearchValue] = useState('');
  const [options, setOptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);

  // Debounce search to reduce API calls
  const debouncedSearch = useDebounce(searchValue, 300);

  // Fetch options when debounced search changes
  useEffect(() => {
    if (!debouncedSearch) {
      setOptions([]);
      return;
    }

    const fetchOptions = async () => {
      setIsLoading(true);
      try {
        const results = await searchAPI(debouncedSearch);
        setOptions(results);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOptions();
  }, [debouncedSearch]);

  return (
    <MultiSelectProAsync
      // Search control (managed by parent)
      searchValue={searchValue}
      onSearchChange={setSearchValue}
      isLoading={isLoading}

      // Options from API
      options={options}

      // Selection
      onValueChange={setSelected}
      defaultValue={selected}

      // UI
      placeholder="Search and select..."
      searchPlaceholder="Type to search..."
      emptyText="No results found"
      loadingText="Searching..."

      // Features
      variant="default"
      maxCount={3}
      closeOnSelect={false}
    />
  );
}
```

### InputOTP
One-time password input component

```tsx
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@djangocfg/ui';

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

### PhoneInput
International phone number input with country selector

```tsx
import { PhoneInput } from '@djangocfg/ui';

<PhoneInput
  defaultCountry="US"
  placeholder="Enter phone number"
  className="max-w-sm"
/>
```

### Form
React Hook Form wrapper with form validation

```tsx
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@djangocfg/ui';

// Requires react-hook-form
import { useForm } from 'react-hook-form';

function MyForm() {
  const form = useForm();

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Enter username" {...field} />
              </FormControl>
              <FormDescription>
                Your public display name
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
}
```

### Field
Advanced field component with label, description and validation

```tsx
import { Field, FieldGroup, FieldSet, FieldLegend } from '@djangocfg/ui';

<FieldSet>
  <FieldLegend>Account Information</FieldLegend>
  <FieldGroup>
    <Field>
      <FieldLabel>Username</FieldLabel>
      <Input placeholder="Enter username" />
      <FieldDescription>
        Your unique username for the platform
      </FieldDescription>
      <FieldError>Username is required</FieldError>
    </Field>
  </FieldGroup>
</FieldSet>
```

### JsonSchemaForm
Automatic form generator from JSON Schema with validation, custom widgets, and full type safety

```tsx
import { JsonSchemaForm } from '@djangocfg/ui/tools';

// Basic usage
const schema = {
  type: 'object',
  required: ['name', 'email'],
  properties: {
    name: {
      type: 'string',
      title: 'Full Name',
      minLength: 2
    },
    email: {
      type: 'string',
      title: 'Email',
      format: 'email'
    },
    age: {
      type: 'number',
      title: 'Age',
      minimum: 18
    },
    subscribe: {
      type: 'boolean',
      title: 'Subscribe to newsletter'
    }
  }
};

<JsonSchemaForm
  schema={schema}
  onSubmit={(data) => console.log(data.formData)}
  liveValidate={false}
/>

// With UI Schema for customization
const uiSchema = {
  subscribe: {
    'ui:widget': 'SwitchWidget'
  }
};

<JsonSchemaForm
  schema={schema}
  uiSchema={uiSchema}
  formData={initialData}
  onChange={(data) => setFormData(data.formData)}
  onSubmit={handleSubmit}
/>
```

## Layout (8)

### Card
Container with header, content, and footer sections

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@djangocfg/ui';

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>This is the main content of the card.</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

### Separator
Visual divider between sections

```tsx
import { Separator } from '@djangocfg/ui';

<div>
  <p>Section 1</p>
  <Separator className="my-4" />
  <p>Section 2</p>
</div>
```

### Skeleton
Loading placeholder animation

```tsx
import { Skeleton } from '@djangocfg/ui';

<div className="space-y-3">
  <Skeleton className="w-full h-12" />
  <Skeleton className="w-3/4 h-8" />
  <Skeleton className="w-1/2 h-8" />
</div>
```

### AspectRatio
Maintain aspect ratio for content

```tsx
import { AspectRatio } from '@djangocfg/ui';

<AspectRatio ratio={16/9} className="bg-muted">
  <img src="/demo.jpg" alt="Demo" className="object-cover rounded-md" />
</AspectRatio>
```

### Sticky
Make content sticky on scroll

```tsx
import { Sticky } from '@djangocfg/ui';

<Sticky offsetTop={0} disableOnMobile={false}>
  <nav className="bg-background border p-4">
    Sticky Navigation
  </nav>
</Sticky>
```

### ScrollArea
Custom scrollable area with styled scrollbar

```tsx
import { ScrollArea, ScrollBar } from '@djangocfg/ui';

<ScrollArea className="h-[200px] w-[350px] rounded-md border p-4">
  <div className="space-y-4">
    {Array.from({ length: 20 }).map((_, i) => (
      <div key={i} className="text-sm">
        Content item {i + 1}
      </div>
    ))}
  </div>
  <ScrollBar orientation="vertical" />
</ScrollArea>
```

### Resizable
Resizable panel layout with draggable handles

```tsx
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@djangocfg/ui';

<ResizablePanelGroup direction="horizontal" className="max-w-md rounded-lg border">
  <ResizablePanel defaultSize={50}>
    <div className="flex h-[200px] items-center justify-center p-6">
      <span className="font-semibold">Panel One</span>
    </div>
  </ResizablePanel>
  <ResizableHandle />
  <ResizablePanel defaultSize={50}>
    <div className="flex h-[200px] items-center justify-center p-6">
      <span className="font-semibold">Panel Two</span>
    </div>
  </ResizablePanel>
</ResizablePanelGroup>
```

### Section
Semantic section container with header

```tsx
import { Section, SectionHeader } from '@djangocfg/ui';

<Section>
  <SectionHeader
    title="Section Title"
    description="Section description goes here"
  />
  <div className="p-4">
    Section content goes here...
  </div>
</Section>
```

## Navigation (7)

### NavigationMenu
Accessible navigation menu with dropdown support and Next.js router integration

```tsx
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from '@djangocfg/ui';

<NavigationMenu>
  <NavigationMenuList>
    <NavigationMenuItem>
      <NavigationMenuTrigger>Getting started</NavigationMenuTrigger>
      <NavigationMenuContent>
        <ul className="grid gap-3 p-6 md:w-[400px]">
          <li>
            {/* NavigationMenuLink with href uses Next.js Link automatically */}
            <NavigationMenuLink href="/">
              <div className="text-sm font-medium">Welcome</div>
              <p className="text-sm text-muted-foreground">
                Get started with our components
              </p>
            </NavigationMenuLink>
          </li>
        </ul>
      </NavigationMenuContent>
    </NavigationMenuItem>
    <NavigationMenuItem>
      {/* Direct link with client-side navigation */}
      <NavigationMenuLink href="/docs">
        Documentation
      </NavigationMenuLink>
    </NavigationMenuItem>
  </NavigationMenuList>
</NavigationMenu>
```

### Breadcrumb
Navigation breadcrumbs showing current page hierarchy with Next.js router support

```tsx
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@djangocfg/ui';

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      {/* BreadcrumbLink with href automatically uses Next.js Link */}
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/components">Components</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      {/* Current page - not a link */}
      <BreadcrumbPage>Breadcrumb</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Tabs
Tab navigation for switching between different views. Supports mobile sheet mode, sticky positioning, and auto-responsive behavior.

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';

// Basic tabs with equal-width tabs
<Tabs defaultValue="account" className="w-[400px]">
  <TabsList fullWidth>
    <TabsTrigger value="account" flexEqual>Account</TabsTrigger>
    <TabsTrigger value="password" flexEqual>Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    <div className="p-4 border rounded-md">
      <p className="text-sm">Make changes to your account here.</p>
    </div>
  </TabsContent>
  <TabsContent value="password">
    <div className="p-4 border rounded-md">
      <p className="text-sm">Change your password here.</p>
    </div>
  </TabsContent>
</Tabs>

// Mobile-responsive tabs with sticky positioning
<Tabs
  defaultValue="account"
  mobileSheet
  mobileTitleText="Settings"
  mobileSheetTitle="Navigation"
  sticky
>
  <TabsList fullWidth>
    <TabsTrigger value="account" flexEqual>Account</TabsTrigger>
    <TabsTrigger value="password" flexEqual>Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    Account content
  </TabsContent>
  <TabsContent value="password">
    Password content
  </TabsContent>
</Tabs>
```

### Pagination
Page navigation with previous/next controls and Next.js router support

```tsx
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@djangocfg/ui';

<Pagination>
  <PaginationContent>
    <PaginationItem>
      {/* Previous/Next with href automatically use Next.js Link */}
      <PaginationPrevious href="/page/1" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/page/1" isActive>1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/page/2">2</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="/page/3">3</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="/page/2" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

### BreadcrumbNavigation
Enhanced breadcrumb component with automatic path generation

```tsx
import { BreadcrumbNavigation } from '@djangocfg/ui';

<BreadcrumbNavigation
  items={[
    { label: "Home", href: "/" },
    { label: "Products", href: "/products" },
    { label: "Category", href: "/products/category" },
    { label: "Item", href: "/products/category/item" },
  ]}
/>
```

### SSRPagination
Server-side rendered pagination component

```tsx
import { SSRPagination } from '@djangocfg/ui';

<SSRPagination
  currentPage={2}
  totalPages={10}
  totalItems={100}
  itemsPerPage={10}
  hasNextPage={true}
  hasPreviousPage={true}
/>
```

### StaticPagination
Client-side pagination component for static builds with callback support

```tsx
import { StaticPagination } from '@djangocfg/ui';

import { useDRFPagination } from '@djangocfg/ui';

const pagination = useDRFPagination(1, 10);
const { data } = useMyAPI(pagination.params);

<StaticPagination
  data={data}
  onPageChange={pagination.setPage}
/>
```

## Overlay (11)

### Dialog
Modal dialog for important user interactions

```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Button,
} from '@djangocfg/ui';

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button type="submit">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### AlertDialog
Confirmation dialog for critical actions

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
  Button,
} from '@djangocfg/ui';

<AlertDialog>
  <AlertDialogTrigger asChild>
    <Button variant="destructive">Delete Account</Button>
  </AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone. This will permanently delete your
        account and remove your data from our servers.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

### Sheet
Slide-out panel from the edge of the screen

```tsx
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  Button,
} from '@djangocfg/ui';

<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open Sheet</Button>
  </SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Edit profile</SheetTitle>
      <SheetDescription>
        Make changes to your profile here.
      </SheetDescription>
    </SheetHeader>
    <div className="grid gap-4 py-4">
      <p>Sheet content goes here.</p>
    </div>
    <SheetFooter>
      <SheetClose asChild>
        <Button type="submit">Save changes</Button>
      </SheetClose>
    </SheetFooter>
  </SheetContent>
</Sheet>
```

### Drawer
Mobile-friendly drawer component

```tsx
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  Button,
} from '@djangocfg/ui';

<Drawer>
  <DrawerTrigger asChild>
    <Button variant="outline">Open Drawer</Button>
  </DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Are you sure?</DrawerTitle>
      <DrawerDescription>This action cannot be undone.</DrawerDescription>
    </DrawerHeader>
    <DrawerFooter>
      <Button>Submit</Button>
      <DrawerClose asChild>
        <Button variant="outline">Cancel</Button>
      </DrawerClose>
    </DrawerFooter>
  </DrawerContent>
</Drawer>
```

### Popover
Floating popover with rich content

```tsx
import { Popover, PopoverContent, PopoverTrigger, Button } from '@djangocfg/ui';

<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">Open Popover</Button>
  </PopoverTrigger>
  <PopoverContent className="w-80">
    <div className="grid gap-4">
      <div className="space-y-2">
        <h4 className="font-medium leading-none">Dimensions</h4>
        <p className="text-sm text-muted-foreground">
          Set the dimensions for the layer.
        </p>
      </div>
    </div>
  </PopoverContent>
</Popover>
```

### HoverCard
Card that appears on hover with additional information

```tsx
import { HoverCard, HoverCardContent, HoverCardTrigger, Button } from '@djangocfg/ui';

<HoverCard>
  <HoverCardTrigger asChild>
    <Button variant="link">@nextjs</Button>
  </HoverCardTrigger>
  <HoverCardContent className="w-80">
    <div className="flex justify-between space-x-4">
      <div className="space-y-1">
        <h4 className="text-sm font-semibold">@nextjs</h4>
        <p className="text-sm">
          The React Framework – created and maintained by @vercel.
        </p>
      </div>
    </div>
  </HoverCardContent>
</HoverCard>
```

### Tooltip
Simple tooltip that appears on hover

```tsx
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger, Button } from '@djangocfg/ui';

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Add to library</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### Command
Command palette for quick actions and navigation

```tsx
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@djangocfg/ui';

<Command className="rounded-lg border shadow-md">
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search Emoji</CommandItem>
      <CommandItem>Calculator</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

### ContextMenu
Right-click context menu

```tsx
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from '@djangocfg/ui';

<ContextMenu>
  <ContextMenuTrigger className="flex h-[150px] w-[300px] items-center justify-center rounded-md border border-dashed text-sm">
    Right click here
  </ContextMenuTrigger>
  <ContextMenuContent className="w-64">
    <ContextMenuItem>Back</ContextMenuItem>
    <ContextMenuItem>Forward</ContextMenuItem>
    <ContextMenuItem>Reload</ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>
```

### DropdownMenu
Dropdown menu for actions and options with Next.js router support

```tsx
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Button,
} from '@djangocfg/ui';

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open Menu</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent className="w-56">
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    {/* DropdownMenuItem with href automatically uses Next.js Link */}
    <DropdownMenuItem href="/profile">Profile</DropdownMenuItem>
    <DropdownMenuItem href="/billing">Billing</DropdownMenuItem>
    <DropdownMenuItem href="/settings">Settings</DropdownMenuItem>
    <DropdownMenuSeparator />
    {/* Without href - for actions */}
    <DropdownMenuItem onClick={() => console.log('Logout')}>
      Logout
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

### Menubar
Application menubar with multiple menu groups and Next.js router support

```tsx
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarTrigger,
} from '@djangocfg/ui';

<Menubar>
  <MenubarMenu>
    <MenubarTrigger>File</MenubarTrigger>
    <MenubarContent>
      {/* MenubarItem with href automatically uses Next.js Link */}
      <MenubarItem href="/new">New Tab</MenubarItem>
      <MenubarItem href="/window">New Window</MenubarItem>
      <MenubarSeparator />
      <MenubarItem href="/share">Share</MenubarItem>
      <MenubarSeparator />
      {/* Without href - for actions */}
      <MenubarItem onClick={() => window.print()}>Print</MenubarItem>
    </MenubarContent>
  </MenubarMenu>
  <MenubarMenu>
    <MenubarTrigger>Edit</MenubarTrigger>
    <MenubarContent>
      <MenubarItem onClick={() => document.execCommand('undo')}>Undo</MenubarItem>
      <MenubarItem onClick={() => document.execCommand('redo')}>Redo</MenubarItem>
    </MenubarContent>
  </MenubarMenu>
</Menubar>
```

## Feedback (6)

### Toast
Toast notifications for user feedback

```tsx
import { useToast, Button } from '@djangocfg/ui';

function Component() {
  const { toast } = useToast();

  return (
    <div className="space-x-2">
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
      <Button
        variant="destructive"
        onClick={() => {
          toast({
            variant: "destructive",
            title: "Error!",
            description: "Something went wrong.",
          });
        }}
      >
        Show Error Toast
      </Button>
    </div>
  );
}
```

### Alert
Alert messages for important information

```tsx
import { Alert, AlertDescription, AlertTitle } from '@djangocfg/ui';

<div className="space-y-4">
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
</div>
```

### Progress
Progress bar for showing completion status

```tsx
import { Progress } from '@djangocfg/ui';

<div className="space-y-4 max-w-md">
  <div>
    <div className="flex justify-between mb-2">
      <span className="text-sm">25%</span>
    </div>
    <Progress value={25} />
  </div>

  <div>
    <div className="flex justify-between mb-2">
      <span className="text-sm">50%</span>
    </div>
    <Progress value={50} />
  </div>

  <div>
    <div className="flex justify-between mb-2">
      <span className="text-sm">75%</span>
    </div>
    <Progress value={75} />
  </div>
</div>
```

### Badge
Status badges for labels and categories

```tsx
import { Badge } from '@djangocfg/ui';

<div className="flex gap-2 flex-wrap">
  <Badge>Default</Badge>
  <Badge variant="secondary">Secondary</Badge>
  <Badge variant="destructive">Destructive</Badge>
  <Badge variant="outline">Outline</Badge>
</div>
```

### Avatar
User avatar with fallback support

```tsx
import { Avatar, AvatarFallback, AvatarImage } from '@djangocfg/ui';

<div className="flex gap-4">
  <Avatar>
    <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
    <AvatarFallback>CN</AvatarFallback>
  </Avatar>

  <Avatar>
    <AvatarImage src="/nonexistent.png" alt="@user" />
    <AvatarFallback>JD</AvatarFallback>
  </Avatar>

  <Avatar>
    <AvatarFallback>AB</AvatarFallback>
  </Avatar>
</div>
```

### Toaster
Global toast notification container (works with Toast component)

```tsx
import { Toaster, useToast } from '@djangocfg/ui';

// Add Toaster once in your app layout
<Toaster />

// Then use the useToast hook anywhere
function MyComponent() {
  const { toast } = useToast();

  return (
    <Button
      onClick={() => {
        toast({
          title: "Scheduled: Catch up",
          description: "Friday, February 10, 2023 at 5:57 PM",
        });
      }}
    >
      Show Toast
    </Button>
  );
}
```

## Data (8)

### Table
Responsive data table component

```tsx
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@djangocfg/ui';

<Table>
  <TableCaption>A list of your recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Method</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">INV001</TableCell>
      <TableCell>Paid</TableCell>
      <TableCell>Credit Card</TableCell>
      <TableCell className="text-right">$250.00</TableCell>
    </TableRow>
    <TableRow>
      <TableCell className="font-medium">INV002</TableCell>
      <TableCell>Pending</TableCell>
      <TableCell>PayPal</TableCell>
      <TableCell className="text-right">$150.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Accordion
Vertically stacked set of collapsible sections

```tsx
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@djangocfg/ui';

<Accordion type="single" collapsible className="w-full">
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>
      Yes. It comes with default styles that matches the aesthetic.
    </AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-3">
    <AccordionTrigger>Is it animated?</AccordionTrigger>
    <AccordionContent>
      Yes. It's animated by default, but you can disable it if you prefer.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

### Collapsible
Simple collapsible content panel

```tsx
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@djangocfg/ui';

<Collapsible className="w-full max-w-md space-y-2">
  <CollapsibleTrigger className="flex items-center justify-between w-full p-4 bg-muted rounded-md">
    <span className="font-medium">Can I use this in my project?</span>
    <ChevronDown className="h-4 w-4" />
  </CollapsibleTrigger>
  <CollapsibleContent className="p-4 bg-muted/50 rounded-md">
    <p className="text-sm text-muted-foreground">
      Yes! This component is free to use in your projects.
    </p>
  </CollapsibleContent>
</Collapsible>
```

### Toggle
Two-state button for on/off interactions

```tsx
import { Toggle } from '@djangocfg/ui';

<div className="flex gap-2">
  <Toggle aria-label="Toggle bold">
    <Bold className="h-4 w-4" />
  </Toggle>
  <Toggle aria-label="Toggle italic">
    <Italic className="h-4 w-4" />
  </Toggle>
  <Toggle aria-label="Toggle underline">
    <Underline className="h-4 w-4" />
  </Toggle>
</div>
```

### ToggleGroup
Group of toggle buttons with single or multiple selection

```tsx
import { ToggleGroup, ToggleGroupItem } from '@djangocfg/ui';

<div className="space-y-4">
  <div>
    <p className="text-sm font-medium mb-2">Single Selection</p>
    <ToggleGroup type="single">
      <ToggleGroupItem value="bold" aria-label="Toggle bold">
        <Bold className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="italic" aria-label="Toggle italic">
        <Italic className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="underline" aria-label="Toggle underline">
        <Underline className="h-4 w-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  </div>

  <div>
    <p className="text-sm font-medium mb-2">Multiple Selection</p>
    <ToggleGroup type="multiple">
      <ToggleGroupItem value="bold" aria-label="Toggle bold">
        <Bold className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="italic" aria-label="Toggle italic">
        <Italic className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="underline" aria-label="Toggle underline">
        <Underline className="h-4 w-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  </div>
</div>
```

### Calendar
Date picker calendar component

```tsx
import { Calendar } from '@djangocfg/ui';

<Calendar
  mode="single"
  selected={date}
  onSelect={setDate}
  className="rounded-md border"
/>
```

### Carousel
Image and content carousel with navigation

```tsx
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@djangocfg/ui';

<Carousel className="w-full max-w-xs">
  <CarouselContent>
    <CarouselItem>
      <div className="p-6 border rounded-md">
        <span className="text-4xl font-semibold">1</span>
      </div>
    </CarouselItem>
    <CarouselItem>
      <div className="p-6 border rounded-md">
        <span className="text-4xl font-semibold">2</span>
      </div>
    </CarouselItem>
    <CarouselItem>
      <div className="p-6 border rounded-md">
        <span className="text-4xl font-semibold">3</span>
      </div>
    </CarouselItem>
  </CarouselContent>
  <CarouselPrevious />
  <CarouselNext />
</Carousel>
```

### Chart
Data visualization charts powered by Recharts

```tsx
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@djangocfg/ui';

import { Bar, BarChart, XAxis, YAxis } from 'recharts';

const chartConfig = {
  sales: { label: "Sales", color: "hsl(var(--chart-1))" },
  profit: { label: "Profit", color: "hsl(var(--chart-2))" },
};

const chartData = [
  { month: "Jan", sales: 400, profit: 240 },
  { month: "Feb", sales: 300, profit: 180 },
  { month: "Mar", sales: 500, profit: 300 },
];

<ChartContainer config={chartConfig} className="min-h-[200px] w-full">
  <BarChart data={chartData}>
    <XAxis dataKey="month" />
    <YAxis />
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="sales" fill="var(--color-sales)" />
    <Bar dataKey="profit" fill="var(--color-profit)" />
  </BarChart>
</ChartContainer>
```

## Specialized (10)

### Sidebar
Full-featured sidebar navigation component (23KB) with collapsible groups, icons, and Next.js router support

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
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@djangocfg/ui';

// SidebarMenuButton with href automatically uses Next.js Link
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
          <SidebarMenuItem>
            <SidebarMenuButton href="/users" tooltip="Users">
              <UsersIcon />
              <span>Users</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>

    <SidebarGroup>
      <SidebarGroupLabel>Settings</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton href="/settings">
              <SettingsIcon />
              <span>Preferences</span>
            </SidebarMenuButton>
            {/* Submenu items also support href */}
            <SidebarMenuSub>
              <SidebarMenuSubItem>
                <SidebarMenuSubButton href="/settings/profile">
                  Profile
                </SidebarMenuSubButton>
              </SidebarMenuSubItem>
            </SidebarMenuSub>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>
</Sidebar>
```

### ImageWithFallback
Enhanced image component with loading states and fallback support

```tsx
import { ImageWithFallback } from '@djangocfg/ui';

<div className="space-y-4">
  {/* Successful load */}
  <ImageWithFallback
    src="/images/example.jpg"
    alt="Example image"
    width={300}
    height={200}
    className="rounded-md"
  />

  {/* With fallback */}
  <ImageWithFallback
    src="/invalid-image.jpg"
    alt="Image with fallback"
    fallbackSrc="/images/placeholder.jpg"
    width={300}
    height={200}
    className="rounded-md"
  />

  {/* Custom loading state */}
  <ImageWithFallback
    src="/large-image.jpg"
    alt="Loading example"
    width={300}
    height={200}
    className="rounded-md"
    loadingComponent={
      <div className="flex items-center justify-center h-full">
        <Spinner />
      </div>
    }
  />
</div>
```

### ButtonGroup
Group buttons together with shared borders

```tsx
import { ButtonGroup, Button } from '@djangocfg/ui';

<ButtonGroup orientation="horizontal">
  <Button variant="outline">Left</Button>
  <Button variant="outline">Center</Button>
  <Button variant="outline">Right</Button>
</ButtonGroup>
```

### Empty
Empty state component for no data scenarios

```tsx
import { Empty, EmptyHeader, EmptyTitle, EmptyDescription, EmptyContent, EmptyMedia } from '@djangocfg/ui';

<Empty>
  <EmptyHeader>
    <EmptyMedia>
      <svg>...</svg>
    </EmptyMedia>
    <EmptyTitle>No results found</EmptyTitle>
    <EmptyDescription>
      Try adjusting your search or filter to find what you're looking for.
    </EmptyDescription>
  </EmptyHeader>
  <EmptyContent>
    <Button>Clear filters</Button>
  </EmptyContent>
</Empty>
```

### Spinner
Loading spinner indicator

```tsx
import { Spinner } from '@djangocfg/ui';

<div className="flex gap-4 items-center">
  <Spinner />
  <Spinner className="size-6" />
  <Spinner className="size-8" />
</div>
```

### Kbd
Keyboard key display component

```tsx
import { Kbd } from '@djangocfg/ui';

<div className="flex gap-2">
  <Kbd>⌘</Kbd>
  <Kbd>K</Kbd>
</div>
```

### TokenIcon
Cryptocurrency token icon component

```tsx
import { TokenIcon } from '@djangocfg/ui';

<div className="flex gap-4">
  <TokenIcon symbol="btc" size={32} />
  <TokenIcon symbol="eth" size={32} />
  <TokenIcon symbol="usdt" size={32} />
</div>
```

### Sonner (Toaster)
Toast notifications powered by Sonner library

```tsx
import { Toaster } from '@djangocfg/ui';
import { toast } from 'sonner';

// Add Toaster to your app layout
<Toaster />

// Then use toast anywhere in your app
toast.success('Operation completed!');
toast.error('Something went wrong');
toast.info('New message received');
toast.promise(
  fetchData(),
  {
    loading: 'Loading...',
    success: 'Data loaded!',
    error: 'Failed to load',
  }
);
```

### InputGroup
Enhanced input with prefix/suffix addons

```tsx
import { InputGroup, Input } from '@djangocfg/ui';

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

### Item
List item component with variants and layouts

```tsx
import { Item, ItemGroup } from '@djangocfg/ui';

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

## Tools (4)

### JsonTree
Interactive JSON tree viewer with expand/collapse, search, and export functionality

```tsx
import { JsonTree } from '@djangocfg/ui';

<JsonTree
  title="User Data"
  data={{
    user: {
      id: 1,
      name: "John Doe",
      email: "john@example.com",
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

### PrettyCode
Syntax-highlighted code display with automatic language detection and theme support

```tsx
import { PrettyCode } from '@djangocfg/ui';

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

### Mermaid
Interactive Mermaid diagram renderer with fullscreen view and theme support

```tsx
import { Mermaid } from '@djangocfg/ui';

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

// Flowchart
<Mermaid
  chart={`
    flowchart LR
      A[Hard edge] -->|Link text| B(Round edge)
      B --> C{Decision}
      C -->|One| D[Result one]
      C -->|Two| E[Result two]
  `}
/>
```

### LottiePlayer
Lottie animation player with size presets and playback controls

```tsx
import { LottiePlayer } from '@djangocfg/ui';

<LottiePlayer
  src="https://lottie.host/embed/a0eb3923-2f93-4a2e-9c91-3e0b0f6f3b3e/WHJEbMDJLn.json"
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

## Blocks (7)

### Hero
Hero section with title, description, and CTAs

```tsx
import { Hero } from '@djangocfg/ui/blocks';

<Hero
  title="Build Your Next Project"
  description="The best way to create modern web applications with React and TypeScript"
  primaryAction={{ label: "Get Started", href: "/docs" }}
  secondaryAction={{ label: "View Demo", href: "/demo" }}
/>
```

### SuperHero
Enhanced hero with badge, gradient title, features, and stats

```tsx
import { SuperHero } from '@djangocfg/ui/blocks';

<SuperHero
  badge={{ icon: <Sparkles />, text: "New in v2.0" }}
  title="Next-Generation"
  titleGradient="Development Platform"
  subtitle="Build faster with our comprehensive UI library"
  features={[
    { icon: <span>⚛️</span>, text: "React 19" },
    { icon: <span>📘</span>, text: "TypeScript" },
    { icon: <span>🎨</span>, text: "Tailwind CSS 4" },
    { icon: <span>⚡</span>, text: "Lightning Fast" }
  ]}
  primaryAction={{ label: "Start Building", href: "/start" }}
  secondaryAction={{ label: "Learn More", href: "/docs", icon: <BookOpen /> }}
  stats={[
    { number: "56+", label: "Components" },
    { number: "7", label: "Blocks" },
    { number: "6", label: "Hooks" },
    { number: "100%", label: "Type Safe" }
  ]}
  backgroundVariant="waves"
  backgroundIntensity="medium"
  showBackgroundSwitcher={true}
/>
```

### FeatureSection
Grid of features with icons and descriptions

```tsx
import { FeatureSection } from '@djangocfg/ui/blocks';

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

### CTASection
Call-to-action section to drive conversions

```tsx
import { CTASection } from '@djangocfg/ui/blocks';

<CTASection
  title="Ready to Get Started?"
  subtitle="Join thousands of developers building amazing products"
  primaryCTA={{ label: "Start Free Trial", href: "/signup" }}
  secondaryCTA={{ label: "Contact Sales", href: "/contact" }}
/>
```

### NewsletterSection
Email capture section for newsletters

```tsx
import { NewsletterSection } from '@djangocfg/ui/blocks';

<NewsletterSection
  title="Stay Updated"
  description="Get the latest news delivered to your inbox"
  placeholder="Enter your email"
  buttonText="Subscribe"
  onSubmit={(email) => console.log(email)}
/>
```

### StatsSection
Display key metrics and statistics

```tsx
import { StatsSection } from '@djangocfg/ui/blocks';

<StatsSection
  title="Our Impact"
  stats={[
    { icon: <Users className="w-6 h-6" />, number: "10K+", label: "Active Users" },
    { icon: <Building2 className="w-6 h-6" />, number: "500+", label: "Companies" },
    { icon: <TrendingUp className="w-6 h-6" />, number: "99.9%", label: "Uptime" },
    { icon: <Headphones className="w-6 h-6" />, number: "24/7", label: "Support" }
  ]}
/>
```

### TestimonialSection
Customer testimonials and reviews

```tsx
import { TestimonialSection } from '@djangocfg/ui/blocks';

<TestimonialSection
  title="What Our Customers Say"
  testimonials={[{
    content: "This product changed how we work!",
    author: {
      name: "John Doe",
      title: "CEO",
      company: "Company"
    }
  }]}
/>
```

## Hooks (6)

### useMediaQuery
Responsive media query hook

```tsx
import { useMediaQuery } from '@djangocfg/ui';

const isMobile = useMediaQuery('(max-width: 768px)');
const isDesktop = useMediaQuery('(min-width: 1024px)');

return isMobile ? <MobileView /> : <DesktopView />;
```

### useTheme
Theme management hook

```tsx
import { useTheme } from '@djangocfg/ui';

const theme = useTheme(); // Returns 'light' | 'dark'

// Toggle theme manually
document.documentElement.classList.toggle('dark');
```

### useCopy
Copy to clipboard hook

```tsx
import { useCopy } from '@djangocfg/ui';

const { copyToClipboard } = useCopy();
const [copied, setCopied] = useState(false);

const handleCopy = async () => {
  await copyToClipboard('text to copy');
  setCopied(true);
};
```

### useCountdown
Countdown timer hook

```tsx
import { useCountdown } from '@djangocfg/ui';

const targetDate = new Date('2025-12-31').toISOString();
const countdown = useCountdown(targetDate);

// Returns: { days, hours, minutes, seconds, isExpired }
```

### useDebounce
Debounce value changes to reduce API calls and improve performance. Perfect for search inputs and form fields.

```tsx
import { useDebounce } from '@djangocfg/ui';

// Basic search debouncing
const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 300); // Default 300ms

useEffect(() => {
  if (debouncedSearch) {
    // API call only fires 300ms after user stops typing
    fetchResults(debouncedSearch);
  }
}, [debouncedSearch]);

// With MultiSelectPro (has built-in search)
const [searchValue, setSearchValue] = useState('');
const debouncedSearchValue = useDebounce(searchValue, 500);

useEffect(() => {
  // Fetch options from API with debounced search
  if (debouncedSearchValue) {
    fetchOptions(debouncedSearchValue);
  }
}, [debouncedSearchValue]);

<MultiSelectPro
  options={filteredOptions}
  onValueChange={setSelected}
  placeholder="Search and select..."
  searchable={true}
  // ... other props
/>
```

### useIsMobile
Check if device is mobile

```tsx
import { useIsMobile } from '@djangocfg/ui';

const isMobile = useIsMobile(); // Boolean

return isMobile ? <MobileMenu /> : <DesktopMenu />;
```

