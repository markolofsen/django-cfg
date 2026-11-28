"use client"

import { AlertCircle } from 'lucide-react';
import React from 'react';

import { Alert, AlertDescription, AlertTitle } from '@djangocfg/ui-core/components';
import { useAppT } from '@djangocfg/i18n';
import { ErrorListProps } from '@rjsf/utils';

/**
 * Error list template for JSON Schema Form
 * Displays validation errors at the top of the form
 */
export function ErrorListTemplate(props: ErrorListProps) {
  const { errors } = props;
  const t = useAppT();

  if (!errors || errors.length === 0) {
    return null;
  }

  return (
    <Alert variant="destructive" className="mb-6">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{t('tools.jsonForm.validationErrors')}</AlertTitle>
      <AlertDescription>
        <ul className="list-disc list-inside space-y-1 mt-2">
          {errors.map((error, index) => (
            <li key={index} className="text-sm">
              {error.stack}
            </li>
          ))}
        </ul>
      </AlertDescription>
    </Alert>
  );
}
