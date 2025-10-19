/**
 * Support Layout
 * Modern support layout with resizable panels for desktop and mobile-optimized view
 */

'use client';

import React from 'react';
import { SupportProvider } from '@djangocfg/api/cfg/contexts';
import { SupportLayoutProvider, useSupportLayoutContext } from './context';
import {
  TicketList,
  MessageList,
  MessageInput,
  CreateTicketDialog,
} from './components';
import {
  Button,
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@djangocfg/ui';
import { Plus, LifeBuoy, ArrowLeft } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────────
// Support Layout Content (with context)
// ─────────────────────────────────────────────────────────────────────────

const SupportLayoutContent: React.FC = () => {
  const { selectedTicket, selectTicket, openCreateDialog, getUnreadCount } =
    useSupportLayoutContext();
  const [isMobile, setIsMobile] = React.useState(false);
  
  React.useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const unreadCount = getUnreadCount();

  if (isMobile) {
    // Mobile layout - single column with navigation
    return (
      <div className="h-screen flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <div className="flex items-center justify-between p-4 border-b bg-background flex-shrink-0">
          <div className="flex items-center gap-2">
            {selectedTicket ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => selectTicket(null)}
                className="p-1"
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
            ) : (
              <LifeBuoy className="h-6 w-6 text-primary" />
            )}
            <h1 className="text-xl font-semibold">
              {selectedTicket ? selectedTicket.subject : 'Support'}
            </h1>
            {unreadCount > 0 && !selectedTicket && (
              <div className="h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount}
              </div>
            )}
          </div>
          {!selectedTicket && (
            <Button onClick={openCreateDialog} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Ticket
            </Button>
          )}
        </div>

        {/* Mobile Content */}
        <div className="flex-1 min-h-0 overflow-hidden">
          {selectedTicket ? (
            // Show messages when ticket is selected
            <div className="h-full flex flex-col">
              <div className="flex-1 min-h-0 overflow-hidden">
                <MessageList />
              </div>
              <div className="flex-shrink-0">
                <MessageInput />
              </div>
            </div>
          ) : (
            // Show ticket list when no ticket is selected
            <TicketList />
          )}
        </div>

        {/* Dialog */}
        <CreateTicketDialog />
      </div>
    );
  }

  // Desktop layout - resizable panels
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Desktop Header */}
      <div className="flex items-center justify-between p-6 border-b bg-background flex-shrink-0">
        <div className="flex items-center gap-3">
          <LifeBuoy className="h-7 w-7 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Support Center</h1>
            <p className="text-sm text-muted-foreground">Get help from our support team</p>
          </div>
          {unreadCount > 0 && (
            <div className="h-6 w-6 bg-red-500 text-white text-sm rounded-full flex items-center justify-center">
              {unreadCount}
            </div>
          )}
        </div>

        <Button onClick={openCreateDialog}>
          <Plus className="h-4 w-4 mr-2" />
          New Ticket
        </Button>
      </div>

      {/* Desktop Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <ResizablePanelGroup direction="horizontal" className="h-full">
          {/* Ticket List Panel */}
          <ResizablePanel defaultSize={35} minSize={25} maxSize={50}>
            <div className="h-full border-r overflow-hidden">
              <TicketList />
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle className="hover:bg-accent transition-colors" />

          {/* Messages Panel */}
          <ResizablePanel defaultSize={65} minSize={50}>
            <div className="h-full flex flex-col overflow-hidden">
              <div className="flex-1 min-h-0 overflow-hidden">
                <MessageList />
              </div>
              <div className="flex-shrink-0">
                <MessageInput />
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {/* Dialog */}
      <CreateTicketDialog />
    </div>
  );
};

// ─────────────────────────────────────────────────────────────────────────
// Support Layout (with providers)
// ─────────────────────────────────────────────────────────────────────────

export interface SupportLayoutProps {
  children?: React.ReactNode;
}

export const SupportLayout: React.FC<SupportLayoutProps> = () => {
  return (
    <div className="h-screen w-full overflow-hidden">
      <SupportProvider>
        <SupportLayoutProvider>
          <SupportLayoutContent />
        </SupportLayoutProvider>
      </SupportProvider>
    </div>
  );
};

