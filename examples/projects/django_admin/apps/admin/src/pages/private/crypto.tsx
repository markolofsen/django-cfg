import { CryptoView } from "@/views";
import { PageWithConfig } from "@/types";
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
};

export default View;
