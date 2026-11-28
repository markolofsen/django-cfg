'use client';

export {
  useActiveTab,
  useIsTabActive,
  useIsTabLeader,
  type UseActiveTabReturn,
} from './useActiveTab';

export {
  useActiveTabStore,
  ensureActiveTabCoordinator,
  disposeActiveTabCoordinator,
  type ActiveTabMessage,
} from './activeTabStore';

export { getTabId } from './tabId';
