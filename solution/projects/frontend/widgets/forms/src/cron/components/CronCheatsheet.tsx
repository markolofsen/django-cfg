'use client';

/**
 * CronCheatsheet
 *
 * Popover with cron syntax reference.
 */

import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { HelpCircle } from 'lucide-react';

export interface CronCheatsheetProps {
  className?: string;
}

export function CronCheatsheet({ className }: CronCheatsheetProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={cn(
            'p-1 rounded hover:bg-muted/50 transition-colors',
            className
          )}
          aria-label="Cron syntax help"
        >
          <HelpCircle className="h-4 w-4 text-muted-foreground" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-72 p-3" align="end">
        <div className="space-y-3">
          <p className="font-medium text-sm">Cron Format</p>
          <code className="block text-xs bg-muted px-2 py-1.5 rounded font-mono text-center">
            min hour day month weekday
          </code>

          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">minute</span>
              <span>0-59</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">hour</span>
              <span>0-23</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">day</span>
              <span>1-31</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">month</span>
              <span>1-12</span>
            </div>
            <div className="flex justify-between col-span-2">
              <span className="text-muted-foreground">weekday</span>
              <span>0-6 (Sun-Sat)</span>
            </div>
          </div>

          <div className="pt-2 border-t border-border space-y-1.5">
            <p className="text-xs font-medium">Special characters</p>
            <div className="grid grid-cols-2 gap-1.5 text-xs">
              <span><code className="bg-muted px-1 rounded">*</code> any value</span>
              <span><code className="bg-muted px-1 rounded">,</code> list (1,3,5)</span>
              <span><code className="bg-muted px-1 rounded">-</code> range (1-5)</span>
              <span><code className="bg-muted px-1 rounded">/</code> step (*/15)</span>
            </div>
          </div>

          <div className="pt-2 border-t border-border space-y-1.5">
            <p className="text-xs font-medium">Examples</p>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">0 9 * * *</span>
                <span>daily at 9am</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">0 9 * * 1-5</span>
                <span>weekdays 9am</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">*/15 * * * *</span>
                <span>every 15 min</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-muted-foreground">0 0 1 * *</span>
                <span>1st of month</span>
              </div>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
