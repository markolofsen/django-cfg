import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyPrettyCode as PrettyCode } from './lazy';

// ─── Samples ──────────────────────────────────────────────────────────────────

const TS_SAMPLE = `import { useCallback, useEffect, useRef, useState } from 'react';

export type Status = 'idle' | 'loading' | 'success' | 'error';

export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export function useVehicles(initialParams?: Partial<PaginationParams>) {
  const [status, setStatus] = useState<Status>('idle');
  const [data, setData] = useState<unknown[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  const fetch = useCallback(async (p: PaginationParams) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setStatus('loading');
    const res = await window.fetch(\`/api/vehicles?page=\${p.page}\`, {
      signal: abortRef.current.signal,
    });
    const json = await res.json();
    setData(json.data);
    setStatus('success');
  }, []);

  useEffect(() => {
    fetch(initialParams as PaginationParams);
    return () => abortRef.current?.abort();
  }, []);

  return { status, data };
}`;

const JSON_SAMPLE = {
  framework: 'next',
  version: '16.2.2',
  features: ['app-router', 'rsc', 'turbopack'],
  flags: { strictMode: true, experimentalRSC: true },
  routes: [
    { path: '/', component: 'HomePage' },
    { path: '/about', component: 'AboutPage' },
  ],
};

const PYTHON_SAMPLE = `from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

import httpx
from pydantic import BaseModel, Field, field_validator


class FuelType(StrEnum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"


class Vehicle(BaseModel):
    id: str
    make: str
    model: str
    year: int
    fuel_type: FuelType
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        if not (1900 <= v <= datetime.utcnow().year + 1):
            raise ValueError(f"Invalid year: {v}")
        return v


@dataclass
class VehicleRepository:
    base_url: str

    async def list(self, page: int = 1) -> list[Vehicle]:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get("/vehicles", params={"page": page})
            response.raise_for_status()
            return [Vehicle.model_validate(v) for v in response.json()["data"]]`;

const BASH_SAMPLE = `#!/usr/bin/env bash
set -euo pipefail

# Deploy script for production
ENV="\${1:-staging}"
TAG="\${2:-latest}"

echo "Deploying to $ENV with tag $TAG"

docker build -t myapp:$TAG .
docker push registry.example.com/myapp:$TAG

kubectl set image deployment/myapp app=registry.example.com/myapp:$TAG
kubectl rollout status deployment/myapp --timeout=2m

echo "Done."`;

const SQL_SAMPLE = `-- Top selling vehicles in the last 30 days
WITH recent_sales AS (
  SELECT
    v.id,
    v.make,
    v.model,
    COUNT(s.id) AS sales_count,
    SUM(s.amount) AS revenue
  FROM vehicles v
  INNER JOIN sales s ON s.vehicle_id = v.id
  WHERE s.created_at >= NOW() - INTERVAL '30 days'
  GROUP BY v.id, v.make, v.model
)
SELECT *
FROM recent_sales
WHERE sales_count > 5
ORDER BY revenue DESC
LIMIT 20;`;

const YAML_SAMPLE = `version: '3.9'

services:
  api:
    image: registry.example.com/myapp:latest
    environment:
      DATABASE_URL: postgres://db/app
      REDIS_URL: redis://cache:6379
    depends_on:
      - db
      - cache
    ports:
      - "8000:8000"

  db:
    image: postgres:16-alpine
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_PASSWORD: secret

  cache:
    image: redis:7-alpine

volumes:
  db_data:`;

const LONG_SAMPLE = Array.from(
  { length: 60 },
  (_, i) => `const value_${i} = ${i * 3}; // computed entry ${i + 1}`,
).join('\n');

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta = {
  title: 'Widgets/Kit/PrettyCode',
  component: PrettyCode,
  tags: ['autodocs'],
  argTypes: {
    data: { control: 'text', table: { category: 'Content' } },
    language: {
      control: 'select',
      options: [
        'tsx',
        'ts',
        'js',
        'jsx',
        'json',
        'python',
        'bash',
        'sql',
        'yaml',
        'css',
        'html',
        'go',
        'rust',
        'markdown',
      ],
      table: { category: 'Content' },
    },
    mode: {
      control: 'inline-radio',
      options: ['dark', 'light'],
      table: { category: 'Appearance' },
    },
    variant: {
      control: 'inline-radio',
      options: ['card', 'plain'],
      table: { category: 'Appearance' },
    },
    inline: { control: 'boolean', table: { category: 'Appearance' } },
    isCompact: { control: 'boolean', table: { category: 'Appearance' } },
    customBg: { control: 'text', table: { category: 'Appearance' } },
    maxLines: { control: { type: 'number', min: 0, step: 1 }, table: { category: 'Behaviour' } },
  },
} satisfies Meta<typeof PrettyCode>;

export default meta;

type Story = StoryObj<typeof meta>;

const Frame = ({ children }: { children: React.ReactNode }) => (
  <div className="w-[720px]">{children}</div>
);

// ─── Playground ───────────────────────────────────────────────────────────────

export const Playground: Story = {
  args: {
    data: TS_SAMPLE,
    language: 'tsx',
    mode: 'dark',
    variant: 'card',
    inline: false,
    isCompact: false,
  },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

// ─── Curated presets ──────────────────────────────────────────────────────────

export const TypeScript: Story = {
  args: { data: TS_SAMPLE, language: 'tsx' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Json: Story = {
  args: { data: JSON_SAMPLE, language: 'json' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Python: Story = {
  args: { data: PYTHON_SAMPLE, language: 'python' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Bash: Story = {
  args: { data: BASH_SAMPLE, language: 'bash' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Sql: Story = {
  args: { data: SQL_SAMPLE, language: 'sql' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Yaml: Story = {
  args: { data: YAML_SAMPLE, language: 'yaml' },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const LongFileWithScroll: Story = {
  args: {
    data: LONG_SAMPLE,
    language: 'ts',
    maxLines: 20,
  },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const Inline: Story = {
  args: {
    data: `const status: 'ok' | 'err' = 'ok';`,
    language: 'ts',
    inline: true,
  },
  render: (args) => (
    <div className="text-sm">
      The variable <PrettyCode {...args} /> represents the result state.
    </div>
  ),
};

export const Compact: Story = {
  args: {
    data: `const port = 3000;`,
    language: 'ts',
    isCompact: true,
  },
  render: (args) => <PrettyCode {...args} />,
};

export const LightMode: Story = {
  args: {
    data: TS_SAMPLE,
    language: 'tsx',
    mode: 'light',
  },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};

export const PlainVariant: Story = {
  args: {
    data: TS_SAMPLE,
    language: 'tsx',
    variant: 'plain',
  },
  render: (args) => (
    <Frame>
      <PrettyCode {...args} />
    </Frame>
  ),
};
