"use client"

import { useCallback } from 'react';

import type { AuthFormValidation } from '../types';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const useAuthValidation = (): AuthFormValidation => {
  const validateIdentifier = useCallback((id: string): boolean => {
    return EMAIL_REGEX.test(id);
  }, []);

  return { validateIdentifier };
};

export const validateIdentifier = (id: string): boolean => EMAIL_REGEX.test(id);
