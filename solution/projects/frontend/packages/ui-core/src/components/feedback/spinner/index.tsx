import { Loader2Icon } from 'lucide-react';

import { useAppT } from '@djangocfg/i18n';
import { cn } from '../../../lib/utils';

function Spinner({ className, ...props }: React.ComponentProps<"svg">) {
  const t = useAppT()
  const loadingLabel = t('ui.states.loading')

  return (
    <Loader2Icon
      role="status"
      aria-label={loadingLabel}
      className={cn("size-4 animate-spin", className)}
      {...props}
    />
  )
}

export { Spinner }
