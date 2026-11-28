'use client';

import consola from 'consola';
import React, { useState } from 'react';

import {
    Card, CardContent, CardDescription, CardHeader, CardTitle
} from '@djangocfg/ui-core/components';
import { RJSFSchema, UiSchema } from '@rjsf/utils';

import type { IChangeEvent } from '@rjsf/core';
import { JsonSchemaForm } from '../JsonSchemaForm';

/**
 * Example JSON Schema for Bot Configuration
 */
const botConfigSchema: RJSFSchema = {
  $schema: 'http://json-schema.org/draft-07/schema#',
  title: 'Bot Configuration',
  type: 'object',
  required: ['name', 'exchange', 'bot_type'],
  properties: {
    name: {
      type: 'string',
      title: 'Bot Name',
      description: 'A unique name for your trading bot',
      minLength: 3,
      maxLength: 50,
    },
    active: {
      type: 'boolean',
      title: 'Active',
      description: 'Enable or disable the bot',
      default: true,
    },
    enabled: {
      type: 'boolean',
      title: 'Enabled',
      description: 'Whether the bot is enabled for trading',
      default: false,
    },
    exchange: {
      type: 'string',
      title: 'Exchange',
      description: 'Select the trading exchange',
      enum: ['binance', 'bybit', 'okx', 'kucoin'],
    },
    bot_type: {
      type: 'string',
      title: 'Bot Type',
      description: 'Type of trading bot',
      enum: ['spot', 'futures', 'margin'],
    },
    settings: {
      type: 'object',
      title: 'Bot Settings',
      properties: {
        max_trades: {
          type: 'integer',
          title: 'Maximum Trades',
          description: 'Maximum number of concurrent trades',
          minimum: 1,
          maximum: 100,
          default: 3,
        },
        trade_amount: {
          type: 'number',
          title: 'Trade Amount (USD)',
          description: 'Amount to invest per trade',
          minimum: 10,
          maximum: 10000,
          default: 100,
        },
        stop_loss: {
          type: 'number',
          title: 'Stop Loss (%)',
          description: 'Stop loss percentage',
          minimum: 0.1,
          maximum: 50,
          default: 5,
        },
        take_profit: {
          type: 'number',
          title: 'Take Profit (%)',
          description: 'Take profit percentage',
          minimum: 0.1,
          maximum: 100,
          default: 10,
        },
        strategy: {
          type: 'string',
          title: 'Trading Strategy',
          enum: ['scalping', 'swing', 'arbitrage', 'grid'],
        },
      },
    },
    api_credentials: {
      type: 'object',
      title: 'API Credentials',
      required: ['api_key', 'api_secret'],
      properties: {
        api_key: {
          type: 'string',
          title: 'API Key',
          description: 'Your exchange API key',
        },
        api_secret: {
          type: 'string',
          title: 'API Secret',
          description: 'Your exchange API secret',
        },
        testnet: {
          type: 'boolean',
          title: 'Use Testnet',
          description: 'Use testnet environment for testing',
          default: true,
        },
      },
    },
    notifications: {
      type: 'object',
      title: 'Notifications',
      properties: {
        email: {
          type: 'boolean',
          title: 'Email Notifications',
          default: true,
        },
        telegram: {
          type: 'boolean',
          title: 'Telegram Notifications',
          default: false,
        },
        webhook: {
          type: 'string',
          title: 'Webhook URL',
          format: 'uri',
        },
      },
    },
  },
};

/**
 * UI Schema for customizing form appearance
 */
const uiSchema: UiSchema = {
  'ui:submitButtonOptions': {
    submitText: 'Save Bot Configuration',
  },
  name: {
    'ui:placeholder': 'My Trading Bot',
  },
  active: {
    'ui:widget': 'SwitchWidget',
  },
  enabled: {
    'ui:widget': 'SwitchWidget',
  },
  exchange: {
    'ui:placeholder': 'Select exchange...',
  },
  bot_type: {
    'ui:placeholder': 'Select bot type...',
  },
  settings: {
    'ui:className': 'grid grid-cols-2 gap-4',
    strategy: {
      'ui:placeholder': 'Select strategy...',
    },
  },
  api_credentials: {
    api_secret: {
      'ui:widget': 'password',
    },
    testnet: {
      'ui:widget': 'SwitchWidget',
    },
  },
  notifications: {
    email: {
      'ui:widget': 'SwitchWidget',
    },
    telegram: {
      'ui:widget': 'SwitchWidget',
    },
    webhook: {
      'ui:placeholder': 'https://example.com/webhook',
    },
  },
};

/**
 * Example component demonstrating JsonSchemaForm usage
 */
export function BotConfigExample() {
  const [formData, setFormData] = useState<unknown>();
  const [submittedData, setSubmittedData] = useState<unknown>(null);

  const handleSubmit = (data: IChangeEvent<unknown>) => {
    consola.success('Form submitted:', data.formData);
    setSubmittedData(data.formData);
  };

  const handleChange = (data: IChangeEvent<unknown>) => {
    setFormData(data.formData);
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Bot Configuration Form</CardTitle>
            <CardDescription>
              Example of JSON Schema Form with Bot Configuration
            </CardDescription>
          </CardHeader>
          <CardContent>
            <JsonSchemaForm
              schema={botConfigSchema}
              uiSchema={uiSchema}
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
      </div>
    </div>
  );
}
