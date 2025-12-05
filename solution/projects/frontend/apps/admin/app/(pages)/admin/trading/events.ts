import { events } from '@djangocfg/ui-nextjs/hooks';
import type { OrderCreateRequest } from '@/api/generated/trading/trading__api__trading/models';

export const TRADING_DIALOG_EVENTS = {
  OPEN_CREATE_ORDER_DIALOG: 'OPEN_CREATE_ORDER_DIALOG',
  CLOSE_TRADING_DIALOG: 'CLOSE_TRADING_DIALOG',
} as const;

export const openCreateOrderDialog = (initialData?: Partial<OrderCreateRequest>) => {
  events.publish({
    type: TRADING_DIALOG_EVENTS.OPEN_CREATE_ORDER_DIALOG,
    payload: { initialData },
  });
};

export const closeTradingDialog = () => {
  events.publish({
    type: TRADING_DIALOG_EVENTS.CLOSE_TRADING_DIALOG,
    payload: {},
  });
};
