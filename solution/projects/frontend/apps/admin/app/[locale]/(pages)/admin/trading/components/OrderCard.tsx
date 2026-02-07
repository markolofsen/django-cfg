import { TrendingDown, TrendingUp, X } from 'lucide-react';

import { Badge, Button, Card, CardContent } from '@djangocfg/ui-nextjs';

import type { Order } from '@/api/generated/trading/trading__api__trading/models';

interface OrderCardProps {
  order: Order;
  onCancel: (id: number) => Promise<void>;
}

export function OrderCardComponent({ order, onCancel }: OrderCardProps) {
  const isBuy = order.side === 'buy';
  const isCompleted = order.status === 'filled';
  const isPending = order.status === 'pending';

  const sideLabel = order.side.toUpperCase();
  const sideBadgeVariant = isBuy ? 'default' : 'destructive';
  const statusBadgeVariant = isCompleted ? 'default' : isPending ? 'secondary' : 'outline';
  const priceText = order.price ? ` • Price: $${order.price}` : '';
  const orderDetails = `${order.order_type} • Qty: ${order.quantity}${priceText}`;
  const createdDate = new Date(order.created_at).toLocaleDateString();
  const TrendIcon = isBuy ? TrendingUp : TrendingDown;
  const trendIconClass = isBuy
    ? 'h-5 w-5 text-green-600 dark:text-green-400'
    : 'h-5 w-5 text-red-600 dark:text-red-400';

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendIcon className={trendIconClass} />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{order.symbol}</span>
                <Badge variant={sideBadgeVariant}>{sideLabel}</Badge>
                <Badge variant={statusBadgeVariant}>{order.status}</Badge>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {orderDetails}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-semibold">${order.total_usd}</div>
              <div className="text-xs text-muted-foreground">{createdDate}</div>
            </div>
            {isPending && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onCancel(order.id)}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
