import { PaymentsLayout } from "@djangocfg/layouts";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return <PaymentsLayout />;
};

View.pageConfig = {
  title: 'Payments',
  description: 'Manage payments, balance, and billing',
};

export default View;

