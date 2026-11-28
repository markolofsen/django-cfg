"use client"

import { Toaster as Sonner } from 'sonner';
import { useResolvedTheme } from '../../../hooks';

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  const theme = useResolvedTheme()

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      // Keep toasts clear of the notch / home indicator (tokens are 0 without viewport-fit=cover).
      offset={{ top: 'max(24px, var(--safe-top, 0px))', bottom: 'max(24px, var(--safe-bottom, 0px))', left: 'max(24px, var(--safe-left, 0px))', right: 'max(24px, var(--safe-right, 0px))' }}
      mobileOffset={{ top: 'max(16px, var(--safe-top, 0px))', bottom: 'max(16px, var(--safe-bottom, 0px))', left: 'max(16px, var(--safe-left, 0px))', right: 'max(16px, var(--safe-right, 0px))' }}
      richColors
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-background group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-muted-foreground",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
