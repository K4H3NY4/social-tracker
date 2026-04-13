"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useAuth } from "@/lib/auth";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const isLoginPage = pathname === "/login";

  useEffect(() => {
    if (!isAuthenticated && !isLoginPage) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoginPage, router]);

  // Login page — render without shell
  if (isLoginPage) {
    return <>{children}</>;
  }

  // Not authenticated yet — blank while redirecting
  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Sidebar />
      <div className="flex-1 lg:ml-[80px] flex flex-col min-h-screen">
        <Header />
        <main className="flex-1">{children}</main>
      </div>
    </>
  );
}
