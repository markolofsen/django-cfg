import type { Decorator } from '@storybook/nextjs-vite';
import { TooltipProvider } from '@djangocfg/ui-core/components';
import { DialogProvider } from '@djangocfg/ui-core/lib/dialog-service';

function StoryFrame({
  layout,
  children,
}: React.PropsWithChildren<{ layout: string }>) {
  if (layout === 'fullscreen') {
    return (
      <div className="flex h-screen w-screen flex-col bg-background text-foreground">
        {children}
      </div>
    );
  }

  if (layout === 'centered') {
    return (
      <div className="flex w-full items-center justify-center bg-background p-6 text-foreground">
        {children}
      </div>
    );
  }

  return (
    <div className="w-full bg-background p-6 text-foreground">{children}</div>
  );
}

/**
 * Global provider and layout ownership for isolated stories.
 *
 * Theme remains owned by `addon-themes`; app providers that require a backend
 * or persistent singleton stay story-local.
 */
export const withStoryHarness: Decorator = (Story, context) => {
  const layout =
    (context.parameters?.['layout'] as string | undefined) ?? 'padded';

  return (
    <TooltipProvider delayDuration={100}>
      <DialogProvider>
        <StoryFrame layout={layout}>
          <Story />
        </StoryFrame>
      </DialogProvider>
    </TooltipProvider>
  );
};
