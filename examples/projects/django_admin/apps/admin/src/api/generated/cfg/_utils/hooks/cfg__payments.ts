/**
 * SWR Hooks for Payments
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__payments'
import type { API } from '../../index'
import type { Balance } from '../schemas/Balance.schema'
import type { PaginatedPaymentListList } from '../schemas/PaginatedPaymentListList.schema'
import type { PaymentDetail } from '../schemas/PaymentDetail.schema'
import type { PaymentList } from '../schemas/PaymentList.schema'

/**
 * Get user balance
 *
 * @method GET
 * @path /cfg/payments/balance/
 */
export function usePaymentsBalanceRetrieve(client?: API): ReturnType<typeof useSWR<Balance>> {
  return useSWR<Balance>(
    'cfg-payments-balance',
    () => Fetchers.getPaymentsBalanceRetrieve(client)
  )
}


/**
 * Get available currencies
 *
 * @method GET
 * @path /cfg/payments/currencies/
 */
export function usePaymentsCurrenciesList(client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    'cfg-payments-currencies',
    () => Fetchers.getPaymentsCurrenciesList(client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/
 */
export function usePaymentsPaymentsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedPaymentListList>> {
  return useSWR<PaginatedPaymentListList>(
    params ? ['cfg-payments-payments', params] : 'cfg-payments-payments',
    () => Fetchers.getPaymentsPaymentsList(params, client)
  )
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/
 */
export function usePaymentsPaymentsRetrieve(id: string, client?: API): ReturnType<typeof useSWR<PaymentDetail>> {
  return useSWR<PaymentDetail>(
    ['cfg-payments-payment', id],
    () => Fetchers.getPaymentsPaymentsRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/confirm/
 */
export function useCreatePaymentsPaymentsConfirmCreate() {
  const { mutate } = useSWRConfig()

  return async (id: string, client?: API): Promise<PaymentList> => {
    const result = await Fetchers.createPaymentsPaymentsConfirmCreate(id, client)
    // Revalidate related queries
    mutate('cfg-payments-payments-confirm')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/status/
 */
export function usePaymentsPaymentsStatusRetrieve(id: string, client?: API): ReturnType<typeof useSWR<PaymentList>> {
  return useSWR<PaymentList>(
    ['cfg-payments-payments-statu', id],
    () => Fetchers.getPaymentsPaymentsStatusRetrieve(id, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/payments/payments/create/
 */
export function useCreatePaymentsPaymentsCreateCreate() {
  const { mutate } = useSWRConfig()

  return async (client?: API): Promise<PaymentList> => {
    const result = await Fetchers.createPaymentsPaymentsCreateCreate(client)
    // Revalidate related queries
    mutate('cfg-payments-payments')
    return result
  }
}


/**
 * Get user transactions
 *
 * @method GET
 * @path /cfg/payments/transactions/
 */
export function usePaymentsTransactionsList(params?: { limit?: number; offset?: number; type?: string }, client?: API): ReturnType<typeof useSWR<any>> {
  return useSWR<any>(
    params ? ['cfg-payments-transactions', params] : 'cfg-payments-transactions',
    () => Fetchers.getPaymentsTransactionsList(params, client)
  )
}


