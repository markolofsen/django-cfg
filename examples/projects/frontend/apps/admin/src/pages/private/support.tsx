import { SupportLayout } from "@djangocfg/layouts";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return <SupportLayout />;
};

View.pageConfig = {
  title: 'Support',
  description: 'Manage support, tickets, and issues',
};

export default View;

