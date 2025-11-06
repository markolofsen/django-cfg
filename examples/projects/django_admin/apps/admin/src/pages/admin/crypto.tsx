/**
 * Cryptocurrency Page
 * Path: /admin/crypto
 */

import { PageWithConfig } from '@/types';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { CryptoView } from '@/views';
import { CryptoProvider } from "@/contexts";

const View: PageWithConfig = () => {
  return (
    <CryptoProvider>
      <CryptoView />
    </CryptoProvider>
  );
};

View.pageConfig = {
  title: 'Cryptocurrency',
  description: 'Manage cryptocurrency data and wallets',
};

View.getLayout = DashboardLayout;

export default View;
