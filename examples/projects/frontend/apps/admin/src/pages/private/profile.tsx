import { ProfileLayout } from "@djangocfg/layouts";
import { PageWithLayout } from "@djangocfg/layouts";

const Page: PageWithLayout = () => {
  return (
    <ProfileLayout
      title="Profile"
      description="Manage your account settings and profile information"
    />
  );
};

Page.pageConfig = {
  title: 'Profile',
};

export default Page;