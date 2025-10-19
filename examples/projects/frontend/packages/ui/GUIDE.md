# 🧩 @djangocfg/ui - UI Component Library

## 🎯 Overview

Modern React UI component library built with:
- **Next.js 15.5.4** + **React 19**
- **Radix UI** primitives
- **Tailwind CSS 4**
- **TypeScript**
- Full **dark mode** support

---

## 📦 Installation

```bash
# In workspace (recommended)
"@djangocfg/ui": "workspace:*"

# With npm
"@djangocfg/ui": "*"
```

---

## 🚀 Usage

### Import Components

```tsx
import { Button, Card, Dialog } from '@djangocfg/ui';
import { useToast, useLocalStorage } from '@djangocfg/ui';
import { DashboardLayout } from '@djangocfg/ui';
```

### Tailwind Config

```ts
import uiConfig from '@djangocfg/ui/tailwind.config';

export default {
  darkMode: "class",
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    ...uiConfig.theme,
    extend: {
      ...uiConfig.theme?.extend,
      // Your overrides
    },
  },
  plugins: [
    ...(uiConfig.plugins || []),
    // Your plugins
  ],
};
```

### Styles

```tsx
// app/layout.tsx or _app.tsx
import '@djangocfg/ui/styles';
```

---

## 📚 Components

### Form Components
- **Button** / **ButtonLink** - Versatile button with variants (default, destructive, outline, secondary, ghost, link)
- **Input** - Form input
- **Textarea** - Multi-line input
- **Label** - Accessible label
- **Checkbox** - Checkbox input
- **RadioGroup** - Radio button group
- **Select** - Dropdown select
- **Switch** - Toggle switch
- **Slider** - Range slider
- **Calendar** - Date picker
- **InputOTP** - One-time password input
- **Form** - Form validation with react-hook-form + zod

### Layout Components
- **Card** - Container with header/content/footer
- **Separator** - Divider line
- **Skeleton** - Loading placeholder
- **AspectRatio** - Aspect ratio container
- **ScrollArea** - Custom scrollable area
- **Resizable** - Resizable panels
- **Sticky** - Sticky positioning
- **Section** - Page section wrapper

### Navigation Components
- **NavigationMenu** - Main navigation menu
- **Breadcrumb** / **BreadcrumbNavigation** - Navigation breadcrumbs
- **Tabs** - Tab navigation
- **Pagination** / **SSRPagination** - Page pagination

### Overlay Components
- **Dialog** - Modal dialog
- **AlertDialog** - Confirmation dialog
- **Sheet** - Slide-out panel
- **Drawer** - Mobile drawer
- **Popover** - Floating popover
- **HoverCard** - Hover information card
- **Tooltip** - Tooltip on hover
- **Command** - Command palette
- **ContextMenu** - Right-click menu
- **DropdownMenu** - Dropdown menu
- **Menubar** - Application menubar

### Feedback Components
- **Toast** / **Toaster** / **Sonner** - Toast notifications
- **Alert** - Alert messages
- **Progress** - Progress bar
- **Badge** - Status badge
- **Avatar** - User avatar

### Data Display
- **Table** - Data table
- **Chart** - Data visualization (Chart.js)
- **Carousel** - Image carousel
- **Accordion** - Collapsible sections
- **Collapsible** - Simple collapse
- **Toggle** / **ToggleGroup** - Toggle buttons

### Specialized
- **Sidebar** - Sidebar navigation (23KB!)
- **ImageWithFallback** - Enhanced image with loading states

---

## 🎨 Blocks

Landing page sections:
- **Hero** / **SuperHero** - Hero sections
- **FeatureSection** - Feature showcase
- **CTASection** - Call-to-action
- **NewsletterSection** - Newsletter signup
- **StatsSection** - Statistics display
- **TestimonialSection** - Customer testimonials

---

## 🪝 Hooks

- **useToast** - Toast notification management
- **useLocalStorage** - Enhanced localStorage with error handling
- **useSessionStorage** - Enhanced sessionStorage with error handling
- **useCountdown** - Real-time countdown timer
- **useDebouncedCallback** - Debounced function execution
- **useEventListener** / **events** - Event bus for component communication
- **useCopy** - Copy to clipboard
- **useTheme** - Theme management
- **useIsMobile** - Mobile detection
- **useImageLoader** - Image loading states
- **useDebugTools** - React DevTools integration

---

## 🏗️ Layouts

### DashboardLayout

Full-featured dashboard layout with sidebar, header, and content areas.

```tsx
import { DashboardLayout } from '@djangocfg/ui';

<DashboardLayout
  // Basic config
  projectName="Unrealon"
  logoPath="/logo.svg"
  homeHref="/"

  // Current state
  currentPath={router.pathname}
  pageTitle="Dashboard"

  // User (optional - for auth-enabled dashboards)
  user={user}
  onLogout={handleLogout}

  // Sidebar menu groups
  menuGroups={[
    {
      label: "Main",
      items: [
        { icon: <HomeIcon />, label: "Dashboard", href: "/", isActive: true },
        { icon: <UsersIcon />, label: "Users", href: "/users" },
      ]
    }
  ]}

  // Optional features
  searchEnabled={true}
  notificationsEnabled={true}
  balanceAmount={1000}
>
  {children}
</DashboardLayout>
```

**Features:**
- Collapsible sidebar with menu groups
- Responsive (mobile drawer)
- Search dialog (Cmd+K)
- Notifications panel
- Balance widget
- User menu
- Auth-agnostic (works with or without auth)

### MainLayout

Marketing/landing page layout with navigation and footer.

```tsx
import { MainLayout } from '@djangocfg/ui';

<MainLayout
  config={{
    navigation: {
      projectName: "Unrealon",
      logoPath: "/logo.svg",
      homePath: "/",
      menuSections: [...]
    },
    userMenu: {
      profilePath: "/profile",
      dashboardPath: "/dashboard",
      authPath: "/auth"
    },
    footer: {
      copyright: "© 2025 Unrealon",
      links: [...]
    }
  }}
  // Optional auth props
  user={user}
  isAuthenticated={isAuth}
  onLogout={handleLogout}
>
  {children}
</MainLayout>
```

---

## 🎨 Theming

### CSS Variables

The library uses CSS variables for theming. Define in your globals.css:

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    /* ... more variables */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... dark mode variables */
  }
}
```

### Dark Mode

```tsx
import { useTheme } from '@djangocfg/ui';

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      {theme === 'light' ? 'Dark' : 'Light'} Mode
    </button>
  );
}
```

---

## 🛠️ Utilities

### cn() - Class Name Merger

```tsx
import { cn } from '@djangocfg/ui/lib';

<div className={cn(
  "base-classes",
  isActive && "active-classes",
  className
)} />
```

---

## 📖 Examples

### Simple Dashboard

```tsx
import { DashboardLayout, Card, Button } from '@djangocfg/ui';
import { LayoutDashboard, Users, Settings } from 'lucide-react';

export default function Dashboard() {
  return (
    <DashboardLayout
      projectName="My App"
      logoPath="/logo.svg"
      homeHref="/"
      currentPath="/"
      pageTitle="Dashboard"
      menuGroups={[
        {
          label: "Menu",
          items: [
            { icon: <LayoutDashboard />, label: "Dashboard", href: "/", isActive: true },
            { icon: <Users />, label: "Users", href: "/users" },
            { icon: <Settings />, label: "Settings", href: "/settings" },
          ]
        }
      ]}
    >
      <Card>
        <CardHeader>
          <CardTitle>Welcome!</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Dashboard content here</p>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
```

### Toast Notifications

```tsx
import { useToast, Button } from '@djangocfg/ui';

function MyComponent() {
  const { toast } = useToast();

  return (
    <Button onClick={() => {
      toast({
        title: "Success!",
        description: "Operation completed",
      });
    }}>
      Show Toast
    </Button>
  );
}
```

### Form with Validation

```tsx
import { Form, Input, Button, useToast } from '@djangocfg/ui';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

function LoginForm() {
  const { toast } = useToast();
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' }
  });

  const onSubmit = (data) => {
    console.log(data);
    toast({ title: "Success!" });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {/* More fields... */}
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  );
}
```

---

## 🔧 Development

### Package Structure

```
src/
├── components/     # 56+ UI components
├── blocks/         # 8 landing page blocks
├── layouts/        # 2 layouts (Dashboard, Main)
├── hooks/          # 11 React hooks
├── lib/            # Utilities (cn, utils)
├── snippets/       # Code snippets
├── tools/          # Development tools
├── events/         # Event bus
└── styles/         # Global CSS
```

### Exports

```json
{
  ".": "./src/index.ts",
  "./components": "./src/components/index.ts",
  "./hooks": "./src/hooks/index.ts",
  "./layouts": "./src/layouts/index.ts",
  "./blocks": "./src/blocks/index.ts",
  "./lib": "./src/lib/index.ts",
  "./styles": "./src/styles/globals.css",
  "./tailwind.config": "./tailwind.config.js"
}
```

---

## 📝 Notes

- **No Auth Dependencies**: Layouts are auth-agnostic. Pass auth props optionally.
- **Radix UI**: Built on battle-tested Radix UI primitives.
- **TypeScript**: Fully typed with strict mode.
- **Accessible**: WCAG compliant components.
- **Responsive**: Mobile-first design.
- **Dark Mode**: Built-in dark mode support.

---

## 📄 License

Part of Unrealon project.
