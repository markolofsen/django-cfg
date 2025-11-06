import Head from "next/head";
import { DashboardView } from "@/views";

export default function DashboardPage() {
  return (
    <>
      <Head>
        <title>Dashboard - Django CFG Demo</title>
      </Head>
      <DashboardView />
    </>
  );
}