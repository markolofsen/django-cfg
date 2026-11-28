/**
 * Advanced browser detection hook
 *
 * Detects modern browsers including Chromium-based browsers that may
 * incorrectly report as Safari (Arc, Brave, Vivaldi, Comet, etc.)
 */

'use client';

import { useMemo } from 'react';

export interface BrowserInfo {
  // Core browser types
  isChrome: boolean;
  isChromium: boolean; // Any Chromium-based browser
  isSafari: boolean; // Real Safari (WebKit on macOS/iOS)
  isFirefox: boolean;
  isEdge: boolean;
  isOpera: boolean;

  // Modern Chromium-based browsers
  isBrave: boolean;
  isArc: boolean;
  isVivaldi: boolean;
  isYandex: boolean;
  isSamsungBrowser: boolean;
  isUCBrowser: boolean;

  // Additional browsers
  isComet: boolean; // Perplexity's Comet browser (Chromium-based, supports push)
  isOperaMini: boolean; // Opera Mini (does NOT support push notifications)
  isIE: boolean; // Internet Explorer (does NOT support push notifications)

  // In-App Browsers (WebViews) - typically do NOT support push notifications
  isFacebookInApp: boolean; // Facebook's in-app browser
  isInstagramInApp: boolean; // Instagram's in-app browser
  isTikTokInApp: boolean; // TikTok's in-app browser
  isSnapchatInApp: boolean; // Snapchat's in-app browser
  isWeChatInApp: boolean; // WeChat's in-app browser
  isThreadsInApp: boolean; // Threads' in-app browser
  isLinkedInInApp: boolean; // LinkedIn's in-app browser (uses Chrome WebView - supports push on Android)
  isTwitterInApp: boolean; // Twitter/X's in-app browser (uses Chrome WebView - supports push on Android)
  isInAppBrowser: boolean; // Any in-app browser detected
  isWebView: boolean; // Generic WebView detection

  // Browser name
  browserName: string;

  // Engine
  isWebKit: boolean; // Safari's engine
  isBlink: boolean; // Chromium's engine
  isGecko: boolean; // Firefox's engine

  // Push notification support
  /**
   * Whether the browser supports Web Push Notifications.
   * Returns false for browsers known to NOT support push:
   * - Opera Mini (no service worker support)
   * - Internet Explorer (deprecated, no Push API)
   * - UC Browser (unreliable push support)
   * - In-App browsers (Facebook, Instagram, TikTok, Snapchat, etc.)
   * - Generic WebViews (except Twitter/LinkedIn on Android which use Chrome WebView)
   *
   * Note: Comet (Perplexity) is Chromium-based and DOES support push notifications.
   * Note: This is a browser-level check. For full push support,
   * also check 'serviceWorker' in navigator && 'PushManager' in window
   */
  supportsPushNotifications: boolean;

  // iOS specific
  isIOSBrowser: boolean; // Any browser on iOS (all use WebKit, limited push support)

  // For debugging
  userAgent: string;
}

const defaultBrowserInfo: BrowserInfo = {
  isChrome: false,
  isChromium: false,
  isSafari: false,
  isFirefox: false,
  isEdge: false,
  isOpera: false,
  isBrave: false,
  isArc: false,
  isVivaldi: false,
  isYandex: false,
  isSamsungBrowser: false,
  isUCBrowser: false,
  isComet: false,
  isOperaMini: false,
  isIE: false,
  isFacebookInApp: false,
  isInstagramInApp: false,
  isTikTokInApp: false,
  isSnapchatInApp: false,
  isWeChatInApp: false,
  isThreadsInApp: false,
  isLinkedInInApp: false,
  isTwitterInApp: false,
  isInAppBrowser: false,
  isWebView: false,
  browserName: 'unknown',
  isWebKit: false,
  isBlink: false,
  isGecko: false,
  supportsPushNotifications: false,
  isIOSBrowser: false,
  userAgent: '',
};

/**
 * Detect browser with improved accuracy for Chromium-based browsers
 *
 * @example
 * ```tsx
 * const browser = useBrowserDetect();
 *
 * if (browser.isSafari && !browser.isChromium) {
 *   // Real Safari
 * }
 *
 * if (browser.isChromium) {
 *   // Any Chromium-based browser (Chrome, Edge, Brave, Arc, etc.)
 * }
 * ```
 */
export function useBrowserDetect(): BrowserInfo {
  return useMemo(() => {
    if (typeof window === 'undefined') {
      return defaultBrowserInfo;
    }

    const ua = window.navigator.userAgent.toLowerCase();

    // Check for specific browsers first (most specific to least specific)

    // Edge (Chromium-based)
    const isEdge = ua.includes('edg/') || ua.includes('edge/');

    // Brave (check for Brave-specific API)
    // Boundary: `navigator.brave` is a Brave-only extension absent from lib.dom.
    // Declaring the one optional field we read keeps the probe honest without
    // asserting anything about the rest of Navigator.
    const braveAware: Navigator & { brave?: unknown } = window.navigator;
    const isBrave = braveAware.brave != null;

    // Arc (check for Arc-specific markers in UA)
    const isArc = ua.includes('arc/');

    // Vivaldi
    const isVivaldi = ua.includes('vivaldi');

    // Yandex Browser
    const isYandex = ua.includes('yabrowser');

    // Samsung Internet
    const isSamsungBrowser = ua.includes('samsungbrowser');

    // UC Browser
    const isUCBrowser = ua.includes('ucbrowser') || ua.includes('uc browser');

    // Comet Browser (Perplexity's AI browser, Chromium-based)
    const isComet = ua.includes('comet') || ua.includes('perplexity');

    // Opera Mini (does NOT support service workers or push)
    const isOperaMini = ua.includes('opera mini') || ua.includes('opios');

    // Internet Explorer (deprecated, no Push API support)
    const isIE = ua.includes('msie') || ua.includes('trident/');

    // In-App Browsers Detection
    const isFacebookInApp = ua.includes('fban') || ua.includes('fbav') || ua.includes('fb_iab');
    const isInstagramInApp = ua.includes('instagram');
    const isTikTokInApp = ua.includes('tiktok') || ua.includes('bytedancewebview') || ua.includes('bytelocale');
    const isSnapchatInApp = ua.includes('snapchat');
    const isWeChatInApp = ua.includes('micromessenger');
    const isThreadsInApp = ua.includes('barcelona');
    const isLinkedInInApp = ua.includes('linkedinapp');
    const isTwitterInApp = ua.includes('twitter');
    const isPinterestInApp = ua.includes('pinterest');
    const isTelegramInApp = ua.includes('telegram');
    const isLineInApp = ua.includes('line/');
    const isKakaoInApp = ua.includes('kakaotalk');

    // Generic WebView detection
    const isWebView = ua.includes('wv)') ||
                     ua.includes('webview') ||
                     ua.includes('; wv') ||
                     (ua.includes('iphone') && !ua.includes('safari')) ||
                     (ua.includes('ipad') && !ua.includes('safari'));

    // Aggregate: Any in-app browser
    const isInAppBrowser = isFacebookInApp ||
                          isInstagramInApp ||
                          isTikTokInApp ||
                          isSnapchatInApp ||
                          isWeChatInApp ||
                          isThreadsInApp ||
                          isLinkedInInApp ||
                          isTwitterInApp ||
                          isPinterestInApp ||
                          isTelegramInApp ||
                          isLineInApp ||
                          isKakaoInApp;

    // iOS detection
    const isIOSBrowser = ua.includes('iphone') || ua.includes('ipad') || ua.includes('ipod');

    // Opera (modern Chromium-based)
    const isOpera = (ua.includes('opr/') || ua.includes('opera')) && !isOperaMini;

    // Chrome
    const isChrome = ua.includes('chrome') &&
                    !isEdge &&
                    !isOpera &&
                    !isYandex &&
                    !isSamsungBrowser &&
                    !isVivaldi &&
                    !isArc &&
                    !isBrave &&
                    !isComet;

    // Firefox
    const isFirefox = ua.includes('firefox') && !ua.includes('seamonkey');

    // Safari (real Safari)
    const hasSafariUA = ua.includes('safari');
    const hasChrome = ua.includes('chrome') || ua.includes('crios');
    const hasVersion = ua.includes('version/');
    const isSafari = hasSafariUA && !hasChrome && hasVersion;

    // Chromium detection
    const isChromium = hasChrome ||
                      isEdge ||
                      isOpera ||
                      isYandex ||
                      isSamsungBrowser ||
                      isVivaldi ||
                      isArc ||
                      isBrave ||
                      isUCBrowser ||
                      isComet;

    // Engine detection
    const isWebKit = !isChromium && isSafari;
    const isBlink = isChromium;
    const isGecko = isFirefox;

    // Determine browser name
    let browserName = 'unknown';
    if (isFacebookInApp) browserName = 'Facebook In-App';
    else if (isInstagramInApp) browserName = 'Instagram In-App';
    else if (isTikTokInApp) browserName = 'TikTok In-App';
    else if (isSnapchatInApp) browserName = 'Snapchat In-App';
    else if (isWeChatInApp) browserName = 'WeChat In-App';
    else if (isThreadsInApp) browserName = 'Threads In-App';
    else if (isLinkedInInApp) browserName = 'LinkedIn In-App';
    else if (isTwitterInApp) browserName = 'Twitter In-App';
    else if (isPinterestInApp) browserName = 'Pinterest In-App';
    else if (isTelegramInApp) browserName = 'Telegram In-App';
    else if (isLineInApp) browserName = 'Line In-App';
    else if (isKakaoInApp) browserName = 'KakaoTalk In-App';
    else if (isComet) browserName = 'Comet';
    else if (isOperaMini) browserName = 'Opera Mini';
    else if (isIE) browserName = 'Internet Explorer';
    else if (isBrave) browserName = 'Brave';
    else if (isArc) browserName = 'Arc';
    else if (isVivaldi) browserName = 'Vivaldi';
    else if (isYandex) browserName = 'Yandex';
    else if (isSamsungBrowser) browserName = 'Samsung Internet';
    else if (isUCBrowser) browserName = 'UC Browser';
    else if (isEdge) browserName = 'Edge';
    else if (isOpera) browserName = 'Opera';
    else if (isChrome) browserName = 'Chrome';
    else if (isSafari) browserName = 'Safari';
    else if (isFirefox) browserName = 'Firefox';
    else if (isWebView) browserName = 'WebView';

    // Determine push notification support
    const browserBlocksPush = isOperaMini ||
                             isIE ||
                             isUCBrowser ||
                             isFacebookInApp ||
                             isInstagramInApp ||
                             isTikTokInApp ||
                             isSnapchatInApp ||
                             isWeChatInApp ||
                             isThreadsInApp ||
                             isPinterestInApp ||
                             isTelegramInApp ||
                             isLineInApp ||
                             isKakaoInApp ||
                             isWebView;

    const twitterLinkedInAndroid = (isTwitterInApp || isLinkedInInApp) && !isIOSBrowser;
    const supportsPushNotifications = !browserBlocksPush || twitterLinkedInAndroid;

    return {
      isChrome,
      isChromium,
      isSafari,
      isFirefox,
      isEdge,
      isOpera,
      isBrave,
      isArc,
      isVivaldi,
      isYandex,
      isSamsungBrowser,
      isUCBrowser,
      isComet,
      isOperaMini,
      isIE,
      isFacebookInApp,
      isInstagramInApp,
      isTikTokInApp,
      isSnapchatInApp,
      isWeChatInApp,
      isThreadsInApp,
      isLinkedInInApp,
      isTwitterInApp,
      isInAppBrowser,
      isWebView,
      browserName,
      isWebKit,
      isBlink,
      isGecko,
      supportsPushNotifications,
      isIOSBrowser,
      userAgent: window.navigator.userAgent,
    };
  }, []);
}
