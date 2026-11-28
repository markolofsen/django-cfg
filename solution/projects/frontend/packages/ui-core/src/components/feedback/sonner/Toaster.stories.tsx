import type { Meta, StoryObj } from '@storybook/react-vite';
import { toast } from 'sonner';
import { Button, Toaster } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Feedback/Toaster',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Re-exported `Toaster` from `sonner`. Mount once at the app root, then call `toast(...)` from anywhere.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Toaster richColors position="top-right" />
      <Button onClick={() => toast('Note saved')}>Default</Button>
      <Button variant="outline" onClick={() => toast.success('Profile updated')}>
        Success
      </Button>
      <Button
        variant="outline"
        onClick={() => toast.error('Could not reach the server')}
      >
        Error
      </Button>
      <Button
        variant="outline"
        onClick={() =>
          toast.message('New version available', {
            description: 'Reload to apply changes.',
            action: { label: 'Reload', onClick: () => window.location.reload() },
          })
        }
      >
        With action
      </Button>
    </div>
  ),
};

export const WithAction: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Toaster richColors position="top-right" />
      <Button
        onClick={() =>
          toast('Email archived', {
            description: 'The conversation was moved to your archive.',
            action: {
              label: 'Undo',
              onClick: () => toast.success('Archive undone'),
            },
          })
        }
      >
        Undo action
      </Button>
      <Button
        variant="outline"
        onClick={() =>
          toast.success('File uploaded', {
            description: 'report.pdf — 1.2 MB',
            action: {
              label: 'View',
              onClick: () => toast.message('Opening report.pdf…'),
            },
          })
        }
      >
        View action
      </Button>
      <Button
        variant="outline"
        onClick={() =>
          toast.error('Build failed', {
            description: 'next-build exited with code 1.',
            action: {
              label: 'Retry',
              onClick: () => toast.loading('Retrying build…'),
            },
          })
        }
      >
        Retry action
      </Button>
    </div>
  ),
};

export const Dismissible: Story = {
  render: () => {
    let lastId: string | number | undefined;
    return (
      <div className="flex flex-wrap gap-2">
        <Toaster richColors position="top-right" closeButton />
        <Button
          onClick={() => {
            lastId = toast('Manual dismiss', {
              description: 'This toast stays until you close it.',
              duration: Infinity,
            });
          }}
        >
          Show sticky toast
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            if (lastId !== undefined) toast.dismiss(lastId);
          }}
        >
          Dismiss last
        </Button>
        <Button variant="outline" onClick={() => toast.dismiss()}>
          Dismiss all
        </Button>
      </div>
    );
  },
};

export const PromiseToast: Story = {
  name: 'Promise',
  render: () => {
    const runPromise = (mode: 'success' | 'error') =>
      new window.Promise<{ name: string }>((resolve, reject) => {
        setTimeout(() => {
          if (mode === 'success') resolve({ name: 'invoice-042.pdf' });
          else reject(new Error('Network unreachable'));
        }, 1500);
      });

    return (
      <div className="flex flex-wrap gap-2">
        <Toaster richColors position="top-right" />
        <Button
          onClick={() =>
            toast.promise(runPromise('success'), {
              loading: 'Uploading file…',
              success: (data) => `Uploaded ${data.name}`,
              error: 'Upload failed',
            })
          }
        >
          Promise (success)
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.promise(runPromise('error'), {
              loading: 'Saving changes…',
              success: 'Changes saved',
              error: (err: Error) => err.message,
            })
          }
        >
          Promise (error)
        </Button>
      </div>
    );
  },
};

export const Custom: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Toaster position="top-right" />
      <Button
        onClick={() =>
          toast.custom((id) => (
            <div className="flex w-[360px] items-start gap-3 rounded-lg border bg-background p-4 shadow-lg">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <span aria-hidden>★</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold">New achievement unlocked</p>
                <p className="text-xs text-muted-foreground">
                  You created your first project. Keep going!
                </p>
                <div className="mt-2 flex gap-2">
                  <Button size="sm" onClick={() => toast.dismiss(id)}>
                    Nice
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toast.dismiss(id)}
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            </div>
          ))
        }
      >
        Rich custom toast
      </Button>
    </div>
  ),
};
