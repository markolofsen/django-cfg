import type { PathKeys, TranslationFn } from './utils/path-keys'

/**
 * All valid translation keys for base I18nTranslations
 *
 * @example
 * ```typescript
 * import type { I18nKeys } from '@djangocfg/i18n'
 *
 * const key: I18nKeys = 'ui.form.save' // OK
 * const bad: I18nKeys = 'ui.form.typo' // Error
 * ```
 */
export type I18nKeys = PathKeys<I18nTranslations>

/**
 * Type-safe translation function for base translations
 */
export type I18nTranslationFn = TranslationFn<I18nTranslations>

/**
 * Core translation structure for @djangocfg packages
 *
 * This type defines all translatable strings used across the component library.
 * Each package section contains its own namespace to avoid conflicts.
 */
export interface I18nTranslations {
  /**
   * UI Components (ui-core)
   */
  ui: {
    /** Select/Combobox/MultiSelect components */
    select: {
      placeholder: string
      search: string
      noResults: string
      selectAll: string
      clearAll: string
      /** Template: "+{count} more" */
      moreItems: string
      loading: string
    }

    /** Pagination components */
    pagination: {
      previous: string
      next: string
      first: string
      last: string
      /** Template: "Page {page}" */
      page: string
      /** Template: "of {total}" */
      of: string
      /** Template: "{from}-{to} of {total}" */
      showing: string
    }

    /** Dialog/Modal components */
    dialog: {
      close: string
      confirm: string
      cancel: string
      ok: string
      yes: string
      no: string
      delete: string
      save: string
      discard: string
      alertTitle: string
      confirmTitle: string
      confirmDelete: string
      promptTitle: string
      promptPlaceholder: string
    }

    /** Form components and validation */
    form: {
      submit: string
      cancel: string
      save: string
      delete: string
      edit: string
      create: string
      update: string
      reset: string
      clear: string
      loading: string
      saving: string
      deleting: string
      required: string
      optional: string
      /** Template: "{min} characters minimum" */
      minLength: string
      /** Template: "{max} characters maximum" */
      maxLength: string
      invalidEmail: string
      invalidUrl: string
      invalidPhone: string
      passwordMismatch: string
    }

    /** Date/Time components */
    datetime: {
      today: string
      yesterday: string
      tomorrow: string
      now: string
      /** Template: "{count} seconds ago" */
      secondsAgo: string
      /** Template: "{count} minutes ago" */
      minutesAgo: string
      /** Template: "{count} hours ago" */
      hoursAgo: string
      /** Template: "{count} days ago" */
      daysAgo: string
      pickDate: string
      pickTime: string
      pickDateTime: string
      pickDateRange: string
    }

    /** File upload components */
    file: {
      upload: string
      uploading: string
      dragDrop: string
      browse: string
      remove: string
      /** Template: "Max size: {size}" */
      maxSize: string
      invalidType: string
      tooLarge: string
    }

    /** Table components */
    table: {
      noData: string
      loading: string
      /** Template: "Showing {from}-{to} of {total}" */
      showing: string
      rowsPerPage: string
      sortAsc: string
      sortDesc: string
      filter: string
      clearFilters: string
      selectAll: string
      deselectAll: string
      /** Template: "{count} selected" */
      selected: string
    }

    /** Common actions */
    actions: {
      view: string
      copy: string
      copied: string
      copyToClipboard: string
      download: string
      share: string
      refresh: string
      retry: string
      expand: string
      collapse: string
      showMore: string
      showLess: string
      seeAll: string
      goBack: string
      remove: string
      previousSlide: string
      nextSlide: string
    }

    /** Phone input */
    phone: {
      searchCountries: string
      noCountries: string
    }

    /** Navigation (for tabs, mobile sheets, etc.) */
    navigation: {
      /** Title for navigation sheet/modal */
      title: string
    }

    /** Common states */
    states: {
      loading: string
      empty: string
      error: string
      success: string
      warning: string
      info: string
      pending: string
      active: string
      inactive: string
      enabled: string
      disabled: string
    }

    /** Error messages */
    errors: {
      generic: string
      network: string
      timeout: string
      notFound: string
      unauthorized: string
      forbidden: string
      serverError: string
      validation: string
      unknown: string
    }
  }

  /**
   * Layout components (@djangocfg/layouts)
   */
  layouts: {
    /** Sidebar component */
    sidebar: {
      toggle: string
      collapse: string
      expand: string
    }

    /** Navigation */
    navigation: {
      menu: string
      home: string
      back: string
      forward: string
      toggleMobile: string
      breadcrumb: string
    }

    /** Profile/User section */
    profile: {
      settings: string
      account: string
      logout: string
      login: string
      signUp: string
      signOut: string
      userMenu: string
      language: string
    }

    /** Theme */
    theme: {
      toggle: string
      light: string
      dark: string
      system: string
    }

    /** Search */
    search: {
      placeholder: string
      noResults: string
      recentSearches: string
      clearHistory: string
    }

    /** Mobile drawer */
    mobile: {
      closeMenu: string
    }

    /** Error pages */
    errors: {
      somethingWentWrong: string
      tryRefreshing: string
      refreshPage: string
      goBack: string
      goHome: string
      needHelp: string
      contactSupport: string
      /** Link to the public service-status page. Rendered only when the
       *  consumer passes `statusUrl` to `ErrorLayout`. */
      checkStatus: string
      /** Template: "If the problem persists, please contact {email}" */
      persistsContact: string
      /** Error titles */
      error: string
      badRequest: string
      authRequired: string
      accessDenied: string
      pageNotFound: string
      requestTimeout: string
      serverError: string
      badGateway: string
      serviceUnavailable: string
      gatewayTimeout: string
      /** Error descriptions */
      badRequestDesc: string
      authRequiredDesc: string
      accessDeniedDesc: string
      pageNotFoundDesc: string
      requestTimeoutDesc: string
      serverErrorDesc: string
      badGatewayDesc: string
      serviceUnavailableDesc: string
      gatewayTimeoutDesc: string
      unknownErrorDesc: string
    }

    /** Push notifications */
    push: {
      enableNotifications: string
      stayUpdated: string
      enable: string
      notNow: string
      dismiss: string
    }

    /** Auth dialog */
    auth: {
      authRequired: string
      pleaseSignIn: string
      goToSignIn: string
      /** Identifier step */
      identifier: {
        title: string
        subtitle: {
          email: string
          phone: string
        }
        placeholder: {
          email: string
          phone: string
        }
        button: string
        oauth: {
          /** {provider} is the provider's brand name: "Continue with GitHub" */
          continueWith: string
          /** Accessible name of the group of provider buttons */
          groupLabel: string
        }
        channel: {
          email: string
          phone: string
        }
      }
      /** OTP step */
      otp: {
        title: string
        subtitle: string
        button: string
        resend: string
        changeEmail: string
        changePhone: string
        /** "Open your email" button — {provider} is the webmail name, e.g. Gmail */
        openMailbox: string
      }
      /** Two-factor step */
      twoFactor: {
        title: string
        subtitle: {
          totp: string
          backup: string
        }
        placeholder: {
          backup: string
        }
        button: string
        toggle: {
          toBackup: string
          toTotp: string
        }
      }
      /** Setup step */
      setup: {
        loading: {
          title: string
          button: string
        }
        qrCode: {
          title: string
          subtitle: string
          manualEntry: string
          confirmPrompt: string
          button: string
          skip: string
        }
        complete: {
          title: string
          subtitle: string
          instruction: string
          copyAll: string
          copied: string
          done: string
        }
      }
      /** Success message */
      success: {
        message: string
        /** What the pause before the redirect is for. */
        redirecting: string
      }
      /** Divider */
      divider: {
        or: string
      }
      /** Provider sign-in: callback card and error copy (brand names stay untranslated) */
      oauth: {
        signingIn: string
        /** {provider} is the provider's brand name, e.g. Google */
        signingInBody: string
        /** The inline notice shown on the sign-in form after a provider round trip failed */
        notice: {
          /** Title of the notice for `link_not_allowed` (staff accounts sign in by email code) */
          linkNotAllowedTitle: string
          /** {provider} is the provider's brand name */
          retry: string
          dismiss: string
          /** Developer-only line under the `origin_not_allowed` notice. {origin}: the page origin, {id}: provider id */
          originNotAllowedHint: string
        }
        error: {
          invalid_state: string
          oauth_exchange_failed: string
          invalid_id_token: string
          email_missing: string
          email_not_verified: string
          hosted_domain_not_allowed: string
          account_inactive: string
          link_not_allowed: string
          rate_limited: string
          provider_unavailable: string
          /** The site cannot start this provider's sign-in (origin or redirect not configured); {provider} is the brand name */
          not_configured: string
          cancelled: string
          generic: string
        }
      }
      /** Footer */
      footer: {
        terms: string
        privacy: string
        support: string
      }
      /** Dev mode */
      dev: {
        anyCodeWorks: string
      }
    }

    /** PWA Install */
    pwa: {
      /** A2HS Hint */
      addToHomeScreen: string
      installApp: string
      tapToLearnHow: string
      clickToSeeGuide: string
      tapToInstall: string
      installing: string
      dismiss: string
      appLogo: string
      /** iOS Guide */
      iosTitle: string
      iosDescription: string
      iosStep1Title: string
      iosStep1Desc: string
      iosStep2Title: string
      iosStep2Desc: string
      iosStep3Title: string
      iosStep3Desc: string
      gotIt: string
      /** Desktop Guide */
      desktopTitle: string
      desktopDescription: string
      desktopDescSafari: string
      desktopTip: string
      desktopFirefoxNote: string
      /** Desktop steps - Chromium */
      chromiumStep1Title: string
      chromiumStep1Desc: string
      chromiumStep2Title: string
      chromiumStep2Desc: string
      chromiumStep3Title: string
      chromiumStep3Desc: string
      /** Desktop steps - Firefox */
      firefoxStep1Title: string
      firefoxStep1Desc: string
      firefoxStep2Title: string
      firefoxStep2Desc: string
      firefoxStep3Title: string
      firefoxStep3Desc: string
      /** Desktop steps - Safari */
      safariStep1Title: string
      safariStep1Desc: string
      safariStep2Title: string
      safariStep2Desc: string
      /** Desktop steps - Unknown */
      unknownStep1Title: string
      unknownStep1Desc: string
      unknownStep2Title: string
      unknownStep2Desc: string
      unknownStep3Title: string
      unknownStep3Desc: string
      close: string
    }

    /** Profile page */
    profilePage: {
      /** Page title */
      title: string
      /** Sections */
      account: string
      personalInfo: string
      work: string
      security: string
      actions: string
      /** Fields */
      email: string
      firstName: string
      lastName: string
      company: string
      position: string
      phone: string
      /** Values */
      notSet: string
      /** Placeholders for empty fields */
      addFirstName: string
      addLastName: string
      addPhone: string
      addCompany: string
      addPosition: string
      on: string
      off: string
      /** Actions */
      save: string
      saving: string
      cancel: string
      signOut: string
      deleteAccount: string
      deleting: string
      /** 2FA */
      twoFactorAuth: string
      twoFactorEnabled: string
      twoFactorDisabled: string
      enable2FA: string
      /** Avatar */
      avatar: string
      changeAvatar: string
      /** Membership */
      memberSince: string
      /** Placeholders */
      enterField: string
      /** Messages */
      profileUpdated: string
      avatarUpdated: string
      failedToUpdate: string
      failedToUploadAvatar: string
      selectImageFile: string
      fileTooLarge: string
      /** Not authenticated */
      notAuthenticated: string
      pleaseLogIn: string
      /** Delete account dialog */
      deleteAccountTitle: string
      deleteAccountDesc: string
      typeToConfirm: string
      confirmationWord: string
    }
  }

  /**
   * API/Network related messages (@djangocfg/api)
   */
  api: {
    errors: {
      networkError: string
      connectionFailed: string
      requestTimeout: string
      serverUnavailable: string
      invalidResponse: string
      rateLimited: string
    }
    status: {
      connecting: string
      connected: string
      disconnected: string
      reconnecting: string
    }
    /** Logout dialog */
    logout: {
      title: string
      message: string
      confirm: string
      cancel: string
    }
  }

  /**
   * Heavy tools (@djangocfg/ui-tools)
   */
  tools: {
    /** Code viewer/editor */
    code: {
      copyCode: string
      noContent: string
    }

    /** Diagram/Mermaid */
    diagram: {
      title: string
      clickToView: string
    }

    /** Image viewer */
    image: {
      noImage: string
      failedToLoad: string
      zoomIn: string
      zoomOut: string
      fitToView: string
      flipHorizontal: string
      flipVertical: string
      rotate: string
      fullscreen: string
    }

    /** Gallery/Lightbox */
    gallery: {
      noImages: string
      lightbox: string
      previous: string
      next: string
      close: string
      download: string
      share: string
    }

    /** Video player */
    video: {
      play: string
      fullscreen: string
      unavailable: string
    }

    /** Audio player */
    audio: {
      restart: string
      back: string
      forward: string
      volume: string
    }

    /** Color picker */
    color: {
      pick: string
    }

    /** JSON Schema form */
    jsonForm: {
      validationErrors: string
      addItem: string
      addFirstItem: string
      noItems: string
    }

    /** OpenAPI viewer */
    openapi: {
      response: string
      noResponse: string
      required: string
      optional: string
      searchEndpoints: string
      all: string
      methods: string
      path: string
      description: string
      navigation: string
      previous: string
      next: string
      bearerToken: string
    }

    /** JSON form */
    form: {
      title: string
    }

    /** Tour/onboarding */
    tour: {
      next: string
      previous: string
      skip: string
      finish: string
      close: string
      /** Template: "Step {current} of {total}" */
      stepOf: string
    }

    /** File uploader */
    upload: {
      dragDrop: string
      dropHere: string
      /** Template: "Max {size}MB per file" */
      maxSize: string
      uploading: string
      uploaded: string
      failed: string
      retry: string
      remove: string
      cancel: string
      paused: string
      pending: string
    }
  }
}

/**
 * Deeply partial type for translation overrides
 */
export type PartialTranslations = DeepPartial<I18nTranslations>

/**
 * Helper type for deep partial
 */
export type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T

/**
 * Supported locale codes
 */
export type LocaleCode = 'en' | 'ru' | 'ko' | string

/**
 * I18n context value
 */
export interface I18nContextValue {
  /** Current locale code */
  locale: LocaleCode
  /** Current translations */
  translations: I18nTranslations
  /**
   * Get translated string by key path
   * @param key - Dot-notation key path (e.g., "ui.select.placeholder")
   * @param params - Optional interpolation parameters
   */
  t: (key: string, params?: Record<string, string | number>) => string
  /**
   * Change current locale
   */
  setLocale: (locale: LocaleCode) => void
}

/**
 * I18n provider props
 */
export interface I18nProviderProps {
  children: React.ReactNode
  /** Initial locale */
  locale?: LocaleCode
  /** Translations for the current locale */
  translations?: I18nTranslations | PartialTranslations
  /** All available translations by locale */
  allTranslations?: Record<LocaleCode, I18nTranslations | PartialTranslations>
  /** Callback when locale changes */
  onLocaleChange?: (locale: LocaleCode) => void
}
