import { LandingView } from "@/views";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return (
      <LandingView />
  );
};

View.pageConfig = {
  title: 'Django CFG Demo',
};

export default View;
