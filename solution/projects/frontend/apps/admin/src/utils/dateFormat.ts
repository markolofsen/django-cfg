/**
 * Date formatting utilities using moment UTC
 */

import moment from 'moment';

/**
 * Format date to UTC datetime string
 * @param date - Date string or Date object
 * @returns Formatted string like "2025-01-03 15:30:45 UTC"
 */
export const formatDateTime = (date: string | Date | null | undefined): string => {
  if (!date) return 'N/A';
  return moment.utc(date).format('YYYY-MM-DD HH:mm:ss [UTC]');
};

/**
 * Format date to UTC date only
 * @param date - Date string or Date object
 * @returns Formatted string like "2025-01-03"
 */
export const formatDate = (date: string | Date | null | undefined): string => {
  if (!date) return 'N/A';
  return moment.utc(date).format('YYYY-MM-DD');
};

/**
 * Format date to time only (HH:mm)
 * @param date - Date string or Date object
 * @returns Formatted string like "15:30"
 */
export const formatTime = (date: string | Date | null | undefined): string => {
  if (!date) return 'N/A';
  return moment.utc(date).format('HH:mm');
};

/**
 * Check if a timestamp is within the last N milliseconds
 * @param timestamp - Timestamp to check
 * @param milliseconds - Time window in milliseconds
 * @returns true if timestamp is within the window
 */
export const isWithinLast = (timestamp: string | Date | null | undefined, milliseconds: number): boolean => {
  if (!timestamp) return false;
  return moment.utc().diff(moment.utc(timestamp), 'milliseconds') < milliseconds;
};

/**
 * Check if service/resource is online (active within last 30 minutes)
 * @param lastActivityAt - Last activity timestamp
 * @returns true if online
 */
export const isOnline = (lastActivityAt: string | Date | null | undefined): boolean => {
  // Changed from 5 to 30 minutes for better UX
  // Services may not have activity every 5 minutes but still be healthy/running
  return isWithinLast(lastActivityAt, 30 * 60 * 1000);
};
