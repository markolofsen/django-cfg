import { forwardRef, useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { FileText, Home, Paperclip, Plus, Settings, Trash2, Users } from 'lucide-react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  Button,
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
  Disclosure,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Link,
  LinkProvider,
  MenuBuilder,
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarTrigger,
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  PopoverRowButton,
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  StaticPagination,
  Stepper,
  StepperIndicator,
  StepperItem,
  StepperList,
  StepperSeparator,
  StepperTitle,
  StepperTrigger,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  navigationMenuTriggerStyle,
  type MenuItem,
} from '@djangocfg/ui-core/components';
import type { DRFPaginatedResponse, LinkComponent, LinkComponentProps } from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Navigation/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every navigation component in `ui-core`, side by side. The group covers three ' +
          'unrelated jobs that look alike in an alphabetical list: **moving between places**, ' +
          '**picking an action from a menu**, and **hiding content until asked**. ' +
          'This page sorts them by that job so the choice is one comparison, not fourteen ' +
          'story pages.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

/** Stands in for the Next.js adapter — stories have no router. */
const PlainLink: LinkComponent = forwardRef<HTMLAnchorElement, LinkComponentProps>(
  function PlainLink({ href, replace: _replace, scroll: _scroll, prefetch: _prefetch, children, ...rest }, ref) {
    return (
      <a href={href} ref={ref} {...rest}>
        {children}
      </a>
    );
  },
);

const NAV_ITEMS = [
  { title: 'Dashboard', icon: Home, href: '/dashboard' },
  { title: 'Users', icon: Users, href: '/users' },
  { title: 'Logs', icon: FileText, href: '/logs' },
  { title: 'Settings', icon: Settings, href: '/settings' },
];

function PaginationCell() {
  const [page, setPage] = useState(1);
  const data = useMemo<DRFPaginatedResponse<{ id: number }>>(() => {
    const pages = 10;
    return {
      count: 100,
      page,
      pages,
      page_size: 10,
      has_next: page < pages,
      has_previous: page > 1,
      next_page: page < pages ? page + 1 : null,
      previous_page: page > 1 ? page - 1 : null,
      results: [],
    };
  }, [page]);
  return <StaticPagination data={data} onPageChange={setPage} />;
}

function SidebarCell() {
  return (
    <div className="h-56 w-full overflow-hidden rounded-md border border-border">
      <SidebarProvider defaultOpen>
        <Sidebar collapsible="icon">
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {NAV_ITEMS.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild tooltip={item.title}>
                        <a href={item.href}>
                          <item.icon />
                          <span>{item.title}</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>
        <SidebarInset>
          <header className="flex h-10 items-center gap-2 border-b border-border px-2">
            <SidebarTrigger />
            <span className="text-xs font-medium">App</span>
          </header>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}

function StepperCell() {
  const [value, setValue] = useState('account');
  return (
    <Stepper value={value} onValueChange={setValue} className="w-full">
      <StepperList>
        {[
          { value: 'account', label: 'Account' },
          { value: 'billing', label: 'Billing' },
          { value: 'done', label: 'Done' },
        ].map((step, i, all) => (
          <StepperItem key={step.value} value={step.value}>
            <StepperTrigger>
              <StepperIndicator />
              <StepperTitle>{step.label}</StepperTitle>
            </StepperTrigger>
            {i < all.length - 1 ? <StepperSeparator /> : null}
          </StepperItem>
        ))}
      </StepperList>
    </Stepper>
  );
}

function MenuBuilderCell() {
  const [wrap, setWrap] = useState(true);
  const items: MenuItem[] = [
    {
      kind: 'section',
      id: 'attach',
      items: [
        { kind: 'item', id: 'add-files', label: 'Add files', icon: Paperclip, onSelect: () => undefined },
      ],
    },
    { kind: 'checkbox', id: 'wrap', label: 'Wrap long lines', checked: wrap, onCheckedChange: setWrap },
    { kind: 'separator', id: 'sep' },
    { kind: 'item', id: 'delete', label: 'Delete', icon: Trash2, variant: 'destructive', onSelect: () => undefined },
  ];
  return (
    <MenuBuilder items={items} align="start">
      <Button variant="outline" size="icon" aria-label="More actions">
        <Plus className="size-4" />
      </Button>
    </MenuBuilder>
  );
}

function PopoverRowButtonCell() {
  const [selected, setSelected] = useState('sonnet');
  return (
    <div className="w-full overflow-hidden rounded-md border border-border py-1">
      {['opus', 'sonnet', 'haiku'].map((model) => (
        <PopoverRowButton
          key={model}
          selected={selected === model}
          onClick={() => setSelected(model)}
        >
          {model}
        </PopoverRowButton>
      ))}
    </div>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by the job — wayfinding, action menus, progressive disclosure —
 * rather than alphabetically, which puts `Breadcrumb` beside `Collapsible`
 * and hides that they answer completely different questions.
 */
export const AllNavigation: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Wayfinding — where am I, where can I go">
        <Gallery>
          <GalleryItem name="Breadcrumb" hint="Depth in a hierarchy, plus the way back.">
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>Settings</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </GalleryItem>

          <GalleryItem name="Tabs" hint="Sibling views inside one page.">
            <Tabs defaultValue="account">
              <TabsList>
                <TabsTrigger value="account">Account</TabsTrigger>
                <TabsTrigger value="team">Team</TabsTrigger>
              </TabsList>
              <TabsContent value="account" className="pt-2 text-sm text-muted-foreground">
                Account panel.
              </TabsContent>
              <TabsContent value="team" className="pt-2 text-sm text-muted-foreground">
                Team panel.
              </TabsContent>
            </Tabs>
          </GalleryItem>

          <GalleryItem name="NavigationMenu" hint="Top-level site nav with flyouts.">
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuLink href="/" className={navigationMenuTriggerStyle()}>
                    Home
                  </NavigationMenuLink>
                </NavigationMenuItem>
                <NavigationMenuItem>
                  <NavigationMenuLink href="/docs" className={navigationMenuTriggerStyle()}>
                    Docs
                  </NavigationMenuLink>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
          </GalleryItem>

          <GalleryItem name="Sidebar" hint="Persistent app shell nav, collapsible.">
            <SidebarCell />
          </GalleryItem>

          <GalleryItem name="StaticPagination" hint="Page through a DRF paginated list.">
            <PaginationCell />
          </GalleryItem>

          <GalleryItem name="Stepper" hint="Position in a linear multi-step flow.">
            <StepperCell />
          </GalleryItem>

          <GalleryItem name="Link" hint="Router-agnostic anchor; needs LinkProvider.">
            <LinkProvider value={PlainLink}>
              <Link href="/dashboard" className="text-sm text-primary underline-offset-4 hover:underline">
                Go to dashboard
              </Link>
            </LinkProvider>
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Action menus — pick a command">
        <Gallery>
          <GalleryItem name="DropdownMenu" hint="Actions hanging off a button.">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">Open menu</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48">
                <DropdownMenuLabel>My account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Profile</DropdownMenuItem>
                <DropdownMenuItem>Billing</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </GalleryItem>

          <GalleryItem name="ContextMenu" hint="Same actions, on right-click.">
            <ContextMenu>
              <ContextMenuTrigger>
                <div className="flex h-20 items-center justify-center rounded-md border border-dashed border-border text-xs text-muted-foreground">
                  Right-click here
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent className="w-48">
                <ContextMenuItem>Rename</ContextMenuItem>
                <ContextMenuSeparator />
                <ContextMenuItem>Delete</ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>
          </GalleryItem>

          <GalleryItem name="Menubar" hint="Desktop-app menu bar across the top.">
            <Menubar>
              <MenubarMenu>
                <MenubarTrigger>File</MenubarTrigger>
                <MenubarContent>
                  <MenubarItem>New tab</MenubarItem>
                  <MenubarSeparator />
                  <MenubarItem>Print</MenubarItem>
                </MenubarContent>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>Edit</MenubarTrigger>
                <MenubarContent>
                  <MenubarItem>Undo</MenubarItem>
                </MenubarContent>
              </MenubarMenu>
            </Menubar>
          </GalleryItem>

          <GalleryItem name="MenuBuilder" hint="Same menu from a data array.">
            <MenuBuilderCell />
          </GalleryItem>

          <GalleryItem name="Command" hint="Searchable command palette.">
            <Command className="rounded-md border border-border">
              <CommandInput placeholder="Search commands…" />
              <CommandList>
                <CommandEmpty>No results.</CommandEmpty>
                <CommandGroup heading="Suggestions">
                  <CommandItem>Open settings</CommandItem>
                  <CommandItem>Invite a teammate</CommandItem>
                </CommandGroup>
              </CommandList>
            </Command>
          </GalleryItem>

          <GalleryItem name="PopoverRowButton" hint="Selectable row for picker popovers.">
            <PopoverRowButtonCell />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Disclosure — hide content until asked">
        <Gallery>
          <GalleryItem name="Accordion" hint="Several sections, one open at a time.">
            <Accordion type="single" collapsible>
              <AccordionItem value="one">
                <AccordionTrigger>What is included?</AccordionTrigger>
                <AccordionContent>Everything in the free tier, plus support.</AccordionContent>
              </AccordionItem>
              <AccordionItem value="two">
                <AccordionTrigger>Can I cancel?</AccordionTrigger>
                <AccordionContent>Any time, from the billing page.</AccordionContent>
              </AccordionItem>
            </Accordion>
          </GalleryItem>

          <GalleryItem name="Collapsible" hint="One region, you supply the trigger.">
            <Collapsible className="space-y-2">
              <CollapsibleTrigger asChild>
                <Button variant="ghost" size="sm">
                  Toggle details
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="rounded-md border border-border p-2 text-sm text-muted-foreground">
                Hidden until expanded.
              </CollapsibleContent>
            </Collapsible>
          </GalleryItem>

          <GalleryItem name="Disclosure" hint="Log-style row: label, fact, payload.">
            <Disclosure label={<span className="font-mono">fs.read</span>} fact="120ms">
              <pre className="font-mono text-xs">{'{ "bytes": 128 }'}</pre>
            </Disclosure>
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
