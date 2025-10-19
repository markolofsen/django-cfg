/**
 * Debug Error Page
 *
 * Intentionally throws a runtime error to test ErrorBoundary
 * Useful for testing error handling in development
 */

'use client';

import { useState } from 'react';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Alert,
  AlertDescription,
} from '@djangocfg/ui/components';

export default function DebugErrorPage() {
  const [shouldThrow, setShouldThrow] = useState(false);

  if (shouldThrow) {
    // Intentionally throw error to test ErrorBoundary
    throw new Error('🔥 Debug: Intentional runtime error for testing ErrorBoundary');
  }

  return (
    <div className="container mx-auto max-w-4xl py-16 px-4">
      <div className="space-y-8">
        {/* Header */}
        <div className="space-y-4">
          <h1 className="text-4xl font-bold">Debug: Error Testing</h1>
          <p className="text-lg text-muted-foreground">
            Test error handling and ErrorBoundary behavior
          </p>
        </div>

        {/* Error Testing Card */}
        <Card>
          <CardHeader>
            <CardTitle>Throw Runtime Error</CardTitle>
            <CardDescription>
              Click the button below to intentionally throw a runtime error. This will trigger
              the ErrorBoundary and display the error page.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert variant="destructive">
              <AlertDescription>
                ⚠️ Warning: This will crash the React component tree and show the error page
              </AlertDescription>
            </Alert>

            <Button
              variant="destructive"
              size="lg"
              onClick={() => setShouldThrow(true)}
              className="w-full sm:w-auto"
            >
              Throw Runtime Error
            </Button>
          </CardContent>
        </Card>

        {/* Info Cards */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* What Happens Card */}
          <Card>
            <CardHeader>
              <CardTitle>What Happens?</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• ErrorBoundary catches the error</li>
                <li>• Error is logged to console</li>
                <li>• ErrorLayout is displayed</li>
                <li>• User can refresh or go back</li>
              </ul>
            </CardContent>
          </Card>

          {/* Other Error Pages Card */}
          <Card>
            <CardHeader>
              <CardTitle>Other Error Types</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>
                  • <a href="/404" className="text-primary hover:underline">404 Not Found</a>
                </li>
                <li>
                  • <a href="/500" className="text-primary hover:underline">500 Server Error</a>
                </li>
                <li>
                  • <a href="/nonexistent" className="text-primary hover:underline">Test 404 (broken link)</a>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Technical Details */}
        <Card>
          <CardHeader>
            <CardTitle>Technical Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <strong className="text-foreground">ErrorBoundary Location:</strong>
              <p className="text-muted-foreground font-mono text-xs mt-1">
                packages/layouts/src/layouts/AppLayout/components/ErrorBoundary.tsx
              </p>
            </div>
            <div>
              <strong className="text-foreground">ErrorLayout Location:</strong>
              <p className="text-muted-foreground font-mono text-xs mt-1">
                packages/layouts/src/layouts/ErrorLayout/ErrorLayout.tsx
              </p>
            </div>
            <div>
              <strong className="text-foreground">Configuration:</strong>
              <p className="text-muted-foreground font-mono text-xs mt-1">
                apps/demo/src/core/appLayoutConfig.ts → errors config
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
