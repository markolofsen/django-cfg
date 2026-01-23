/**
 * Admin Russian Translations
 */

import type { AdminTranslations } from './en';

export const ru: AdminTranslations = {
  nav: {
    home: 'Главная',
    dashboard: 'Панель управления',
    admin: 'Администрирование',
    profile: 'Профиль',
    settings: 'Настройки',
  },
  pages: {
    home: {
      title: 'Добро пожаловать',
      subtitle: 'Django-CFG Панель администратора',
    },
    dashboard: {
      title: 'Панель управления',
      welcome: 'С возвращением!',
    },
  },
  common: {
    loading: 'Загрузка...',
    error: 'Произошла ошибка',
    retry: 'Повторить',
    save: 'Сохранить',
    cancel: 'Отмена',
    delete: 'Удалить',
    edit: 'Редактировать',
    create: 'Создать',
    search: 'Поиск...',
    noResults: 'Ничего не найдено',
  },
};
