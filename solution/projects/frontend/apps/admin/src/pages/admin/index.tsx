/**
 * Dashboard Overview Page
 * Path: /admin/dashboard
 */

import { PageWithLayout } from "@djangocfg/layouts";
import { DashboardLayout } from '@/layouts/DashboardLayout';

const View: PageWithLayout = () => {
  return (
    <div>
      <h1>Dashboard Overview</h1>
    </div>
  )
};

View.pageConfig = {
  title: 'Dashboard Overview',
  description: 'System overview with stat cards and health',
};

View.getLayout = DashboardLayout;

export default View;
