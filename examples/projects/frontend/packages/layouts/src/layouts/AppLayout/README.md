# AppLayout - Unified Application Layout System

Умный самодостаточный компонент для управления всеми layout'ами приложения.

## 📁 Структура

```
AppLayout/
├── types/                  # Все типы
│   ├── config.ts          # AppLayoutConfig
│   ├── layout.ts          # PublicLayoutConfig, PrivateLayoutConfig
│   ├── navigation.ts      # NavigationItem, DashboardMenuItem
│   ├── routes.ts          # RouteConfig, RouteDetectors
│   └── index.ts
│
├── context/                # Unified App Context
│   ├── AppContext.tsx     # Главный контекст приложения
│   └── index.ts
│
├── hooks/                  # Custom hooks
│   ├── useLayoutMode.ts   # Определение текущего режима
│   ├── useNavigation.ts   # Навигационные хуки
│   └── index.ts
│
├── providers/              # Provider components
│   ├── ThemeProvider.tsx  # Тема
│   ├── AuthProvider.tsx   # Аутентификация
│   └── index.ts
│
├── layouts/                # Layout renderers
│   ├── PublicLayout/      # Публичный layout
│   ├── PrivateLayout/     # Приватный layout (Dashboard)
│   ├── AuthLayout/        # Auth layout (минимальный)
│   └── index.ts
│
├── components/             # UI components
│   ├── Seo.tsx           # SEO meta tags
│   ├── PageProgress.tsx  # Loading bar
│   └── index.ts
│
├── utils/                  # Utilities
│   ├── routeDetection.ts # Определение типа маршрута
│   └── index.ts
│
├── AppLayout.tsx          # Главный компонент
├── index.ts               # Public exports
└── README.md              # Документация
```

## 🎯 Основная идея

**Единая точка входа** - один компонент `<AppLayout>` управляет всем:
- Автоматически определяет тип страницы (public/private/auth)
- Применяет нужный layout
- Управляет состоянием через единый контекст
- Предоставляет хуки для доступа к функционалу

## 🚀 Использование

### В _app.tsx (единственное место подключения)

```tsx
import { AppLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core/appLayoutConfig';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AppLayout config={appLayoutConfig}>
      <Component {...pageProps} />
    </AppLayout>
  );
}
```

### Конфигурация

```tsx
// core/appLayoutConfig.ts
import type { AppLayoutConfig } from '@djangocfg/layouts';

export const appLayoutConfig: AppLayoutConfig = {
  app: {
    name: 'My App',
    logoPath: '/logo.svg',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL,
  },
  routes: {
    auth: '/auth',
    defaultCallback: '/dashboard',
    detectors: {
      isPublicRoute: (path) => !path.startsWith('/private'),
      isPrivateRoute: (path) => path.startsWith('/private'),
      isAuthRoute: (path) => path.startsWith('/auth'),
      getUnauthenticatedRedirect: (path) =>
        path.startsWith('/private') ? '/auth' : null,
      getPageTitle: (path) => 'My App',
    },
  },
  publicLayout: {
    navigation: { /* ... */ },
    userMenu: { /* ... */ },
    footer: { /* ... */ },
  },
  privateLayout: {
    menuGroups: [ /* ... */ ],
    showChat: true,
  },
};
```

## 🎨 Использование в компонентах

### Доступ к контексту

```tsx
import { useAppContext } from '@djangocfg/layouts';

function MyComponent() {
  const {
    config,
    layoutMode,
    mobileMenuOpen,
    toggleMobileMenu
  } = useAppContext();

  return (
    <button onClick={toggleMobileMenu}>
      {layoutMode === 'private' ? 'Dashboard' : 'Home'}
    </button>
  );
}
```

### Использование хуков

```tsx
import { useLayoutMode, useNavigation } from '@djangocfg/layouts';

function MyComponent() {
  const mode = useLayoutMode(); // 'public' | 'private' | 'auth'
  const { isActive } = useNavigation();

  if (mode === 'private') {
    return <DashboardView />;
  }

  return <PublicView />;
}
```

## 🏗️ Архитектурные принципы

### 1. Single Source of Truth
Вся конфигурация в одном месте - `AppLayoutConfig`

### 2. Context над Props
Никакого prop drilling - всё через `useAppContext()`

### 3. Декомпозиция
Каждая папка отвечает за свою область:
- `types/` - только типы
- `context/` - состояние и контекст
- `hooks/` - переиспользуемая логика
- `layouts/` - рендеринг layout'ов
- `components/` - UI компоненты

### 4. Автоматизация
Layout определяется автоматически на основе маршрута

### 5. Расширяемость
Легко добавить новый layout или функционал

## 📦 Экспорты

```tsx
// Главный компонент
export { AppLayout } from './AppLayout';

// Контекст и хуки
export { useAppContext } from './context';
export { useLayoutMode, useNavigation } from './hooks';

// Типы
export type {
  AppLayoutConfig,
  PublicLayoutConfig,
  PrivateLayoutConfig,
  RouteConfig,
  NavigationItem,
  DashboardMenuItem,
} from './types';
```

## 🎯 Преимущества

✅ **Одно место подключения** - только в `_app.tsx`
✅ **Нет prop drilling** - всё через контекст
✅ **Автоматический роутинг** - layout определяется сам
✅ **Типобезопасность** - TypeScript везде
✅ **Легкая настройка** - один конфиг объект
✅ **Декомпозиция** - чистая структура папок
✅ **Переиспользование** - хуки для всего
