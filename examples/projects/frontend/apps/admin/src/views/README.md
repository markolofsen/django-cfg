# Demo App Views

React views (pages) для Demo приложения, построенные на основе **@djangocfg/ui** компонентов и SWR контекстов.

## 📁 Структура

```
views/
├── dashboard/    # Dashboard overview
├── profile/      # User profile management
├── blog/         # Blog posts list
├── shop/         # Products catalog
└── debug_ipc/    # WebSocket debugging (dev only)
```

## 🎨 Архитектура

Все views следуют единой архитектуре:

### 1. **UI Components** (@djangocfg/ui)
```tsx
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Input
} from '@djangocfg/ui';
```

### 2. **SWR Hooks** (из generated API)
```tsx
import { useBlogPostsList } from '../../api/generated/shop/_utils/hooks';
```

### 3. **Contexts** (высокоуровневая логика)
```tsx
import { useProfile, useShop, useBlog } from '../../contexts';
```

## 📄 Views Overview

### DashboardView (`/views/dashboard/`)

**Цель:** Главная страница с обзором статистики

**Данные:**
- Профиль пользователя (`useProfile`)
- Статистика магазина (`useShop`)
- Статистика блога (`useBlog`)

**Компоненты:**
- Stats cards (4 колонки)
- User activity summary
- Shop overview
- Blog overview
- Popular products
- Popular posts

**Особенности:**
- Автоматическая загрузка с skeleton
- Отображение трендов (+12.5%, +8.2%)
- Адаптивная сетка (responsive grid)

### ProfileView (`/views/profile/`)

**Цель:** Управление профилем пользователя

**Данные:**
- Текущий профиль (`useProfile`)
- Редактируемые поля (company, job_title, social links)

**Функциональность:**
- Просмотр профиля
- Режим редактирования (toggle)
- Валидация форм
- Toast уведомления
- Статистика активности

**Поля:**
- Company & Job Title
- Website, GitHub, Twitter, LinkedIn
- Activity stats (posts, comments, orders)

### BlogView (`/views/blog/`)

**Цель:** Список всех постов блога

**Данные:**
- Посты (`useBlogPostsList` SWR hook)
- Категории и теги (`useBlog` context)

**Функциональность:**
- Поиск по заголовку
- Фильтр по категории
- Фильтр по статусу (published/draft/archived)
- Клик на пост → переход на детальную страницу
- Создание нового поста

**Отображение:**
- Карточки постов с:
  - Заголовок и excerpt
  - Featured image (если есть)
  - Badges (status, featured)
  - Статистика (views, likes, comments)
  - Теги
  - Автор и категория

### ShopView (`/views/shop/`)

**Цель:** Каталог продуктов

**Данные:**
- Продукты (`useShopProductsList` SWR hook)
- Категории (`useShop` context)

**Функциональность:**
- Поиск по названию
- Фильтр по категории
- Фильтр по статусу (active/inactive/out_of_stock)
- Клик на продукт → переход на страницу продукта

**Отображение:**
- Grid (3 колонки на desktop)
- Карточки продуктов с:
  - Изображение (aspect-square)
  - Badges (featured, sale, out of stock)
  - Цена (с зачеркнутой старой ценой при скидке)
  - Категория
  - Статистика (views, sales, stock)

## 🛠️ Usage Examples

### Использование в Next.js Pages

```tsx
// pages/index.tsx
import { DashboardView } from '../src/views';

export default function HomePage() {
  return <DashboardView />;
}
```

```tsx
// pages/profile.tsx
import { ProfileView } from '../src/views';

export default function ProfilePage() {
  return <ProfileView />;
}
```

### Использование в Next.js App Router

```tsx
// app/dashboard/page.tsx
import { DashboardView } from '@/views';

export default function DashboardPage() {
  return <DashboardView />;
}
```

### Кастомизация

```tsx
// Расширение DashboardView
import DashboardView from './views/dashboard';
import { Card } from '@djangocfg/ui';

export default function CustomDashboard() {
  return (
    <>
      <DashboardView />

      {/* Дополнительный контент */}
      <Card>
        <CardHeader>
          <CardTitle>Custom Section</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Additional content here</p>
        </CardContent>
      </Card>
    </>
  );
}
```

## 🎨 Дизайн Паттерны

### 1. Loading States

Все views используют skeleton loading:

```tsx
if (isLoading) {
  return (
    <div className="grid gap-4">
      {[...Array(3)].map((_, i) => (
        <Card key={i}>
          <CardHeader>
            <div className="h-6 w-3/4 bg-muted animate-pulse rounded" />
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}
```

### 2. Error States

```tsx
if (error) {
  return (
    <Card>
      <CardContent className="py-8">
        <p className="text-center text-destructive">Failed to load data</p>
      </CardContent>
    </Card>
  );
}
```

### 3. Empty States

```tsx
if (data.length === 0) {
  return (
    <Card>
      <CardContent className="py-12">
        <div className="text-center space-y-3">
          <Icon className="h-12 w-12 mx-auto text-muted-foreground" />
          <h3 className="text-lg font-medium">No items found</h3>
          <Button onClick={handleCreate}>Create New</Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 4. Responsive Design

```tsx
{/* Mobile: 1 column, Tablet: 2 columns, Desktop: 3 columns */}
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
  {items.map(item => <ItemCard key={item.id} {...item} />)}
</div>
```

### 5. Toast Notifications

```tsx
import { useToast } from '@djangocfg/ui';

const { toast } = useToast();

const handleSave = async () => {
  try {
    await updateProfile(data);
    toast({
      title: 'Success',
      description: 'Profile updated successfully',
    });
  } catch (err) {
    toast({
      title: 'Error',
      description: 'Failed to update profile',
      variant: 'destructive',
    });
  }
};
```

## 🔌 Интеграция с Routing

### Next.js Pages Router

```tsx
// pages/blog/index.tsx
import { BlogView } from '@/views';
export default BlogView;

// pages/blog/[slug].tsx
import { BlogPostDetailView } from '@/views/blog';
export default BlogPostDetailView;
```

### Next.js App Router

```tsx
// app/blog/page.tsx
import { BlogView } from '@/views';
export default function BlogPage() {
  return <BlogView />;
}
```

## 📊 Data Flow

```
View Component
    ↓
SWR Hook (useBlogPostsList)
    ↓
API Client (generated)
    ↓
Django REST API
    ↓
PostgreSQL Database
```

**Кеширование:**
- SWR автоматически кеширует данные
- Повторные запросы возвращают кеш
- Автоматическая ревалидация после мутаций

## 🎯 Best Practices

### 1. Используйте SWR hooks напрямую для данных
```tsx
// ✅ Good: Прямое использование SWR hook
const { data, isLoading } = useBlogPostsList({ page: 1 });

// ❌ Bad: Fetch в useEffect
useEffect(() => {
  fetch('/api/posts').then(r => r.json()).then(setData);
}, []);
```

### 2. Используйте контексты для высокоуровневой логики
```tsx
// ✅ Good: Контекст для общих данных
const { stats, categories } = useBlog();

// ❌ Bad: Повторные запросы в каждом компоненте
const { data: stats } = useBlogStats();
const { data: categories } = useBlogCategories();
```

### 3. Обрабатывайте все состояния
```tsx
// ✅ Good: Loading, Error, Empty, Success
if (isLoading) return <Skeleton />;
if (error) return <ErrorState />;
if (data.length === 0) return <EmptyState />;
return <DataDisplay data={data} />;
```

### 4. Используйте UI компоненты из @djangocfg/ui
```tsx
// ✅ Good: Готовые компоненты
import { Card, Button } from '@djangocfg/ui';

// ❌ Bad: Кастомные стили
<div className="p-4 border rounded shadow-sm">
```

## 🚀 Performance

### Оптимизация

1. **SWR дедупликация** - множество компонентов → один запрос
2. **Skeleton loading** - мгновенный UI feedback
3. **Responsive images** - оптимизация изображений
4. **Lazy loading** - подгрузка по необходимости

### Bundle Size

- Views: ~15-20KB каждый (minified + gzipped)
- @djangocfg/ui: ~50KB (tree-shakeable)
- SWR: ~5KB

## 📝 TODO

Будущие улучшения:

- [ ] Blog post detail view
- [ ] Blog post create/edit view
- [ ] Product detail view
- [ ] Orders list view
- [ ] Settings view
- [ ] Pagination components
- [ ] Advanced filters
- [ ] Bulk actions
- [ ] Export functionality

## 🔗 Related

- [Contexts Documentation](../contexts/README.md)
- [UI Components Guide](../../../packages/ui/GUIDE.md)
- [API Documentation](../api/README.md)
