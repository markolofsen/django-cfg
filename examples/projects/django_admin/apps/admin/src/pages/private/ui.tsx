import { UIGuideApp } from "@djangocfg/layouts";
import { PageWithLayout } from "@djangocfg/layouts";

const View: PageWithLayout = () => {
  return <UIGuideApp />;
};

View.pageConfig = {
  title: 'Component Showcase',
  description: 'Explore our comprehensive collection of React components',
};

export default View;

