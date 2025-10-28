import type { ReactElement } from 'react';
import { TradingView } from "@/views";
import { PageWithConfig } from "@/types";
import { TradingProvider } from "@/contexts";
import { AdminLayout } from '@/layouts/AdminLayout';

const Page: PageWithConfig = () => {
  return (
    <TradingProvider>
      <TradingView />
    </TradingProvider>
  );
};

Page.pageConfig = {
  title: 'Trading Portfolio',
};

Page.getLayout = (page: ReactElement) => {
  return <AdminLayout>{page}</AdminLayout>;
};

export default Page;
