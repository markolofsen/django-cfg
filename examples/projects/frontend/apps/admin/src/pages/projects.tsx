import { PageWithLayout } from "@djangocfg/layouts";
import { ProjectsView } from "@/views";

const View: PageWithLayout = () => {
  return <ProjectsView />;
};

View.pageConfig = {
  title: 'Production Projects',
  description: 'Real-world applications and platforms built with DjangoCFG',
};

export default View;
