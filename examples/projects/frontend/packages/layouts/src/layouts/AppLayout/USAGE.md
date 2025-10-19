# AppLayout - Usage Guide

## 🎯 Философия

**Одна точка входа. Ноль prop drilling. Максимум умности.**

AppLayout - это единственный компонент, который нужен для управления всеми layout'ами в приложении.

## 🚀 Quick Start

### 1. Создай конфиг (один раз)

```typescript
// apps/cloud/src/core/appLayoutConfig.ts
import type { AppLayoutConfig } from '@djangocfg/layouts';

export const appLayoutConfig: AppLayoutConfig = {
  app: {
    name: 'My App',
    logoPath: '/logo.svg',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL!,
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
    navigation: {
      homePath: '/',
      menuSections: [
        {
          title: 'Main',
          items: [
            { label: 'Home', path: '/' },
            { label: 'Docs', path: '/docs' },
          ],
        },
      ],
    },
    userMenu: {
      profilePath: '/profile',
    },
    footer: {
      badge: { icon: MyIcon, text: 'My App' },
      links: { privacy: '/privacy', terms: '/terms' },
      menuSections: [],
    },
  },
  privateLayout: {
    homeHref: '/',
    profileHref: '/profile',
    showChat: true,
    menuGroups: [
      {
        label: 'Main',
        order: 1,
        items: [
          { path: '/dashboard', label: 'Dashboard', icon: DashboardIcon },
        ],
      },
    ],
    contentPadding: 'default',
  },
};
```

### 2. Используй в _app.tsx (один раз)

```typescript
// pages/_app.tsx
import { AppLayout } from '@djangocfg/layouts';
import { appLayoutConfig } from '@/core';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AppLayout config={appLayoutConfig}>
      <Component {...pageProps} />
    </AppLayout>
  );
}
```

### 3. Всё! 🎉

Теперь:
- ✅ Public страницы автоматически получат MainLayout
- ✅ Private страницы (`/private/*`) автоматически получат DashboardLayout
- ✅ Auth страницы (`/auth/*`) получат минимальный layout
- ✅ Все компоненты имеют доступ к конфигу через `useAppContext()`

## 🎨 Использование в компонентах

### Доступ к конфигу и состоянию

```typescript
import { useAppContext } from '@djangocfg/layouts';

function MyComponent() {
  const {
    config,                  // Весь конфиг
    layoutMode,              // 'public' | 'private' | 'auth'
    currentPath,             // Текущий путь
    mobileMenuOpen,          // Состояние мобильного меню
    toggleMobileMenu,        // Функция для переключения
    sidebarCollapsed,        // Sidebar в dashboard
    toggleSidebar,           // Функция для sidebar
  } = useAppContext();

  return (
    <button onClick={toggleMobileMenu}>
      Menu
    </button>
  );
}
```

### Использование хуков

```typescript
import { useLayoutMode, useNavigation } from '@djangocfg/layouts';

function MyComponent() {
  const mode = useLayoutMode();
  const { isActive, getPageTitle } = useNavigation();

  if (mode === 'private') {
    return <DashboardContent />;
  }

  return <PublicContent />;
}
```

### Доступ к auth

```typescript
import { useAuth } from '@djangocfg/layouts';

function UserProfile() {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Not authenticated</div>;
  }

  return (
    <div>
      <p>Welcome, {user.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## 🔧 Настройка layout'ов

### Public Layout

Управляется через `config.publicLayout`:

```typescript
publicLayout: {
  navigation: {
    homePath: '/',
    menuSections: [/* меню для navbar */],
  },
  userMenu: {
    dashboardPath: '/dashboard',  // Опционально
    profilePath: '/profile',
  },
  footer: {
    badge: { icon: MyIcon, text: 'App Name' },
    links: { privacy: '/privacy', terms: '/terms' },
    menuSections: [/* меню для footer */],
  },
}
```

### Private Layout

Управляется через `config.privateLayout`:

```typescript
privateLayout: {
  homeHref: '/',
  profileHref: '/profile',
  showChat: true,                    // Показывать чат
  contentPadding: 'default',         // или 'none'
  menuGroups: [
    {
      label: 'Main',
      order: 1,
      items: [
        { path: '/dashboard', label: 'Dashboard', icon: Icon },
      ],
    },
  ],
  headerActions: <CustomActions />,  // Опционально
}
```

## 📊 Структура проекта

```
apps/cloud/
├── src/
│   ├── core/
│   │   ├── appLayoutConfig.ts      ← Единый конфиг
│   │   ├── routes.ts               ← Определение маршрутов
│   │   └── settings.ts             ← Настройки приложения
│   │
│   └── pages/
│       ├── _app.tsx                ← AppLayout подключается здесь
│       ├── index.tsx               ← Публичная страница (auto)
│       ├── auth/
│       │   └── index.tsx           ← Auth layout (auto)
│       └── private/
│           └── dashboard.tsx       ← Dashboard layout (auto)
```

## 🎯 Преимущества

### ✅ Нет prop drilling
Всё через контекст - никаких пропсов вниз по дереву

### ✅ Автоматический роутинг
Layout определяется автоматически на основе пути

### ✅ Единый конфиг
Один объект конфигурации для всего приложения

### ✅ Типобезопасность
TypeScript везде

### ✅ Легкое тестирование
Весь функционал доступен через хуки

### ✅ Простота использования
Подключил один раз в `_app.tsx` - и всё работает

## 🔍 Как это работает

```
_app.tsx
  ↓
AppLayout (config)
  ↓
CoreProviders (Theme, Auth, Toaster)
  ↓
AppContextProvider (State management)
  ↓
LayoutRouter (Auto-detect route)
  ↓
├─ PublicLayout     (/)
├─ PrivateLayout    (/private/*)
└─ AuthLayout       (/auth/*)
     ↓
   Page Component
```

## 💡 Best Practices

### 1. Один конфиг
Храни всю конфигурацию в одном файле `appLayoutConfig.ts`

### 2. Используй хуки
Вместо прямого доступа к контексту, используй специализированные хуки

### 3. Не гоняй пропсы
Если данные доступны в контексте - берите их там, не передавайте пропсами

### 4. Кастомные layout'ы
Если нужен кастомный layout для страницы - используй `getLayout`:

```typescript
// pages/special.tsx
import { CustomLayout } from '@/layouts';

function SpecialPage() {
  return <div>Special content</div>;
}

SpecialPage.getLayout = (page) => {
  return <CustomLayout>{page}</CustomLayout>;
};

export default SpecialPage;
```

## 🐛 Troubleshooting

### "useAppContext must be used within AppContextProvider"

Убедись что компонент рендерится внутри `<AppLayout>`

### Layout не меняется

Проверь `routes.detectors` в конфиге - они определяют тип layout'а

### Sidebar не работает

Используй `useAppContext()` для доступа к `sidebarCollapsed` и `toggleSidebar`
