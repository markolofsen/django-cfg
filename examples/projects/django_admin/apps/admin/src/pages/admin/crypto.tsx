import type { ReactElement } from 'react';
import { CryptoView } from "@/views";
import { PageWithConfig } from "@/types";
import { CryptoProvider } from "@/contexts";
import { AdminLayout } from '@/layouts/AdminLayout';

const Page: PageWithConfig = () => {
  return (
    <CryptoProvider>
      <CryptoView />
    </CryptoProvider>
  );
};

Page.pageConfig = {
  title: 'Cryptocurrency',
};

Page.getLayout = (page: ReactElement) => {
  return <AdminLayout>{page}</AdminLayout>;
};

export default Page;
