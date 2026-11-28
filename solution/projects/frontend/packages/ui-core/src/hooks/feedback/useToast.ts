"use client"

/**
 * Toast notifications using Sonner
 *
 * @example
 * import { toast } from '@djangocfg/ui-core/hooks';
 *
 * toast.success('Saved!');
 * toast.error('Error', { description: 'Details here' });
 * toast.promise(fetchData(), { loading: 'Loading...', success: 'Done!', error: 'Failed' });
 */

import { toast } from 'sonner';

// Re-export types and toast from sonner
export { toast, type ExternalToast as ToastOptions } from 'sonner';

// Hook for components using destructuring pattern: const { toast } = useToast()
type ToastFn = typeof toast;
export function useToast(): { toast: ToastFn; dismiss: ToastFn['dismiss'] } {
  return { toast, dismiss: toast.dismiss };
}
