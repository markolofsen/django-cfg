/**
 * Centrifugo Monitor Page
 *
 * Real-time monitoring and management interface for Centrifugo
 */

import { CentrifugoView } from "@/views/centrifugo";
import { PageWithConfig } from "@/types/pageConfig";

const CentrifugoPage: PageWithConfig = () => {
  return <CentrifugoView />;
};

CentrifugoPage.pageConfig = {
  title: 'Centrifugo Monitor',
  description: 'Real-time monitoring and management interface for Centrifugo',
  protected: true,
};

export default CentrifugoPage;
