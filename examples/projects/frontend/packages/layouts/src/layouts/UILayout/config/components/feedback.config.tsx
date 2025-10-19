/**
 * Feedback Components Configuration
 */

import React from 'react';
import {
  Alert,
  AlertDescription,
  AlertTitle,
  Progress,
  Badge,
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  useToast,
} from '@djangocfg/ui';
import type { ComponentConfig } from './types';

// Toast Preview Component
function ToastPreview() {
  const { toast } = useToast();

  return (
    <div className="p-4 border rounded-md bg-muted/30">
      <p className="text-sm text-muted-foreground mb-3">
        Toast is a hook-based component. Click buttons to trigger toasts:
      </p>
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
      <p className="text-xs text-muted-foreground mt-3">
        ✓ Toaster is globally available via AppLayout
      </p>
    </div>
  );
}

export const FEEDBACK_COMPONENTS: ComponentConfig[] = [
  {
    name: 'Toast',
    category: 'feedback',
    description: 'Toast notifications for user feedback',
    importPath: `import { useToast, Button } from '@djangocfg/ui';`,
    example: `function Component() {
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
}`,
    preview: <ToastPreview />,
  },
  {
    name: 'Alert',
    category: 'feedback',
    description: 'Alert messages for important information',
    importPath: `import { Alert, AlertDescription, AlertTitle } from '@djangocfg/ui';`,
    example: `<div className="space-y-4">
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
</div>`,
    preview: (
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
    ),
  },
  {
    name: 'Progress',
    category: 'feedback',
    description: 'Progress bar for showing completion status',
    importPath: `import { Progress } from '@djangocfg/ui';`,
    example: `<div className="space-y-4 max-w-md">
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
</div>`,
    preview: (
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
    ),
  },
  {
    name: 'Badge',
    category: 'feedback',
    description: 'Status badges for labels and categories',
    importPath: `import { Badge } from '@djangocfg/ui';`,
    example: `<div className="flex gap-2 flex-wrap">
  <Badge>Default</Badge>
  <Badge variant="secondary">Secondary</Badge>
  <Badge variant="destructive">Destructive</Badge>
  <Badge variant="outline">Outline</Badge>
</div>`,
    preview: (
      <div className="flex gap-2 flex-wrap">
        <Badge>Default</Badge>
        <Badge variant="secondary">Secondary</Badge>
        <Badge variant="destructive">Destructive</Badge>
        <Badge variant="outline">Outline</Badge>
      </div>
    ),
  },
  {
    name: 'Avatar',
    category: 'feedback',
    description: 'User avatar with fallback support',
    importPath: `import { Avatar, AvatarFallback, AvatarImage } from '@djangocfg/ui';`,
    example: `<div className="flex gap-4">
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
</div>`,
    preview: (
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
    ),
  },
];
