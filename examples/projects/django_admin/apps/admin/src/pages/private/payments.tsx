import { PaymentsLayout } from "@djangocfg/layouts";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return <PaymentsLayout />;
};

View.pageConfig = {
  title: 'Payments',
  description: 'Manage payments, balance, and billing',
};

export default View;

