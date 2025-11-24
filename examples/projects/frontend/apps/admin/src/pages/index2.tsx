import { PageWithLayout } from "@djangocfg/layouts";
import { useAuth } from '@djangocfg/layouts'
import { redirectToAuth } from "@/core/routes";
import { useEffect } from "react";
import { routes } from "@/core/routes";
import { useRouter } from "next/router";
import { Loader2 } from "lucide-react";
import { isDevelopment } from "@/core/settings";

const Page: PageWithLayout = () => {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // if (!isAuthenticated && !isDevelopment) {
    if (!isAuthenticated) {
      router.push(redirectToAuth());
    } else {
      router.push(routes.admin.overview.path);
    }
  }, [isAuthenticated, router.asPath]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="animate-spin text-primary" style={{ width: '48px', height: '48px' }} />
        <span className="text-lg font-medium text-muted-foreground">
          Loading...
        </span>
      </div>
    </div>
  );
};

Page.pageConfig = {
  title: 'Portal',
};

export default Page;
