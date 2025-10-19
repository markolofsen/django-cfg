import { UIGuideApp } from "@djangocfg/layouts";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return <UIGuideApp />;
};

View.pageConfig = {
  title: 'Component Showcase',
  description: 'Explore our comprehensive collection of React components',
};

export default View;

