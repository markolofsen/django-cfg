/**
 * Admin English Translations
 */

export interface AdminTranslations {
  nav: {
    home: string;
    dashboard: string;
    admin: string;
    profile: string;
    settings: string;
  };
  pages: {
    home: {
      title: string;
      subtitle: string;
    };
    dashboard: {
      title: string;
      welcome: string;
    };
  };
  common: {
    loading: string;
    error: string;
    retry: string;
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    create: string;
    search: string;
    noResults: string;
  };
}

export const en: AdminTranslations = {
  nav: {
    home: 'Home',
    dashboard: 'Dashboard',
    admin: 'Admin',
    profile: 'Profile',
    settings: 'Settings',
  },
  pages: {
    home: {
      title: 'Welcome',
      subtitle: 'Django-CFG Admin Dashboard',
    },
    dashboard: {
      title: 'Dashboard',
      welcome: 'Welcome back!',
    },
  },
  common: {
    loading: 'Loading...',
    error: 'An error occurred',
    retry: 'Retry',
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    search: 'Search...',
    noResults: 'No results found',
  },
};
