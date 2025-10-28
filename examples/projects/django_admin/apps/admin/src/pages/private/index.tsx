import Head from "next/head";
import { DashboardView } from "@/views";
import { AccountsProvider } from "@djangocfg/api/cfg/contexts";

export default function DashboardPage() {
  return (
    <>
      <Head>
        <title>Dashboard - Django CFG Demo</title>
      </Head>
      <AccountsProvider>
        <DashboardView />
      </AccountsProvider>
    </>
  );
}