import { PageWithLayout } from "@djangocfg/layouts";
import PackagesView from "@/views/packages";

const View: PageWithLayout = () => {
  return <PackagesView />;
};

View.pageConfig = {
  title: 'Packages',
  description: 'Explore the @djangocfg monorepo ecosystem - UI, API, Realtime, and more',
};

export default View;
