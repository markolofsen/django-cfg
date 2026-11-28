import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  RequestViewer,
  type NetworkRequest,
} from '.';

const meta = {
  title: 'Widgets/Chat Dev/RequestViewer',
  component: RequestViewer,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Lightweight HTTP inspector — renders an already-executed request/response in headers / body / timing tabs. Never fetches; pair with an interceptor that hands captured calls in. Status pill + method label colors route through `statusColor` / `methodColor` from `src/http.ts` in this package, then map to semantic surface classes.',
      },
    },
  },
} satisfies Meta<typeof RequestViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

const JSON_BODY = JSON.stringify(
  {
    user: { id: 42, name: 'Ada Lovelace', email: 'ada@example.com' },
    roles: ['admin', 'editor'],
    enabled: true,
  },
  null,
  2,
);

const TEXT_BODY = 'plain text response — not JSON, rendered as <pre>.';

const COMMON_HEADERS = {
  request: [
    { name: 'Accept', value: 'application/json' },
    { name: 'User-Agent', value: 'djangocfg-storybook/1.0' },
    { name: 'Authorization', value: 'Bearer ********' },
  ],
  response: [
    { name: 'Content-Type', value: 'application/json; charset=utf-8' },
    { name: 'Cache-Control', value: 'no-store' },
    { name: 'X-Request-Id', value: 'req_01HZ7…' },
  ],
};

const SHORT_TIMING = [
  { label: 'DNS', duration: 2.3 },
  { label: 'TCP', duration: 5.8 },
  { label: 'TLS', duration: 14.1 },
  { label: 'TTFB', duration: 28.4 },
  { label: 'Download', duration: 4.0 },
];

const SLOW_TIMING = [
  { label: 'DNS', duration: 12 },
  { label: 'TCP', duration: 48 },
  { label: 'TLS', duration: 220 },
  { label: 'Send', duration: 6 },
  { label: 'Wait (TTFB)', duration: 1840 },
  { label: 'Download', duration: 312 },
];

const get200: NetworkRequest = {
  method: 'GET',
  url: 'https://api.example.com/v1/users/42',
  status: 200,
  statusText: 'OK',
  requestHeaders: COMMON_HEADERS.request,
  responseHeaders: COMMON_HEADERS.response,
  responseBody: JSON_BODY,
  contentType: 'application/json',
  timing: SHORT_TIMING,
  duration: 54.6,
};

const post201: NetworkRequest = {
  method: 'POST',
  url: 'https://api.example.com/v1/users',
  status: 201,
  statusText: 'Created',
  requestHeaders: [
    ...COMMON_HEADERS.request,
    { name: 'Content-Type', value: 'application/json' },
  ],
  responseHeaders: [
    ...COMMON_HEADERS.response,
    { name: 'Location', value: '/v1/users/43' },
  ],
  responseBody: JSON.stringify({ id: 43, created: true }, null, 2),
  contentType: 'application/json',
  duration: 78.2,
};

const error404: NetworkRequest = {
  method: 'GET',
  url: 'https://api.example.com/v1/users/9999',
  status: 404,
  statusText: 'Not Found',
  requestHeaders: COMMON_HEADERS.request,
  responseHeaders: [
    { name: 'Content-Type', value: 'application/json; charset=utf-8' },
  ],
  responseBody: JSON.stringify(
    { error: 'not_found', message: 'User 9999 does not exist.' },
    null,
    2,
  ),
  contentType: 'application/json',
  duration: 22.1,
};

const slow: NetworkRequest = {
  method: 'PATCH',
  url: 'https://api.example.com/v1/users/42',
  status: 200,
  statusText: 'OK',
  requestHeaders: COMMON_HEADERS.request,
  responseHeaders: COMMON_HEADERS.response,
  responseBody: JSON.stringify({ ok: true, applied: ['name'] }, null, 2),
  contentType: 'application/json',
  timing: SLOW_TIMING,
  duration: SLOW_TIMING.reduce((s, t) => s + t.duration, 0),
};

const textBody: NetworkRequest = {
  method: 'GET',
  url: 'https://api.example.com/v1/robots.txt',
  status: 200,
  statusText: 'OK',
  requestHeaders: [{ name: 'Accept', value: 'text/plain' }],
  responseHeaders: [{ name: 'Content-Type', value: 'text/plain' }],
  responseBody: TEXT_BODY,
  contentType: 'text/plain',
  duration: 8.4,
};

export const Get200: Story = {
  args: { request: get200 },
};

export const Post201: Story = {
  args: { request: post201, defaultTab: 'body' },
};

export const Error404: Story = {
  args: { request: error404, defaultTab: 'body' },
};

export const Slow: Story = {
  args: { request: slow, defaultTab: 'timing' },
};

export const JsonBody: Story = {
  args: { request: get200, defaultTab: 'body' },
};

export const TextBody: Story = {
  args: { request: textBody, defaultTab: 'body' },
};
