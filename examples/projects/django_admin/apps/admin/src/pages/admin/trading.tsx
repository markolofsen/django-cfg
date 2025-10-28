import { TradingView } from "@/views";
import { PageWithConfig } from "@/types";
import { TradingProvider } from "@/contexts";

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

export default Page;
