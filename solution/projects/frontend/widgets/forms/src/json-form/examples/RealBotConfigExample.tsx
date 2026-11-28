'use client';

import consola from 'consola';
import React, { useState } from 'react';

import {
    Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@djangocfg/ui-core/components';
import { RJSFSchema } from '@rjsf/utils';

import type { IChangeEvent } from '@rjsf/core';
import { JsonSchemaForm } from '../JsonSchemaForm';

/**
 * Real Bot Config Schema from API
 * This is the actual schema returned by the backend
 */
const realBotConfigSchema: RJSFSchema = {
  type: 'object',
  title: 'BotConfig',
  $schema: 'http://json-schema.org/draft-07/schema#',
  required: ['name', 'exchange'],
  properties: {
    name: {
      type: 'string',
      description: 'Bot name',
    },
    active: {
      type: 'boolean',
      description: 'Bot active',
    },
    enabled: {
      type: 'boolean',
      description: 'Bot enabled',
    },
    exchange: {
      type: 'string',
      description: 'Exchange name (binance, bybit, etc)',
    },
    direction: {
      type: 'string',
      description: 'Trading direction (long, short, both)',
    },
    amount_usdt: {
      type: 'number',
      description: 'Amount in USDT',
    },
    market_type: {
      type: 'string',
      description: 'Market type (spot, futures, swap)',
    },
    signal_type: {
      type: 'string',
      description: 'Signal type (listing, technical, etc)',
    },
    allowed_quotes: {
      type: 'array',
      items: {
        type: 'string',
      },
      description: 'Allowed quote currencies',
    },
    allowed_sources: {
      type: 'array',
      items: {
        type: 'string',
      },
      description: 'Allowed signal sources',
    },
    force_market_close_timer: {
      type: 'integer',
      description: 'Force close timer in seconds',
    },
    force_market_close_enabled: {
      type: 'boolean',
      description: 'Enable forced market close',
    },
  },
};

/**
 * Real settings data from bot
 */
const realSettings = {
  version: '1.0.0',
  hostname: 'botserver',
  supported_exchanges: ['binance'],
  supported_strategies: ['default'],
};

/**
 * Example component with real bot config schema
 */
export function RealBotConfigExample() {
  const [formData, setFormData] = useState<unknown>(realSettings);
  const [submittedData, setSubmittedData] = useState<unknown>(null);

  const handleSubmit = (data: IChangeEvent<unknown>) => {
    consola.success('Form submitted:', data.formData);
    setSubmittedData(data.formData);
  };

  const handleChange = (data: IChangeEvent<unknown>) => {
    consola.info('Form changed:', data.formData);
    setFormData(data.formData);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Real Bot Configuration Form</CardTitle>
            <CardDescription>
              Using actual schema from API response
            </CardDescription>
          </CardHeader>
          <CardContent>
            <JsonSchemaForm
              schema={realBotConfigSchema}
              formData={formData}
              onSubmit={handleSubmit}
              onChange={handleChange}
              liveValidate={false}
              showErrorList="top"
            />
          </CardContent>
        </Card>

        {submittedData !== null && submittedData !== undefined && (
          <Card>
            <CardHeader>
              <CardTitle>Submitted Data</CardTitle>
              <CardDescription>
                The data that was submitted from the form
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="p-4 bg-muted rounded-md overflow-auto text-sm">
                {JSON.stringify(submittedData, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Current Form Data</CardTitle>
            <CardDescription>
              Real-time form data (onChange)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="p-4 bg-muted rounded-md overflow-auto text-sm">
              {JSON.stringify(formData, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
