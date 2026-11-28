'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { Button } from '@djangocfg/ui-core/components';
import {
  Popover,
  PopoverContent,
  PopoverAnchor,
} from '@djangocfg/ui-core/components';
import { TourProvider, useTourContext } from '../context';
import type {
  TourProps,
  TourPopoverProps,
  TourNavigationProps,
} from '../types';

export function Tour({
  children,
  steps,
  onComplete,
  onDismiss,
  defaultOpen = false,
}: TourProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);
  const [currentStep, setCurrentStep] = React.useState(0);

  const totalSteps = steps.length;

  const goToStep = React.useCallback((index: number) => {
    if (index >= 0 && index < steps.length) {
      setCurrentStep(index);
    }
  }, [steps.length]);

  const nextStep = React.useCallback(() => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep((prev) => prev + 1);
    } else {
      setIsOpen(false);
      onComplete?.();
    }
  }, [currentStep, totalSteps, onComplete]);

  const prevStep = React.useCallback(() => {
    setCurrentStep((prev) => Math.max(0, prev - 1));
  }, []);

  const close = React.useCallback(() => {
    setIsOpen(false);
    onDismiss?.();
  }, [onDismiss]);

  const open = React.useCallback(() => {
    setCurrentStep(0);
    setIsOpen(true);
  }, []);

  const value = React.useMemo(
    () => ({
      isOpen,
      currentStep,
      steps,
      totalSteps,
      goToStep,
      nextStep,
      prevStep,
      close,
      open,
    }),
    [isOpen, currentStep, steps, totalSteps, goToStep, nextStep, prevStep, close, open]
  );

  return (
    <TourProvider value={value}>
      <div data-slot="tour">{children}</div>
    </TourProvider>
  );
}
Tour.displayName = 'Tour';

export function TourPopover({ className }: TourPopoverProps) {
  const { isOpen, currentStep, steps, close } = useTourContext();
  const step = steps[currentStep];
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);

  React.useEffect(() => {
    if (!step) return;
    const el = document.querySelector(step.target) as HTMLElement | null;
    setAnchorEl(el);
  }, [step]);

  if (!isOpen || !step || !anchorEl) return null;

  return (
    <Popover open={isOpen} onOpenChange={(open) => !open && close()}>
      <PopoverAnchor virtualRef={{ current: anchorEl }} />
      <PopoverContent
        data-slot="tour-popover"
        side={step.placement ?? 'bottom'}
        align="center"
        className={cn('w-80 p-4', className)}
      >
        <TourPopoverContent />
      </PopoverContent>
    </Popover>
  );
}
TourPopover.displayName = 'TourPopover';

const DEFAULT_SPOTLIGHT_PADDING = 8;

interface TourSpotlightProps {
  className?: string;
  /** Pixels of breathing room around the target rectangle. Default: 8. */
  padding?: number;
  /** Background colour of the dimmed area. Default: `rgba(0,0,0,0.6)`. */
  background?: string;
  /** Show a ring around the highlighted target. Default: true. */
  ring?: boolean;
  /** Close the tour when clicking outside the spotlight. Default: false. */
  closeOnClick?: boolean;
}

/**
 * Spotlight overlay — full-viewport dim with a hole cut around the
 * current step's target element. Mount once alongside `<TourPopover />`.
 */
export function TourSpotlight({
  className,
  padding = DEFAULT_SPOTLIGHT_PADDING,
  background = 'rgba(0, 0, 0, 0.6)',
  ring = true,
  closeOnClick = false,
}: TourSpotlightProps) {
  const { isOpen, currentStep, steps, close } = useTourContext();
  const step = steps[currentStep];
  const [rect, setRect] = React.useState<DOMRect | null>(null);

  React.useEffect(() => {
    if (!isOpen || !step) {
      setRect(null);
      return;
    }
    const el = document.querySelector(step.target) as HTMLElement | null;
    if (!el) {
      setRect(null);
      return;
    }

    const measure = () => setRect(el.getBoundingClientRect());
    measure();

    const ro = new ResizeObserver(measure);
    ro.observe(el);
    window.addEventListener('resize', measure);
    window.addEventListener('scroll', measure, true);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', measure);
      window.removeEventListener('scroll', measure, true);
    };
  }, [isOpen, step]);

  if (!isOpen || !rect) return null;

  const x = Math.max(0, rect.left - padding);
  const y = Math.max(0, rect.top - padding);
  const w = rect.width + padding * 2;
  const h = rect.height + padding * 2;

  // Polygon mask: outer rectangle (viewport) minus inner rectangle (target).
  // Traced as a single polygon — the inner cut-out is reached via a thin
  // bridge along the left edge so the shape stays self-closing.
  const clipPath = `polygon(
    0% 0%,
    0% 100%,
    ${x}px 100%,
    ${x}px ${y}px,
    ${x + w}px ${y}px,
    ${x + w}px ${y + h}px,
    ${x}px ${y + h}px,
    ${x}px 100%,
    100% 100%,
    100% 0%
  )`;

  return (
    <>
      <div
        data-slot="tour-spotlight"
        aria-hidden="true"
        onClick={closeOnClick ? close : undefined}
        className={cn(
          'fixed inset-0 z-40 transition-[clip-path] duration-200',
          closeOnClick && 'cursor-pointer',
          className,
        )}
        style={{ background, clipPath }}
      />
      {ring && (
        <div
          data-slot="tour-spotlight-ring"
          aria-hidden="true"
          className="pointer-events-none fixed z-40 rounded-md ring-2 ring-primary/70 ring-offset-2 ring-offset-background transition-all duration-200"
          style={{ left: x, top: y, width: w, height: h }}
        />
      )}
    </>
  );
}
TourSpotlight.displayName = 'TourSpotlight';

function TourPopoverContent() {
  const { currentStep, steps, close } = useTourContext();
  const step = steps[currentStep];
  // `TourPopover` only mounts this once it has a step; the guard is unreachable.
  if (!step) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h4 className="font-semibold text-sm">{step.title}</h4>
          {step.description && (
            <p className="text-muted-foreground text-sm mt-1">{step.description}</p>
          )}
        </div>
        <button
          type="button"
          onClick={close}
          className="text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Close tour"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <TourNavigation />
    </div>
  );
}

export function TourNavigation({ className }: TourNavigationProps) {
  const { currentStep, totalSteps, nextStep, prevStep } = useTourContext();
  const isLast = currentStep === totalSteps - 1;

  return (
    <div
      data-slot="tour-navigation"
      className={cn('flex items-center justify-between pt-2 border-t border-border', className)}
    >
      <div className="flex gap-1">
        {Array.from({ length: totalSteps }).map((_, i) => (
          <div
            key={i}
            data-active={i === currentStep ? 'true' : undefined}
            className={cn(
              'h-1.5 w-1.5 rounded-full transition-colors',
              i === currentStep ? 'bg-primary' : 'bg-muted-foreground/30'
            )}
          />
        ))}
      </div>
      <div className="flex items-center gap-2">
        {currentStep > 0 && (
          <Button variant="ghost" size="sm" onClick={prevStep}>
            Back
          </Button>
        )}
        <Button size="sm" onClick={nextStep}>
          {isLast ? 'Finish' : 'Next'}
        </Button>
      </div>
    </div>
  );
}
TourNavigation.displayName = 'TourNavigation';
