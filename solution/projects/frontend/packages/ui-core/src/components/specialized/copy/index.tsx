'use client'

import { Check, Copy } from 'lucide-react';
import * as React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { copyText } from '../../../lib/clipboard';
import { cn } from '../../../lib/utils';
import { Button } from '../../forms/button';
import type { TooltipProp } from '../../overlay/tooltip';

// =============================================================================
// CopyButton - Copy button with icon feedback
// =============================================================================

export interface CopyButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onClick' | 'onCopy'> {
  /** Text to copy to clipboard */
  value: string
  /** Duration in ms to show success state (default: 2000) */
  successDuration?: number
  /** Callback after successful copy */
  onCopy?: (value: string) => void
  /** Button size variant */
  size?: 'default' | 'sm' | 'icon'
  /** Button style variant */
  variant?: 'default' | 'ghost' | 'outline'
  /** Optional label text (if provided, shows text next to icon) */
  children?: React.ReactNode
  /** Icon size class (default: "h-4 w-4") */
  iconClassName?: string
  /** Hover name (standard tooltip, hover devices only). Forwarded to the inner Button. */
  tooltip?: TooltipProp
}

const CopyButton = React.forwardRef<HTMLButtonElement, CopyButtonProps>(
  ({
    value,
    successDuration = 2000,
    onCopy,
    className,
    size = 'icon',
    variant = 'ghost',
    children,
    iconClassName = 'h-4 w-4',
    ...props
  }, ref) => {
    const t = useAppT()
    const [copied, setCopied] = React.useState(false)

    const handleCopy = async () => {
      if (!(await copyText(value))) return
      setCopied(true)
      onCopy?.(value)
      setTimeout(() => setCopied(false), successDuration)
    }

    const hasLabel = !!children
    const copiedText = t('ui.actions.copied')
    const copyLabel = t('ui.actions.copyToClipboard')

    return (
      <Button
        ref={ref}
        type="button"
        size={hasLabel ? size : 'icon'}
        variant={variant}
        onClick={handleCopy}
        className={cn('shrink-0', className)}
        aria-label={copied ? copiedText : copyLabel}
        {...props}
      >
        {copied ? (
          <Check className={cn(iconClassName, 'text-success')} />
        ) : (
          <Copy className={iconClassName} />
        )}
        {hasLabel && <span className={copied ? 'text-success' : undefined}>{copied ? copiedText : children}</span>}
      </Button>
    )
  }
)
CopyButton.displayName = 'CopyButton'

// =============================================================================
// CopyField - Field with label, text display, and copy button
// =============================================================================

export interface CopyFieldProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'children' | 'onCopy'> {
  /** Label text (optional) */
  label?: string
  /** Text to display and copy */
  value: string
  /** Duration in ms to show success state */
  successDuration?: number
  /** Callback after successful copy */
  onCopy?: (value: string) => void
  /** Show as monospace font */
  mono?: boolean
  /** Truncate long text (default: true). Set to false to allow wrapping */
  truncate?: boolean
  /** Break long words to prevent overflow (use with truncate={false}) */
  breakAll?: boolean
}

const CopyField = React.forwardRef<HTMLDivElement, CopyFieldProps>(
  ({
    label,
    value,
    successDuration = 2000,
    onCopy,
    className,
    mono = true,
    truncate = true,
    breakAll = false,
    ...props
  }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center justify-between gap-2 p-3 rounded-[var(--radius)] bg-muted',
          className
        )}
        {...props}
      >
        <div className="min-w-0 flex-1">
          {label && (
            <div className="text-xs text-muted-foreground mb-0.5">{label}</div>
          )}
          <div
            className={cn(
              'text-sm',
              mono && 'font-mono',
              truncate && 'truncate',
              breakAll && 'break-all'
            )}
            title={value}
          >
            {value}
          </div>
        </div>
        <CopyButton
          value={value}
          successDuration={successDuration}
          onCopy={onCopy}
        />
      </div>
    )
  }
)
CopyField.displayName = 'CopyField'

export { CopyButton, CopyField }
