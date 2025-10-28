import { LandingView } from "@/views";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return (
      <LandingView />
  );
};

View.pageConfig = {
  title: 'Django CFG Demo',
};

export default View;
