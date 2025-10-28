/**
 * Centrifugo View Events
 *
 * Event-driven communication for Centrifugo management dialogs and actions
 */

import { events } from '@djangocfg/ui';

// ─────────────────────────────────────────────────────────────────────────
// Event Types
// ─────────────────────────────────────────────────────────────────────────

export const CENTRIFUGO_EVENTS = {
  // Testing dialogs
  OPEN_PUBLISH_TEST_DIALOG: 'OPEN_PUBLISH_TEST_DIALOG',
  OPEN_PUBLISH_WITH_LOGGING_DIALOG: 'OPEN_PUBLISH_WITH_LOGGING_DIALOG',
  OPEN_SEND_ACK_DIALOG: 'OPEN_SEND_ACK_DIALOG',

  // Admin API dialogs
  OPEN_CHANNEL_HISTORY_DIALOG: 'OPEN_CHANNEL_HISTORY_DIALOG',
  OPEN_CHANNEL_PRESENCE_DIALOG: 'OPEN_CHANNEL_PRESENCE_DIALOG',

  // Refresh actions
  REFRESH_OVERVIEW: 'REFRESH_OVERVIEW',
  REFRESH_PUBLISHES: 'REFRESH_PUBLISHES',
  REFRESH_CHANNELS: 'REFRESH_CHANNELS',
} as const;

// ─────────────────────────────────────────────────────────────────────────
// Event Payload Types
// ─────────────────────────────────────────────────────────────────────────

export interface PublishTestDialogPayload {
  channel?: string;
  message?: any;
}

export interface SendAckDialogPayload {
  messageId?: string;
  channel?: string;
}

export interface ChannelHistoryDialogPayload {
  channel: string;
}

export interface ChannelPresenceDialogPayload {
  channel: string;
}

export interface RefreshPublishesPayload {
  channel?: string;
  status?: string;
  offset?: number;
}

// ─────────────────────────────────────────────────────────────────────────
// Event Emitters
// ─────────────────────────────────────────────────────────────────────────

export const emitOpenPublishTestDialog = (payload?: PublishTestDialogPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.OPEN_PUBLISH_TEST_DIALOG,
    payload: payload || {},
  });
};

export const emitOpenPublishWithLoggingDialog = (payload?: PublishTestDialogPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.OPEN_PUBLISH_WITH_LOGGING_DIALOG,
    payload: payload || {},
  });
};

export const emitOpenSendAckDialog = (payload?: SendAckDialogPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.OPEN_SEND_ACK_DIALOG,
    payload: payload || {},
  });
};

export const emitOpenChannelHistoryDialog = (payload: ChannelHistoryDialogPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.OPEN_CHANNEL_HISTORY_DIALOG,
    payload,
  });
};

export const emitOpenChannelPresenceDialog = (payload: ChannelPresenceDialogPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.OPEN_CHANNEL_PRESENCE_DIALOG,
    payload,
  });
};

export const emitRefreshOverview = () => {
  events.publish({
    type: CENTRIFUGO_EVENTS.REFRESH_OVERVIEW,
    payload: {},
  });
};

export const emitRefreshPublishes = (payload?: RefreshPublishesPayload) => {
  events.publish({
    type: CENTRIFUGO_EVENTS.REFRESH_PUBLISHES,
    payload: payload || {},
  });
};

export const emitRefreshChannels = () => {
  events.publish({
    type: CENTRIFUGO_EVENTS.REFRESH_CHANNELS,
    payload: {},
  });
};
