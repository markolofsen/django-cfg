import { CryptoView } from "@/views";
import { PageWithConfig } from "@/types";
import { CryptoProvider } from "@/contexts";

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

export default Page;
