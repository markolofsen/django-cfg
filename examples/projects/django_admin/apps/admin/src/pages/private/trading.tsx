import { TradingView } from "@/views";
import { PageWithConfig } from "@/types";
import { TradingProvider } from "@/contexts";

const View: PageWithConfig = () => {
  return (
    <TradingProvider>
      <TradingView />
    </TradingProvider>
  );
};

View.pageConfig = {
  title: 'Trading Portfolio',
};

export default View;
