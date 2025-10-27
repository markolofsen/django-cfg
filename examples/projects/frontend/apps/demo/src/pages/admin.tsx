import { AdminView } from "@/views";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return (
      <AdminView />
  );
};

View.pageConfig = {
  title: 'Django Admin - Django CFG Demo',
};

export default View;
