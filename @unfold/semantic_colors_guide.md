# 🎨 Semantic Colors Guide - Unfold Style

Это руководство показывает, как правильно использовать семантические цвета в стиле Unfold для кросс-темной поддержки.

## 🎯 Основные принципы

### 1. **Семантические цвета вместо конкретных**
```css
/* ❌ Плохо - конкретные цвета */
.bg-gray-100 { background-color: #f3f4f6; }
.text-gray-600 { color: #4b5563; }

/* ✅ Хорошо - семантические цвета */
.bg-base-100 { background-color: var(--color-base-100); }
.text-font-default-light { color: var(--color-font-default-light); }
```

### 2. **CSS переменные для тем**
```css
:root {
  /* Base colors */
  --color-base-50: 249, 250, 251;
  --color-base-100: 243, 244, 246;
  --color-base-200: 229, 231, 235;
  --color-base-300: 209, 213, 219;
  --color-base-400: 156, 163, 175;
  --color-base-500: 107, 114, 128;
  --color-base-600: 75, 85, 99;
  --color-base-700: 55, 65, 81;
  --color-base-800: 31, 41, 55;
  --color-base-900: 17, 24, 39;
  --color-base-950: 3, 7, 18;

  /* Font colors */
  --color-font-subtle-light: var(--color-base-500);
  --color-font-subtle-dark: var(--color-base-400);
  --color-font-default-light: var(--color-base-600);
  --color-font-default-dark: var(--color-base-300);
  --color-font-important-light: var(--color-base-900);
  --color-font-important-dark: var(--color-base-100);
}
```

## 🎨 Цветовая система

### Base Colors (Базовые цвета)
```css
/* Фоны */
.bg-base-50    /* Самый светлый фон */
.bg-base-100   /* Легкий фон */
.bg-base-200   /* Фон для карточек */
.bg-base-300   /* Фон для ховера */
.bg-base-400   /* Фон для активных элементов */
.bg-base-500   /* Нейтральный фон */
.bg-base-600   /* Темный фон */
.bg-base-700   /* Очень темный фон */
.bg-base-800   /* Фон для сайдбара */
.bg-base-900   /* Основной темный фон */
.bg-base-950   /* Самый темный фон */
```

### Font Colors (Цвета текста)
```css
/* Семантические цвета текста */
.text-font-subtle-light      /* Слабый текст (светлая тема) */
.text-font-subtle-dark       /* Слабый текст (темная тема) */
.text-font-default-light     /* Обычный текст (светлая тема) */
.text-font-default-dark      /* Обычный текст (темная тема) */
.text-font-important-light   /* Важный текст (светлая тема) */
.text-font-important-dark    /* Важный текст (темная тема) */
```

### Primary Colors (Основные цвета)
```css
/* Primary цвета для акцентов */
.bg-primary-50
.bg-primary-100
.bg-primary-200
.bg-primary-300
.bg-primary-400
.bg-primary-500
.bg-primary-600
.bg-primary-700
.bg-primary-800
.bg-primary-900
.bg-primary-950
```

## 🔄 Кросс-темная поддержка

### 1. **Автоматическое переключение**
```html
<!-- Tailwind автоматически применяет dark: классы -->
<div class="bg-white dark:bg-base-900">
  <p class="text-font-default-light dark:text-font-default-dark">
    Текст автоматически адаптируется под тему
  </p>
</div>
```

### 2. **Условные стили**
```css
/* В CSS файле */
.card {
  @apply bg-white border border-base-200 dark:bg-base-900 dark:border-base-700;
}

.button {
  @apply bg-primary-600 text-white hover:bg-primary-700 
         dark:bg-primary-500 dark:hover:bg-primary-600;
}
```

## 📋 Практические примеры

### Карточка
```html
<div class="bg-white border border-base-200 rounded-default shadow-xs 
            dark:bg-base-900 dark:border-base-700">
  <div class="p-4">
    <h3 class="text-font-important-light dark:text-font-important-dark font-semibold">
      Заголовок
    </h3>
    <p class="text-font-default-light dark:text-font-default-dark mt-2">
      Описание карточки
    </p>
  </div>
</div>
```

### Кнопка
```html
<button class="bg-primary-600 hover:bg-primary-700 text-white 
               px-4 py-2 rounded-default transition-colors
               dark:bg-primary-500 dark:hover:bg-primary-600">
  Нажми меня
</button>
```

### Навигация
```html
<nav class="bg-base-50 border-r border-base-200 
            dark:bg-base-900 dark:border-base-800">
  <a href="#" class="text-font-default-light hover:text-primary-600
                     dark:text-font-default-dark dark:hover:text-primary-500">
    Ссылка
  </a>
</nav>
```

### Форма
```html
<form class="space-y-4">
  <input type="text" 
         class="bg-white border border-base-200 px-3 py-2 rounded-default
                dark:bg-base-900 dark:border-base-700
                text-font-default-light dark:text-font-default-dark
                placeholder-font-subtle-light dark:placeholder-font-subtle-dark">
</form>
```

## 🎯 Рекомендации

### 1. **Используйте семантические имена**
```css
/* ❌ Плохо */
.text-gray-600
.bg-gray-100

/* ✅ Хорошо */
.text-font-default-light
.bg-base-100
```

### 2. **Всегда добавляйте dark: варианты**
```css
/* ❌ Плохо - только светлая тема */
.bg-white
.text-gray-600

/* ✅ Хорошо - обе темы */
.bg-white dark:bg-base-900
.text-font-default-light dark:text-font-default-dark
```

### 3. **Используйте opacity для эффектов**
```css
/* Ховер эффекты */
.hover:bg-base-50 dark:hover:bg-base-800
.hover:text-base-700 dark:hover:text-base-200

/* Overlay эффекты */
.bg-base-900/80  /* 80% opacity */
.bg-white/[.06]  /* 6% opacity */
```

### 4. **Группируйте связанные стили**
```css
/* Компонент карточки */
.card {
  @apply bg-white border border-base-200 rounded-default shadow-xs
         dark:bg-base-900 dark:border-base-700;
}

.card-title {
  @apply text-font-important-light dark:text-font-important-dark font-semibold;
}

.card-content {
  @apply text-font-default-light dark:text-font-default-dark;
}
```

## 🔧 Настройка в проекте

### 1. **Добавьте CSS переменные**
```css
/* tailwind.config.js или styles.css */
:root {
  --color-base-50: 249, 250, 251;
  --color-base-100: 243, 244, 246;
  /* ... остальные цвета */
}
```

### 2. **Настройте Tailwind**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        base: {
          50: 'rgb(var(--color-base-50))',
          100: 'rgb(var(--color-base-100))',
          // ... остальные
        },
        font: {
          'subtle-light': 'var(--color-font-subtle-light)',
          'subtle-dark': 'var(--color-font-subtle-dark)',
          // ... остальные
        }
      }
    }
  }
}
```

### 3. **Используйте в компонентах**
```html
<!-- Компонент с семантическими цветами -->
<div class="bg-base-100 border border-base-200 rounded-default
            dark:bg-base-800 dark:border-base-700">
  <h2 class="text-font-important-light dark:text-font-important-dark">
    Заголовок
  </h2>
  <p class="text-font-default-light dark:text-font-default-dark">
    Контент
  </p>
</div>
```

## 🎨 Примеры из Unfold

### Навигация
```html
<nav class="bg-base-50 flex flex-col min-h-screen 
            dark:text-font-default-dark dark:bg-base-950/20">
  <a class="text-font-default-light hover:text-primary-600
            dark:text-font-default-dark dark:hover:text-primary-500">
    Навигация
  </a>
</nav>
```

### Таблицы
```html
<table class="w-full">
  <tr class="bg-white dark:bg-base-900">
    <td class="text-font-default-light dark:text-font-default-dark">
      Ячейка
    </td>
  </tr>
  <tr class="bg-base-50 dark:bg-white/[.02]">
    <td class="text-font-default-light dark:text-font-default-dark">
      Альтернативная ячейка
    </td>
  </tr>
</table>
```

### Формы
```html
<input type="text" 
       class="bg-white border border-base-200 px-3 py-2 rounded-default
              dark:bg-base-900 dark:border-base-700
              text-font-default-light dark:text-font-default-dark
              placeholder-font-subtle-light dark:placeholder-font-subtle-dark">
```

## 🚀 Преимущества подхода

1. **Автоматическая адаптация** - цвета автоматически подстраиваются под тему
2. **Семантичность** - цвета имеют смысл, а не просто названия
3. **Консистентность** - единая система цветов по всему приложению
4. **Легкость изменения** - изменить тему можно через CSS переменные
5. **Type safety** - Tailwind проверяет правильность классов

## 📚 Дополнительные ресурсы

- [Unfold Documentation](https://unfoldadmin.com/)
- [Tailwind CSS Dark Mode](https://tailwindcss.com/docs/dark-mode)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
