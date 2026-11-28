"use client"

import { AlertCircle, CheckCircle2, Download, Loader2 } from 'lucide-react';
import * as React from 'react';

import { Button, type ButtonProps } from '../../forms/button';
import { cn } from '../../../lib';
import { useLocalStorage } from '../../../hooks';

// Token key used by the API client
const TOKEN_KEY = "auth_token"

export interface DownloadButtonProps extends Omit<ButtonProps, 'onClick'> {
  /**
   * URL to download from
   */
  url: string

  /**
   * Optional filename override. If not provided, will try to extract from Content-Disposition header
   */
  filename?: string

  /**
   * Optional callback when download starts
   */
  onDownloadStart?: () => void

  /**
   * Optional callback when download completes
   */
  onDownloadComplete?: (filename: string) => void

  /**
   * Optional callback when download fails
   */
  onDownloadError?: (error: Error) => void

  /**
   * Use fetch API for download (allows progress tracking and auth headers)
   * Default: true
   */
  useFetch?: boolean

  /**
   * Show download status icons (loading, success, error)
   * Default: true
   */
  showStatus?: boolean

  /**
   * Auto-reset status after success/error (in ms)
   * Default: 2000
   */
  statusResetDelay?: number

  /**
   * Method for download (GET or POST)
   * Default: GET
   */
  method?: 'GET' | 'POST'

  /**
   * Optional request body for POST requests
   */
  body?: unknown
}

type DownloadStatus = 'idle' | 'downloading' | 'success' | 'error'

const DownloadButton = React.forwardRef<HTMLButtonElement, DownloadButtonProps>(
  (
    {
      url,
      filename,
      onDownloadStart,
      onDownloadComplete,
      onDownloadError,
      useFetch = true,
      showStatus = true,
      statusResetDelay = 2000,
      method = 'GET',
      body,
      children,
      disabled,
      className,
      ...props
    },
    ref
  ) => {
    const [status, setStatus] = React.useState<DownloadStatus>('idle')
    const resetTimeoutRef = React.useRef<NodeJS.Timeout | undefined>(undefined)

    // Get auth token from localStorage
    const [token] = useLocalStorage<string>(TOKEN_KEY, '')

    // Clean up timeout on unmount
    React.useEffect(() => {
      return () => {
        if (resetTimeoutRef.current) {
          clearTimeout(resetTimeoutRef.current)
        }
      }
    }, [])

    /**
     * Extract filename from Content-Disposition header
     */
    const extractFilename = (headers: Headers): string | null => {
      const disposition = headers.get('Content-Disposition')
      if (!disposition) return null

      // Try to match: filename*=UTF-8''example.txt or filename="example.txt"
      const filenameMatch = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';]+)["']?/i)
      if (filenameMatch && filenameMatch[1]) {
        return decodeURIComponent(filenameMatch[1])
      }

      return null
    }

    /**
     * Trigger browser download for blob
     */
    const triggerDownload = (blob: Blob, downloadFilename: string) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = downloadFilename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }

    /**
     * Reset status after delay
     */
    const scheduleStatusReset = () => {
      if (resetTimeoutRef.current) {
        clearTimeout(resetTimeoutRef.current)
      }
      resetTimeoutRef.current = setTimeout(() => {
        setStatus('idle')
      }, statusResetDelay)
    }

    /**
     * Download using fetch API (supports auth, progress, error handling)
     */
    const downloadWithFetch = async () => {
      try {
        setStatus('downloading')
        onDownloadStart?.()

        const headers: HeadersInit = {}

        // Add authorization header if token is available
        if (token) {
          headers['Authorization'] = `Bearer ${token}`
        }

        const options: RequestInit = {
          method,
          headers,
        }

        if (method === 'POST' && body) {
          options.body = JSON.stringify(body)
          options.headers = {
            ...options.headers,
            'Content-Type': 'application/json',
          }
        }

        const response = await fetch(url, options)

        if (!response.ok) {
          throw new Error(`Download failed: ${response.status} ${response.statusText}`)
        }

        const blob = await response.blob()

        // Determine filename
        const downloadFilename =
          filename ||
          extractFilename(response.headers) ||
          `download-${Date.now()}.bin`

        // Trigger download
        triggerDownload(blob, downloadFilename)

        setStatus('success')
        onDownloadComplete?.(downloadFilename)
        scheduleStatusReset()
      } catch (error) {
        console.error('Download error:', error)
        setStatus('error')
        onDownloadError?.(error as Error)
        scheduleStatusReset()
      }
    }

    /**
     * Simple download using window.open (fallback)
     */
    const downloadWithWindowOpen = () => {
      try {
        setStatus('downloading')
        onDownloadStart?.()
        window.open(url, '_blank')

        // We can't really track success/failure with window.open
        // So just assume success after a short delay
        setTimeout(() => {
          setStatus('success')
          onDownloadComplete?.(filename || 'file')
          scheduleStatusReset()
        }, 500)
      } catch (error) {
        console.error('Download error:', error)
        setStatus('error')
        onDownloadError?.(error as Error)
        scheduleStatusReset()
      }
    }

    /**
     * Handle download click
     */
    const handleDownload = () => {
      if (status === 'downloading') return

      if (useFetch) {
        downloadWithFetch()
      } else {
        downloadWithWindowOpen()
      }
    }

    /**
     * Render status icon
     */
    const renderStatusIcon = () => {
      if (!showStatus) return null

      switch (status) {
        case 'downloading':
          return <Loader2 className="animate-spin" />
        case 'success':
          return <CheckCircle2 className="text-success" />
        case 'error':
          return <AlertCircle className="text-destructive" />
        default:
          return <Download />
      }
    }

    return (
      <Button
        ref={ref}
        onClick={handleDownload}
        disabled={disabled || status === 'downloading'}
        className={cn(className)}
        {...props}
      >
        {renderStatusIcon()}
        {children}
      </Button>
    )
  }
)

DownloadButton.displayName = "DownloadButton"

export { DownloadButton }
