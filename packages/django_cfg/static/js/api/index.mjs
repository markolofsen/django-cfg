/**
 * Django CFG API Clients
 * Lightweight ES Modules with JSDoc type annotations
 * Organized by Django apps
 *
 * @module django-cfg-api
 *
 * @example
 * // Import specific app API
 * import { tasksAPI } from '/static/api/tasks/index.mjs';
 * const stats = await tasksAPI.cfgTasksApiTasksStatsRetrieve();
 *
 * @example
 * // Import multiple APIs from main index
 * import { tasksAPI, paymentsAPI } from '/static/api/index.mjs';
 *
 * @example
 * // Import with custom base URL
 * import { TasksAPI } from '/static/api/tasks/index.mjs';
 * const api = new TasksAPI('https://api.example.com');
 */

import { BaseAPIClient } from './base.mjs';
import { AccountsAPI, accountsAPI } from './accounts/index.mjs';
import { CentrifugoAPI, centrifugoAPI } from './centrifugo/index.mjs';
import { KnowbaseAPI, knowbaseAPI } from './knowbase/index.mjs';
import { LeadsAPI, leadsAPI } from './leads/index.mjs';
import { NewsletterAPI, newsletterAPI } from './newsletter/index.mjs';
import { PaymentsAPI, paymentsAPI } from './payments/index.mjs';
import { SupportAPI, supportAPI } from './support/index.mjs';
import { TasksAPI, tasksAPI } from './tasks/index.mjs';

/**
 * Export all API classes for custom instantiation
 * @exports
 */
export {
    BaseAPIClient,
    AccountsAPI,
    CentrifugoAPI,
    KnowbaseAPI,
    LeadsAPI,
    NewsletterAPI,
    PaymentsAPI,
    SupportAPI,
    TasksAPI,
};

/**
 * Export all default instances for convenience
 * These instances use the current origin as base URL
 * @exports
 */
export {
    accountsAPI,
    centrifugoAPI,
    knowbaseAPI,
    leadsAPI,
    newsletterAPI,
    paymentsAPI,
    supportAPI,
    tasksAPI,
};

/**
 * Grouped exports by functionality
 * Access APIs by app name: apis.tasks, apis.payments, etc.
 * @type {Object.<string, BaseAPIClient>}
 */
export const apis = {
    accounts: accountsAPI,
    centrifugo: centrifugoAPI,
    knowbase: knowbaseAPI,
    leads: leadsAPI,
    newsletter: newsletterAPI,
    payments: paymentsAPI,
    support: supportAPI,
    tasks: tasksAPI,
};

/**
 * Helper function to get API by app name
 * @param {string} appName - Name of the Django app
 * @returns {BaseAPIClient|undefined} API instance for the app
 * @example
 * const tasksAPI = getAPI('tasks');
 */
export function getAPI(appName) {
    return apis[appName];
}

/**
 * List of all available apps
 * @type {string[]}
 */
export const availableApps = [
    'accounts',
    'centrifugo',
    'knowbase',
    'leads',
    'newsletter',
    'payments',
    'support',
    'tasks',
];