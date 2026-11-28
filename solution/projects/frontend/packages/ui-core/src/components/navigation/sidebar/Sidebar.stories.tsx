import type { Meta, StoryObj } from '@storybook/react-vite';
import { FileText, Home, Settings, Users } from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Sidebar',
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const navItems = [
  { title: 'Dashboard', icon: Home, href: '/dashboard' },
  { title: 'Users', icon: Users, href: '/users' },
  { title: 'Logs', icon: FileText, href: '/logs' },
  { title: 'Settings', icon: Settings, href: '/settings' },
];

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <SidebarInset>
      <header className="flex h-12 items-center gap-2 border-b px-3">
        <SidebarTrigger />
        <span className="text-sm font-medium">App</span>
      </header>
      <main className="p-4 text-sm text-muted-foreground">{children}</main>
    </SidebarInset>
  );
}

export const Default: Story = {
  render: () => (
    <div className="h-[480px] w-full overflow-hidden">
      <SidebarProvider defaultOpen>
        <Sidebar collapsible="icon">
          <SidebarHeader>
            <div className="px-2 py-1.5 text-sm font-semibold">My App</div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => (
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
          <SidebarFooter>
            <div className="px-2 py-1.5 text-xs text-muted-foreground">v1.0.0</div>
          </SidebarFooter>
        </Sidebar>
        <Shell>Toggle the sidebar from the header trigger or ⌘B.</Shell>
      </SidebarProvider>
    </div>
  ),
};

export const Collapsed: Story = {
  render: () => (
    <div className="h-[480px] w-full overflow-hidden">
      <SidebarProvider defaultOpen={false}>
        <Sidebar collapsible="icon">
          <SidebarHeader>
            <div className="px-2 py-1.5 text-sm font-semibold">App</div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => (
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
        <Shell>Sidebar starts collapsed to icon rail.</Shell>
      </SidebarProvider>
    </div>
  ),
};

export const WithGroups: Story = {
  render: () => (
    <div className="h-[560px] w-full overflow-hidden">
      <SidebarProvider defaultOpen>
        <Sidebar collapsible="icon">
          <SidebarHeader>
            <div className="px-2 py-1.5 text-sm font-semibold">Workspace</div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Platform</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild tooltip="Dashboard">
                      <a href="/dashboard">
                        <Home />
                        <span>Dashboard</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild tooltip="Users">
                      <a href="/users">
                        <Users />
                        <span>Users</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
            <SidebarGroup>
              <SidebarGroupLabel>System</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild tooltip="Logs">
                      <a href="/logs">
                        <FileText />
                        <span>Logs</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild tooltip="Settings">
                      <a href="/settings">
                        <Settings />
                        <span>Settings</span>
                      </a>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>
        <Shell>Two labelled groups (Platform / System).</Shell>
      </SidebarProvider>
    </div>
  ),
};
