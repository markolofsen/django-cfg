# Payments Contexts

Декомпозированные контексты для модуля Payments.

## Структура

### PaymentsContext
**Файл:** `PaymentsContext.tsx`  
**Назначение:** Управление платежами

**API:**
- `payments: PaginatedPaymentListList` - список платежей (пагинированный)
- `isLoadingPayments: boolean` - статус загрузки
- `refreshPayments()` - обновить список
- `getPayment(id)` - получить конкретный платеж
- `createPayment(data)` - создать платеж
- `cancelPayment(id, data)` - отменить платеж
- `checkPaymentStatus(id, data)` - проверить статус платежа

**Использование:**
```tsx
import { PaymentsProvider, usePaymentsContext } from '@djangocfg/api/cfg/contexts';

function PaymentsList() {
  const { payments, isLoadingPayments, refreshPayments } = usePaymentsContext();
  // ...
}
```

---

### BalancesContext
**Файл:** `BalancesContext.tsx`  
**Назначение:** Управление балансами пользователей (read-only)

**API:**
- `balances: PaginatedUserBalanceList` - список балансов
- `isLoadingBalances: boolean` - статус загрузки
- `refreshBalances()` - обновить список
- `getBalance(id)` - получить конкретный баланс
- `getBalanceSummary()` - получить сводку по балансу

**Использование:**
```tsx
import { BalancesProvider, useBalancesContext } from '@djangocfg/api/cfg/contexts';

function Balance() {
  const { balances, getBalanceSummary } = useBalancesContext();
  // ...
}
```

---

### CurrenciesContext
**Файл:** `CurrenciesContext.tsx`  
**Назначение:** Управление валютами и курсами обмена (read-only)

**API:**
- `currencies: PaginatedCurrencyListList` - список валют
- `isLoadingCurrencies: boolean` - статус загрузки
- `refreshCurrencies()` - обновить список
- `getCurrency(id)` - получить конкретную валюту
- `getCurrencyRates(baseCurrency, currencies)` - получить курсы обмена

**Использование:**
```tsx
import { CurrenciesProvider, useCurrenciesContext } from '@djangocfg/api/cfg/contexts';

function CurrencySelector() {
  const { currencies, getCurrencyRates } = useCurrenciesContext();
  // ...
}
```

---

### ApiKeysContext
**Файл:** `ApiKeysContext.tsx`  
**Назначение:** Управление API ключами

**API:**
- `apiKeys: PaginatedAPIKeyListList` - список API ключей
- `isLoadingApiKeys: boolean` - статус загрузки
- `refreshApiKeys()` - обновить список
- `getApiKey(id)` - получить конкретный ключ
- `createApiKey(data)` - создать ключ
- `deleteApiKey(id)` - удалить ключ

**Использование:**
```tsx
import { ApiKeysProvider, useApiKeysContext } from '@djangocfg/api/cfg/contexts';

function ApiKeysList() {
  const { apiKeys, createApiKey, deleteApiKey } = useApiKeysContext();
  // ...
}
```

---

### OverviewContext
**Файл:** `OverviewContext.tsx`  
**Назначение:** Дашборд и метрики платежной системы (read-only)

**API:**
- `overview: PaymentsDashboardOverview` - общий обзор
- `metrics: PaymentsMetrics` - метрики
- `balanceOverview: BalanceOverview` - обзор баланса
- `apiKeysOverview: APIKeysOverview` - обзор API ключей
- `subscriptionOverview: SubscriptionOverview` - обзор подписок
- `chartData: PaymentsChartResponse` - данные для графиков
- `recentPayments: PaginatedRecentPaymentList` - последние платежи
- `recentTransactions: PaginatedRecentTransactionList` - последние транзакции
- `isLoadingOverview: boolean` - статус загрузки
- `refreshOverview()` - обновить все данные

**Использование:**
```tsx
import { OverviewProvider, useOverviewContext } from '@djangocfg/api/cfg/contexts';

function Dashboard() {
  const { overview, metrics, chartData } = useOverviewContext();
  // ...
}
```

---

## Композиция провайдеров

Если нужно использовать несколько контекстов:

```tsx
import { 
  PaymentsProvider, 
  BalancesProvider, 
  OverviewProvider 
} from '@djangocfg/api/cfg/contexts';

function PaymentsDashboard() {
  return (
    <OverviewProvider>
      <PaymentsProvider>
        <BalancesProvider>
          <YourComponent />
        </BalancesProvider>
      </PaymentsProvider>
    </OverviewProvider>
  );
}
```

---

## Миграция со старого PaymentsContext

**Было:**
```tsx
import { PaymentsProvider, usePaymentsContext } from '@djangocfg/api/cfg/contexts';

const { payments, balances, apiKeys } = usePaymentsContext();
```

**Стало:**
```tsx
import { 
  PaymentsProvider, usePaymentsContext,
  BalancesProvider, useBalancesContext,
  ApiKeysProvider, useApiKeysContext
} from '@djangocfg/api/cfg/contexts';

// В разных компонентах или комбинируя:
const { payments } = usePaymentsContext();
const { balances } = useBalancesContext();
const { apiKeys } = useApiKeysContext();
```

---

## Преимущества декомпозиции

1. **Модульность** - каждый контекст отвечает за свою область
2. **Производительность** - меньше ненужных ре-рендеров
3. **Гибкость** - можно использовать только нужные контексты
4. **Читаемость** - явное разделение зон ответственности
5. **Масштабируемость** - проще добавлять новую функциональность

---

## Не включенные сущности

В текущей декомпозиции **не включены** (могут быть добавлены позже):
- `SubscriptionsContext` - управление подписками (CRUD)
- `TransactionsContext` - история транзакций (read-only)
- `TariffsContext` - тарифные планы (read-only)
- `NetworksContext` - блокчейн сети (read-only)
- `AdminContext` - админ-функции (для админки)

Эти сущности можно добавить по мере необходимости, следуя той же структуре.

