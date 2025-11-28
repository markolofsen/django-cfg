import { DashboardView } from "@/views";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return (
      <DashboardView />
  );
};

View.pageConfig = {
  title: 'Django Admin - Django CFG Demo',
};

export default View;
