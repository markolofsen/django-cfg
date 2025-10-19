import { ProfileView } from "@/views";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return <ProfileView />;
};

View.pageConfig = {
  title: 'Profile',
};

export default View;