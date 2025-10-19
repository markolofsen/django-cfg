/**
 * Create Payment Dialog (v2.0 - Simplified)
 * Dialog for creating new payments
 */

'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Button,
  TokenIcon,
} from '@djangocfg/ui';
import { Plus, RefreshCw } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { usePaymentsContext, useRootPaymentsContext } from '@djangocfg/api/cfg/contexts';
import { PAYMENT_EVENTS, closePaymentsDialog } from '../events';
import { openPaymentDetailsDialog } from '../events';

// Payment creation schema
const PaymentCreateSchema = z.object({
  amount_usd: z.number().min(0.01, 'Amount must be at least $0.01'),
  currency_code: z.string().min(1, 'Please select a currency'),
});

type PaymentCreateRequest = z.infer<typeof PaymentCreateSchema>;

export const CreatePaymentDialog: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { createPayment } = usePaymentsContext();
  const { currencies, isLoadingCurrencies } = useRootPaymentsContext();

  const form = useForm<PaymentCreateRequest>({
    resolver: zodResolver(PaymentCreateSchema),
    defaultValues: {
      amount_usd: 10,
      currency_code: 'USDT',
    },
  });

  // Extract currencies list from response (handle different possible structures)
  const currenciesList = useMemo(() => {
    const data = currencies?.currencies || currencies?.results || currencies || [];
    return Array.isArray(data) ? data : [];
  }, [currencies]);

  // Get currency options for select
  const currencyOptions = useMemo(() => {
    return currenciesList
      .filter((curr: any) => curr.is_enabled !== false)
      .map((curr: any) => ({
        code: curr.code || curr.currency_code || curr.symbol,
        name: curr.name || curr.code || curr.currency_code,
        usd_rate: curr.usd_rate || curr.rate || 1,
        network: curr.network || null,
      }));
  }, [currenciesList]);

  // Calculate crypto amount from USD
  const calculateCryptoAmount = useMemo(() => {
    const amountUsd = form.watch('amount_usd');
    const currencyCode = form.watch('currency_code');
    const currency = currencyOptions.find((c: any) => c.code === currencyCode);

    if (!currency || !currency.usd_rate || !amountUsd) {
      return null;
    }

    const cryptoAmount = amountUsd / currency.usd_rate;
    return {
      amount: cryptoAmount,
      currency: currency.code,
      rate: currency.usd_rate,
      network: currency.network,
    };
  }, [form.watch('amount_usd'), form.watch('currency_code'), currencyOptions]);

  // Listen for open/close events
  useEffect(() => {
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);

    window.addEventListener(PAYMENT_EVENTS.OPEN_CREATE_PAYMENT_DIALOG, handleOpen);
    window.addEventListener(PAYMENT_EVENTS.CLOSE_DIALOG, handleClose);

    return () => {
      window.removeEventListener(PAYMENT_EVENTS.OPEN_CREATE_PAYMENT_DIALOG, handleOpen);
      window.removeEventListener(PAYMENT_EVENTS.CLOSE_DIALOG, handleClose);
    };
  }, []);

  const handleClose = () => {
    setOpen(false);
    form.reset();
  };

  // Initialize default currency if not set
  useEffect(() => {
    if (currencyOptions.length > 0 && !form.getValues('currency_code')) {
      form.setValue('currency_code', currencyOptions[0].code);
    }
  }, [currencyOptions, form]);

  const handleSubmit = async (data: PaymentCreateRequest) => {
    try {
      setIsSubmitting(true);

      const result = await createPayment();
      handleClose();
      closePaymentsDialog();

      // Extract payment ID from result
      const paymentData = result as any;
      const paymentId = paymentData?.payment?.id || paymentData?.id;

      if (paymentId) {
        openPaymentDetailsDialog(String(paymentId));
      }
    } catch (error) {
      console.error('Failed to create payment:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create Payment</DialogTitle>
          <DialogDescription>
            Create a new payment to add funds to your account.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="amount_usd"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Amount (USD)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      step="0.01"
                      min="0.01"
                      placeholder="10.00"
                      {...field}
                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                    />
                  </FormControl>
                  <FormDescription>
                    The amount you want to pay in USD.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="currency_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Currency</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    disabled={isLoadingCurrencies}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select currency..." />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {currencyOptions.map((curr: any) => (
                        <SelectItem key={curr.code} value={curr.code}>
                          <div className="flex items-center gap-2">
                            <TokenIcon symbol={curr.code} size={16} />
                            <span>{curr.code}</span>
                            {curr.network && (
                              <span className="text-xs text-muted-foreground">
                                ({curr.network})
                              </span>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    The cryptocurrency to use for payment.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Conversion Information */}
            {calculateCryptoAmount && (
              <div className="rounded-sm bg-muted p-4 space-y-3">
                {/* Amount to Send in Crypto */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">You will send</span>
                  <div className="flex items-center gap-2">
                    <TokenIcon symbol={calculateCryptoAmount.currency} size={16} />
                    <span className="font-mono font-semibold">
                      {calculateCryptoAmount.amount.toFixed(8)} {calculateCryptoAmount.currency}
                    </span>
                  </div>
                </div>

                {/* USD Amount Received */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">You will receive</span>
                  <span className="text-lg font-bold">
                    ${form.watch('amount_usd')?.toFixed(2)} USD
                  </span>
                </div>

                {/* Exchange Rate */}
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Rate</span>
                  <span className="font-medium">
                    1 {calculateCryptoAmount.currency} = ${calculateCryptoAmount.rate?.toFixed(2)}
                  </span>
                </div>

                {/* Network Info */}
                {calculateCryptoAmount.network && (
                  <div className="border-t pt-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Network</span>
                      <span className="text-sm font-medium">{calculateCryptoAmount.network}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting || currencyOptions.length === 0}>
                {isSubmitting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Payment
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
