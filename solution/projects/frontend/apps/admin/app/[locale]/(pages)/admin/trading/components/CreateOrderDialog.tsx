import { useEffect, useState } from 'react';

import { OrderOrderType, OrderSide } from '@/api/generated/trading/enums';
import { useTrading } from '@/contexts';
import { events } from '@djangocfg/ui-core';
import {
    Button, Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
    Input, Label, Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@djangocfg/ui-nextjs';

import { TRADING_DIALOG_EVENTS } from '../events';

import type { OrderCreateRequest } from '@/api/generated/trading/trading__api__trading/models';
export function CreateOrderDialogComponent() {
  const { createOrder } = useTrading();
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<OrderCreateRequest>({
    symbol: '',
    side: OrderSide.BUY,
    quantity: '',
    order_type: OrderOrderType.MARKET,
  });

  // Subscribe to dialog events
  useEffect(() => {
    const unsubscribe = events.subscribe((event: any) => {
      if (event.type === TRADING_DIALOG_EVENTS.OPEN_CREATE_ORDER_DIALOG) {
        setIsOpen(true);
        if (event.payload?.initialData) {
          setFormData((prev) => ({ ...prev, ...event.payload.initialData }));
        }
      } else if (event.type === TRADING_DIALOG_EVENTS.CLOSE_TRADING_DIALOG) {
        setIsOpen(false);
        setFormData({
          symbol: '',
          side: OrderSide.BUY,
          quantity: '',
          order_type: OrderOrderType.MARKET,
        });
      }
    });
    return unsubscribe;
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await createOrder(formData);
      setIsOpen(false);
      setFormData({
        symbol: '',
        side: OrderSide.BUY,
        quantity: '',
        order_type: OrderOrderType.MARKET,
      });
    } catch (error) {
      console.error('Failed to create order:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Order</DialogTitle>
          <DialogDescription>
            Place a new trading order
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="symbol">Symbol</Label>
              <Input
                id="symbol"
                placeholder="BTC/USDT"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="side">Side</Label>
              <Select
                value={formData.side}
                onValueChange={(value) => setFormData({ ...formData, side: value as OrderSide })}
              >
                <SelectTrigger id="side">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={OrderSide.BUY}>Buy</SelectItem>
                  <SelectItem value={OrderSide.SELL}>Sell</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="order_type">Order Type</Label>
              <Select
                value={formData.order_type}
                onValueChange={(value) =>
                  setFormData({ ...formData, order_type: value as OrderOrderType })
                }
              >
                <SelectTrigger id="order_type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={OrderOrderType.MARKET}>Market</SelectItem>
                  <SelectItem value={OrderOrderType.LIMIT}>Limit</SelectItem>
                  <SelectItem value={OrderOrderType.STOP_LOSS}>Stop Loss</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                step="any"
                placeholder="0.00"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                required
              />
            </div>

            {(formData.order_type === OrderOrderType.LIMIT || formData.order_type === OrderOrderType.STOP_LOSS) && (
              <div className="space-y-2">
                <Label htmlFor="price">Price</Label>
                <Input
                  id="price"
                  type="number"
                  step="any"
                  placeholder="0.00"
                  value={formData.price || ''}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value || null })}
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Order'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
