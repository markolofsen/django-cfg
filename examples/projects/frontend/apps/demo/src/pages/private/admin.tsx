import Head from "next/head";
import { AdminView } from "@/views";

export default function AdminPage() {
  return (
    <>
      <Head>
        <title>Django Admin - Django CFG Demo</title>
      </Head>
      <AdminView />
    </>
  );
}
