import { AdminView } from "@/views";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return (
      <AdminView />
  );
};

View.pageConfig = {
  title: 'Django Admin - Django CFG Demo',
};

export default View;
