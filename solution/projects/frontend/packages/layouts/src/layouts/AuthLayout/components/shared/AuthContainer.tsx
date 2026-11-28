'use client';

import React, { memo, useEffect, useState } from 'react';

import { AUTH } from '../../constants';
import type { AuthStep } from '../../types';

export interface AuthContainerProps {
  children: React.ReactNode;
  step: AuthStep;
  className?: string;
}

/**
 * AuthContainer - Apple-style minimal container with step animations.
 *
 * Memoised: re-renders only when `step`, `className` or `children`
 * reference change. Internal animation state is isolated and does
 * not propagate upward.
 */
function AuthContainerRaw({
  children,
  step,
  className = '',
}: AuthContainerProps) {
  const [isEntering, setIsEntering] = useState(true);
  const [currentStep, setCurrentStep] = useState(step);

  // Trigger animation on step change
  useEffect(() => {
    if (step !== currentStep) {
      setIsEntering(true);
      setCurrentStep(step);
    }
  }, [step, currentStep]);

  // Reset entering state after animation
  useEffect(() => {
    if (isEntering) {
      const timer = setTimeout(() => setIsEntering(false), AUTH.ANIMATION_DURATION);
      return () => clearTimeout(timer);
    }
  }, [isEntering]);

  return (
    <div
      className={`auth-container ${className}`}
      data-entering={isEntering}
      data-step={step}
    >
      {children}
    </div>
  );
}

export const AuthContainer = memo(AuthContainerRaw);
