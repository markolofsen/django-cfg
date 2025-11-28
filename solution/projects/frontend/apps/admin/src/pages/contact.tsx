/**
 * Contact Page
 * Path: /contact
 */

import { PageWithLayout } from '@djangocfg/layouts';
import { ContactView } from '@/views/contact';

const Page: PageWithLayout = () => {
  return <ContactView />;
};

Page.pageConfig = {
  title: 'Contact Us',
  description: 'Get in touch with us',
};

export default Page;
