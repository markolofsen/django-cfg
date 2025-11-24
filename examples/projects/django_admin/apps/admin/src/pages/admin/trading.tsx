/**
 * Trading Page
 * Path: /admin/trading
 */

import { PageWithLayout } from "@djangocfg/layouts";
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { TradingView } from '@/views';
import { TradingProvider } from "@/contexts";

const View: PageWithLayout = () => {
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
