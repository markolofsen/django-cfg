import { SupportLayout } from "@djangocfg/layouts";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return <SupportLayout />;
};

View.pageConfig = {
  title: 'Support',
  description: 'Manage support, tickets, and issues',
};

export default View;

