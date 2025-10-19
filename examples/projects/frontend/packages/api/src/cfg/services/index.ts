/**
 * API Services
 *
 * Domain services with business logic and error handling
 */

// Base Client + API singleton
export { BaseClient, api } from '../BaseClient';

// Domain Services
export { AuthService } from './auth';
export { LeadsService } from './leads';
export { SupportService } from './support';
export { TasksService } from './tasks';
export { WebhooksService } from './webhooks';

// Payment Services
export {
  ApiKeysService,
  PaymentsService,
  SubscriptionsService,
  PaymentDashboardService,
} from './payments';

// Newsletter Services
export {
  NewsletterService,
  CampaignsService,
  NewslettersListService,
  BulkEmailService,
} from './newsletter';
