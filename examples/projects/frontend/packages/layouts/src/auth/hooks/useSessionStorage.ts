import { useState } from 'react';

/**
 * Simple sessionStorage hook with better error handling
 * @param key - Storage key
 * @param initialValue - Default value if key doesn't exist
 * @returns [value, setValue, removeValue] - Current value, setter function, and remove function
 */
export function useSessionStorage<T>(key: string, initialValue: T) {
  // Get initial value from sessionStorage or use provided initialValue
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Check data size and limit
  const checkDataSize = (data: any): boolean => {
    try {
      const jsonString = JSON.stringify(data);
      const sizeInBytes = new Blob([jsonString]).size;
      const sizeInKB = sizeInBytes / 1024;
      
      // Limit to 1MB per item
      if (sizeInKB > 1024) {
        console.warn(`Data size (${sizeInKB.toFixed(2)}KB) exceeds 1MB limit for key "${key}"`);
        return false;
      }
      
      return true;
    } catch (error) {
      console.error(`Error checking data size for key "${key}":`, error);
      return false;
    }
  };

  // Clear old data when sessionStorage is full
  const clearOldData = () => {
    try {
      const keys = Object.keys(sessionStorage).filter(key => key && typeof key === 'string');
      // Remove oldest items if we have more than 50 items
      if (keys.length > 50) {
        const itemsToRemove = Math.ceil(keys.length * 0.2);
        for (let i = 0; i < itemsToRemove; i++) {
          try {
            const key = keys[i];
            if (key) {
              sessionStorage.removeItem(key);
              sessionStorage.removeItem(`${key}_timestamp`);
            }
          } catch {
            // Ignore errors when removing items
          }
        }
      }
    } catch (error) {
      console.error('Error clearing old sessionStorage data:', error);
    }
  };

  // Force clear all data if quota is exceeded
  const forceClearAll = () => {
    try {
      const keys = Object.keys(sessionStorage);
      for (const key of keys) {
        try {
          sessionStorage.removeItem(key);
        } catch {
          // Ignore errors when removing items
        }
      }
    } catch (error) {
      console.error('Error force clearing sessionStorage:', error);
    }
  };

  // Update sessionStorage when value changes
  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      
      // Check data size before attempting to save
      if (!checkDataSize(valueToStore)) {
        console.warn(`Data size too large for key "${key}", removing key`);
        // Remove the key if data is too large
        try {
          window.sessionStorage.removeItem(key);
          window.sessionStorage.removeItem(`${key}_timestamp`);
        } catch {
          // Ignore errors when removing
        }
        // Still update the state
        setStoredValue(valueToStore);
        return;
      }
      
      setStoredValue(valueToStore);

      if (typeof window !== 'undefined') {
        // Try to set the value
        try {
          window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
          // Add timestamp for cleanup
          window.sessionStorage.setItem(`${key}_timestamp`, Date.now().toString());
        } catch (storageError: any) {
          // If quota exceeded, clear old data and try again
          if (storageError.name === 'QuotaExceededError' || 
              storageError.code === 22 || 
              storageError.message?.includes('quota')) {
            console.warn('sessionStorage quota exceeded, clearing old data...');
            clearOldData();
            
            // Try again after clearing
            try {
              window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
              window.sessionStorage.setItem(`${key}_timestamp`, Date.now().toString());
            } catch (retryError) {
              console.error(`Failed to set sessionStorage key "${key}" after clearing old data:`, retryError);
              // If still fails, force clear all and try one more time
              try {
                forceClearAll();
                window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
                window.sessionStorage.setItem(`${key}_timestamp`, Date.now().toString());
              } catch (finalError) {
                console.error(`Failed to set sessionStorage key "${key}" after force clearing:`, finalError);
                // If still fails, just update the state without sessionStorage
                setStoredValue(valueToStore);
              }
            }
          } else {
            throw storageError;
          }
        }
      }
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
      // Still update the state even if sessionStorage fails
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
    }
  };

  // Remove value from sessionStorage
  const removeValue = () => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        try {
          window.sessionStorage.removeItem(key);
          window.sessionStorage.removeItem(`${key}_timestamp`);
        } catch (removeError: any) {
          // If removal fails due to quota, try to clear some data first
          if (removeError.name === 'QuotaExceededError' || 
              removeError.code === 22 || 
              removeError.message?.includes('quota')) {
            console.warn('sessionStorage quota exceeded during removal, clearing old data...');
            clearOldData();
            
            try {
              window.sessionStorage.removeItem(key);
              window.sessionStorage.removeItem(`${key}_timestamp`);
            } catch (retryError) {
              console.error(`Failed to remove sessionStorage key "${key}" after clearing:`, retryError);
              // If still fails, force clear all
              forceClearAll();
            }
          } else {
            throw removeError;
          }
        }
      }
    } catch (error) {
      console.error(`Error removing sessionStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue, removeValue] as const;
}
