import type { Meta, StoryObj } from '@storybook/nextjs-vite';
import { useMemo, useState } from 'react';
import { Archive, CalendarDays, Folder, Home, Inbox, Library, MessageCircle, MessageCirclePlus, Search, Sparkles, User } from 'lucide-react';

import { LayoutI18nProvider, PrivateLayout, type HeaderConfig, type SidebarConfig } from '@djangocfg/layouts';
import { MockAuthProvider, buildMockUser } from '@djangocfg/layouts/testing';
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger, Avatar, AvatarFallback, Progress, RadioGroup, RadioGroupItem, Slider, Textarea,
  ToggleGroup, ToggleGroupItem, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
  Alert, AlertDescription, AlertTitle, Badge, Button, Checkbox, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel,
  DropdownMenuSeparator, DropdownMenuTrigger, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Switch, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Tabs, TabsList, TabsTrigger,
} from '@djangocfg/ui-core/components';
import { ThemeProvider, ThemeSegmented } from '@djangocfg/ui-core/theme';

// The chat package is not a dependency of this app yet; its sources are imported by path
// (no install needed). Replace with `@djangocfg/widget-chat/...` once it is added to package.json.
import '../../../../widgets/chat/src/styles/index.css';
import { AssistantHostProvider, AssistantPortal } from '../../../../widgets/chat/src/assistant/shell/panel/host';
import { useDemoAssistant } from '../../../../widgets/chat/src/assistant/examples/demo/demo-assistant';
import { AssistantFab } from '../../../../widgets/chat/src/assistant/shell/launcher/assistant-fab';
import { AssistantFrame } from '../../../../widgets/chat/src/assistant/shell/panel/assistant-frame';

/**
 * The real `PrivateLayout` (the shell every project uses) with the assistant docked on the right, wired exactly as `AssistantShell` does in the hub:
 * `AssistantFrame` wraps the whole layout, one chat stays mounted through a portal, `AssistantFab` returns when the column is closed.
 * Use the toolbar's Preset (`notion`) and the System/Light/Dark control in the top bar to judge the colours.
 */

const SIDEBAR: SidebarConfig = {
  homeHref: '/home',
  groups: [],
  views: [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
      groups: [
        { label: '', items: [{ label: 'Search', href: '/search', icon: Search }, { label: 'Inbox', href: '/inbox', icon: Inbox, badge: 44 }, { label: 'Library', href: '/library', icon: Library }] },
        { label: 'Favorites', items: [{ label: 'SEO', href: '/seo', icon: Sparkles }, { label: 'Research', href: '/research', icon: Sparkles }] },
        { label: 'Private', items: [{ label: 'Personal', href: '/personal', icon: User }, { label: 'Diary', href: '/diary', icon: Folder }, { label: 'Archive', href: '/archive', icon: Archive }] },
      ],
    },
    {
      id: 'chat',
      label: 'Chat',
      icon: MessageCircle,
      groups: [
        { label: '', items: [{ label: 'New chat', href: '/chat/new', icon: MessageCirclePlus }] },
        {
          label: 'Chats',
          items: ['CRM', 'Expenses overview', 'Studio Setup', 'Gantt — Launch plan broken'].map((t, i) => ({ label: t, href: `/chat/${i}`, icon: MessageCircle })),
        },
        { label: 'Agents', items: [{ label: 'New agent', href: '/agents/new', icon: Sparkles }] },
      ],
    },
    {
      id: 'calendar',
      label: 'Calendar',
      icon: CalendarDays,
      groups: [{ label: 'Upcoming events', items: [{ label: 'Connect your calendar', href: '/calendar/connect', icon: CalendarDays }] }],
    },
  ],
};

const HEADER: HeaderConfig = { title: 'Bridgetown Companies', brandLetter: 'B' };

type Tag = 'gray' | 'brown' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple' | 'pink' | 'red';
const ROWS: { title: string; date: string; areas: [string, Tag][]; type: [string, Tag] }[] = [
  { title: 'Quarterly planning notes', date: 'November 5, 2026', areas: [['Work', 'blue']], type: ['Event', 'gray'] },
  { title: 'Team offsite agenda', date: 'October 28, 2026', areas: [['People', 'orange'], ['Work', 'blue'], ['Budget', 'yellow']], type: ['Event', 'gray'] },
  { title: 'Move the office closer to the station', date: 'October 28, 2026', areas: [['Ideas', 'purple'], ['Places', 'pink']], type: ['Idea', 'purple'] },
  { title: 'Partnership proposal', date: 'October 28, 2026', areas: [['Business', 'green'], ['People', 'orange']], type: ['Event', 'gray'] },
  { title: 'Follow up on the open question', date: 'October 15, 2026', areas: [['Health', 'red']], type: ['Thought', 'blue'] },
];

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-10">
      <h2 className="mb-3 text-xs font-medium text-muted-foreground">{title}</h2>
      <div className="flex flex-wrap items-center gap-3">{children}</div>
    </section>
  );
}

function DiaryPage({ onAsk }: { onAsk: () => void }) {
  const [notify, setNotify] = useState(true);
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="box-border flex h-[var(--panel-header-h,3rem)] shrink-0 items-center justify-between border-b px-4 text-sm text-muted-foreground">
        <span>Personal / Diary</span>
        <div className="flex items-center gap-2">
          <ThemeSegmented size="compact" />
          <button type="button" onClick={onAsk} className="rounded-md px-2 py-1 hover:bg-accent">
            Ask AI
          </button>
        </div>
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-12 py-10">
          <h1 className="text-4xl font-bold tracking-tight">Diary</h1>
          <Tabs defaultValue="all" className="mt-4">
            <TabsList>
              <TabsTrigger value="all">All entries</TabsTrigger>
              <TabsTrigger value="cal">Calendar</TabsTrigger>
              <TabsTrigger value="area">By area</TabsTrigger>
            </TabsList>
          </Tabs>
          <Table frame={false} grid containerClassName="mt-4">
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                {['Entry', 'Date', 'Area', 'Type'].map((h) => (
                  <TableHead key={h}>{h}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {ROWS.map((r) => (
                <TableRow key={r.title}>
                  <TableCell className="font-medium">{r.title}</TableCell>
                  <TableCell>{r.date}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {r.areas.map(([n, c]) => (
                        <Badge key={n} variant={c}>{n}</Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={r.type[1]}>{r.type[0]}</Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Section title="Buttons">
            <Button>New</Button>
            <Button variant="secondary">Share</Button>
            <Button variant="outline">Filter</Button>
            <Button variant="ghost">Cancel</Button>
            <Button variant="destructive">Delete</Button>
            <Button size="sm">Small</Button>
          </Section>
          <Section title="Fields">
            <Input className="w-56" placeholder="Search or ask" />
            <Select defaultValue="en">
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="ru">Russian</SelectItem>
                <SelectItem value="de">German</SelectItem>
              </SelectContent>
            </Select>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox defaultChecked /> Remember me
            </label>
            <label className="flex items-center gap-2 text-sm">
              <Switch checked={notify} onCheckedChange={setNotify} /> Notifications
            </label>
          </Section>
          <Section title="Menu and tags">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">Workspace</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-60">
                <DropdownMenuLabel>jane.cooper@example.com</DropdownMenuLabel>
                <DropdownMenuItem>Settings</DropdownMenuItem>
                <DropdownMenuItem>Invite members</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Log out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            {(['gray', 'brown', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'red'] as Tag[]).map((c) => (
              <Badge key={c} variant={c}>{c}</Badge>
            ))}
          </Section>
          <Section title="Feedback">
            <Alert className="w-full">
              <AlertTitle>Saved</AlertTitle>
              <AlertDescription>Your diary entry was added to Private.</AlertDescription>
            </Alert>
          </Section>
          <Section title="People and progress">
            <div className="flex -space-x-2">
              {['JC', 'MK', 'AL'].map((n) => (
                <Avatar key={n} className="size-7 border-2 border-background">
                  <AvatarFallback className="text-xs">{n}</AvatarFallback>
                </Avatar>
              ))}
            </div>
            <Progress value={62} className="w-48" />
            <Slider defaultValue={[40]} max={100} className="w-48" />
            <ToggleGroup type="single" defaultValue="list">
              <ToggleGroupItem value="list">List</ToggleGroupItem>
              <ToggleGroupItem value="board">Board</ToggleGroupItem>
              <ToggleGroupItem value="cal">Calendar</ToggleGroupItem>
            </ToggleGroup>
          </Section>
          <Section title="Choices">
            <RadioGroup defaultValue="private" className="flex gap-4">
              <label className="flex items-center gap-2 text-sm"><RadioGroupItem value="private" /> Private</label>
              <label className="flex items-center gap-2 text-sm"><RadioGroupItem value="team" /> Team</label>
              <label className="flex items-center gap-2 text-sm"><RadioGroupItem value="public" /> Public</label>
            </RadioGroup>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="ghost">Hover me</Button>
                </TooltipTrigger>
                <TooltipContent>Copy link</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Section>
          <Section title="Long text">
            <Textarea className="w-full" placeholder="Write something, or press space for AI…" rows={3} />
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="a">
                <AccordionTrigger>What is in Private?</AccordionTrigger>
                <AccordionContent>Pages only you can see: your diary, personal notes and the archive.</AccordionContent>
              </AccordionItem>
              <AccordionItem value="b">
                <AccordionTrigger>Who can see the diary?</AccordionTrigger>
                <AccordionContent>Nobody but you, unless you share a page.</AccordionContent>
              </AccordionItem>
            </Accordion>
          </Section>
        </div>
      </div>
    </div>
  );
}

const withCollapsibleGroups = (config: SidebarConfig): SidebarConfig => ({
  ...config,
  views: config.views?.map((view) => ({ ...view, groups: view.groups.map((g) => (g.label ? { ...g, collapsible: true, defaultOpen: true } : g)) })),
});

function NotionShell({ collapsibleGroups = false, sidebarState, signedOut = false }: { collapsibleGroups?: boolean; sidebarState?: 'pinned' | 'collapsed'; signedOut?: boolean }) {
  if (sidebarState && typeof document !== 'undefined') document.cookie = `sidebar_state=${sidebarState === 'pinned'}; path=/`;
  // Like a host: "open" applies at load only where a column fits; a narrow window starts closed (no full-screen sheet after a reload).
  const [open, setOpen] = useState(() => typeof window !== 'undefined' && window.innerWidth >= 1280);
  const [width, setWidth] = useState(400);
  const user = useMemo(() => buildMockUser(), []);
  const demo = useDemoAssistant({ simple: true, focusWhen: open });
  return (
    <ThemeProvider defaultTheme="light" storageKey="notion-shell-theme">
      <AssistantHostProvider>
        <AssistantPortal>
          {demo?.chat}
        </AssistantPortal>
        <MockAuthProvider user={signedOut ? null : user}>
          <LayoutI18nProvider value={{ locale: 'en', locales: ['en'], onLocaleChange: () => undefined }}>
            <AssistantFrame docked={open} requireAuth width={width} minWidth={320} maxWidth={560} defaultWidth={400} onWidthChange={setWidth} onClose={() => setOpen(false)} onOpenChange={setOpen} labels={{ title: 'Assistant' }} actions={demo?.header}>
              <PrivateLayout sidebar={collapsibleGroups ? withCollapsibleGroups(SIDEBAR) : SIDEBAR} header={HEADER} pathname="/diary" requireAuth={false} contentPadding="none" contentScroll="hidden" settings={{ syncUrl: false, sections: [] }}>
                <DiaryPage onAsk={() => setOpen((v) => !v)} />
              </PrivateLayout>
            </AssistantFrame>
          </LayoutI18nProvider>
        </MockAuthProvider>
        {open ? null : <AssistantFab label="Open assistant" onClick={() => setOpen(true)} />}
      </AssistantHostProvider>
    </ThemeProvider>
  );
}

const meta = {
  title: 'Layouts/Notion shell',
  component: NotionShell,
  parameters: { layout: 'fullscreen' },
  globals: { preset: 'notion' },
} satisfies Meta<typeof NotionShell>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** Groups with a label fold, as in a Notion teamspace list. */
export const CollapsibleGroups: Story = { args: { collapsibleGroups: true } };

/** Desktop, sidebar collapsed: rest the pointer on the left edge for ~400 ms and it slides in. */
export const CollapsedSidebar: Story = { args: { sidebarState: 'collapsed' } };

/** Below 1280px the assistant is a side panel over the page, never a column that squeezes it. */
export const Tablet: Story = { parameters: { viewport: { defaultViewport: 'tablet' } } };

/** On a phone the assistant is a sheet and the sidebar a drawer. */
/** A reader who is not signed in: the assistant shows a big icon, one reason and a "Sign in" button (the frame's `requireAuth`, from the django-cfg auth state). */
export const SignedOut: Story = { args: { signedOut: true } };

export const Phone: Story = { parameters: { viewport: { defaultViewport: 'mobile1' } } };
