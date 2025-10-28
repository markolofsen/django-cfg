import { ProfileLayout } from "@djangocfg/layouts";
import { PageWithConfig } from "@/types";

const Page: PageWithConfig = () => {
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