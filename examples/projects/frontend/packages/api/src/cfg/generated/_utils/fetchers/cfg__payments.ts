/**
 * Typed fetchers for Payments
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { BalanceSchema, type Balance } from '../schemas/Balance.schema'
import { PaginatedPaymentListListSchema, type PaginatedPaymentListList } from '../schemas/PaginatedPaymentListList.schema'
import { PaymentDetailSchema, type PaymentDetail } from '../schemas/PaymentDetail.schema'
import { PaymentListSchema, type PaymentList } from '../schemas/PaymentList.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * Get user balance
 *
 * @method GET
 * @path /cfg/payments/balance/
 */
export async function getPaymentsBalanceRetrieve(  client?
): Promise<Balance> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.balanceRetrieve()
  return BalanceSchema.parse(response)
}


/**
 * Get available currencies
 *
 * @method GET
 * @path /cfg/payments/currencies/
 */
export async function getPaymentsCurrenciesList(  client?
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.currenciesList()
  return response
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/
 */
export async function getPaymentsPaymentsList(  params?: { page?: number; page_size?: number },  client?
): Promise<PaginatedPaymentListList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.paymentsList(params?.page, params?.page_size)
  return PaginatedPaymentListListSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/
 */
export async function getPaymentsPaymentsRetrieve(  id: string,  client?
): Promise<PaymentDetail> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.paymentsRetrieve(id)
  return PaymentDetailSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/payments/payments/{id}/confirm/
 */
export async function createPaymentsPaymentsConfirmCreate(  id: string,  client?
): Promise<PaymentList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.paymentsConfirmCreate(id)
  return PaymentListSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/payments/payments/{id}/status/
 */
export async function getPaymentsPaymentsStatusRetrieve(  id: string,  client?
): Promise<PaymentList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.paymentsStatusRetrieve(id)
  return PaymentListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/payments/payments/create/
 */
export async function createPaymentsPaymentsCreateCreate(  client?
): Promise<PaymentList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.paymentsCreateCreate()
  return PaymentListSchema.parse(response)
}


/**
 * Get user transactions
 *
 * @method GET
 * @path /cfg/payments/transactions/
 */
export async function getPaymentsTransactionsList(  params?: { limit?: number; offset?: number; type?: string },  client?
): Promise<any> {
  const api = client || getAPIInstance()
  const response = await api.cfg_payments.transactionsList(params?.limit, params?.offset, params?.type)
  return response
}


