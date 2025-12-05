import { Card, CardContent, Button, Badge } from '@djangocfg/ui-nextjs';
import { TrendingUp, TrendingDown, X } from 'lucide-react';
import type { Order } from '@/api/generated/trading/trading__api__trading/models';

interface OrderCardProps {
  order: Order;
  onCancel: (id: number) => Promise<void>;
}

export function OrderCardComponent({ order, onCancel }: OrderCardProps) {
  const isBuy = order.side === 'buy';
  const isCompleted = order.status === 'filled';
  const isPending = order.status === 'pending';

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isBuy ? (
              <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-600 dark:text-red-400" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{order.symbol}</span>
                <Badge variant={isBuy ? 'default' : 'destructive'}>
                  {order.side.toUpperCase()}
                </Badge>
                <Badge variant={isCompleted ? 'default' : isPending ? 'secondary' : 'outline'}>
                  {order.status}
                </Badge>
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {order.order_type} • Qty: {order.quantity}
                {order.price && ` • Price: $${order.price}`}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-semibold">${order.total_usd}</div>
              <div className="text-xs text-muted-foreground">
                {new Date(order.created_at).toLocaleDateString()}
              </div>
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
