/**
 * ErrorBoundary - Automatic Error Handling
 *
 * Built-in React Error Boundary for AppLayout
 * Catches all runtime errors and displays ErrorLayout
 * No manual setup required - works automatically!
 */

'use client';

import React, { Component, ReactNode } from 'react';
import { ErrorLayout } from '../../ErrorLayout';
import { Bug } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Callback when error occurs */
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  /** Custom fallback UI */
  fallback?: (error: Error, reset: () => void) => ReactNode;
  /** Support email for error pages */
  supportEmail?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

/**
 * ErrorBoundary Component
 *
 * Automatically wraps all AppLayout children
 * Catches React errors and shows ErrorLayout
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error
    console.error('ErrorBoundary caught error:', error);
    console.error('Error info:', errorInfo);

    // Call optional callback
    this.props.onError?.(error, errorInfo);

    // Store error info in state
    this.setState({ errorInfo });
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.resetError);
      }

      // Default error UI using ErrorLayout
      return (
        <ErrorLayout
          title="Application Error"
          description="Something went wrong while rendering the page. Try refreshing or going back."
          illustration={<Bug className="w-24 h-24 text-destructive/50" strokeWidth={1.5} />}
          supportEmail={this.props.supportEmail}
          actions={
            <div className="flex gap-4">
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
              >
                Refresh Page
              </button>
              <button
                onClick={() => window.history.back()}
                className="px-6 py-3 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90 transition-colors font-medium"
              >
                Go Back
              </button>
            </div>
          }
        />
      );
    }

    return this.props.children;
  }
}
