import Head from "next/head";
import { PageWithLayout } from "@djangocfg/layouts";

const Page: PageWithLayout = () => {
  return (
    <div>
      <h1>Private Dashboard</h1>
    </div>
  );
};

Page.pageConfig = {
  title: 'Dashboard',
};

export default Page;