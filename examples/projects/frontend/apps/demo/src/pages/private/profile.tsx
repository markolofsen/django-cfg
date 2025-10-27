import { ProfileLayout } from "@djangocfg/layouts";
import { PageWithConfig } from "@/types";

const View: PageWithConfig = () => {
  return (
    <ProfileLayout
      title="Profile"
      description="Manage your account settings and profile information"
    />
  );
};

View.pageConfig = {
  title: 'Profile',
};

export default View;