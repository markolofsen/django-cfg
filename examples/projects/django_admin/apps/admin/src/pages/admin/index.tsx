import { DashboardView } from "@/views";
import type { PageWithConfig } from "@/types";

const Page: PageWithConfig = () => {
  return <DashboardView />;
};

Page.pageConfig = {
  title: 'Dashboard',
};

export default Page;