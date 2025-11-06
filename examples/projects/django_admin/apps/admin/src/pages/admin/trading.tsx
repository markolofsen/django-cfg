/**
 * Trading Page
 * Path: /admin/trading
 */

import { PageWithConfig } from '@/types';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { TradingView } from '@/views';
import { TradingProvider } from "@/contexts";

const View: PageWithConfig = () => {
  return (
    <TradingProvider>
      <TradingView />
    </TradingProvider>
  );
};

View.pageConfig = {
  title: 'Trading',
  description: 'Manage trading portfolio and orders',
};

View.getLayout = DashboardLayout;

export default View;
