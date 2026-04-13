"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Search, Bell, ChevronDown, LogOut, User } from "lucide-react";
import { useAuth } from "@/lib/auth";

interface HeaderProps {
  clientName?: string;
}

export function Header({ clientName }: HeaderProps) {
  const router = useRouter();
  const { logout, user } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="flex items-center justify-between h-[72px] px-6 border-b border-border bg-bg-primary/80 backdrop-blur-xl sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold tracking-tight">
          <span className="text-accent-lime">Craig</span>
          <span className="text-text-primary"> AI</span>
        </h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="hidden md:flex items-center gap-2 bg-bg-secondary border border-border rounded-full px-4 py-2 w-64">
          <Search className="w-4 h-4 text-text-tertiary" />
          <input
            type="text"
            placeholder="Start Search Here..."
            className="bg-transparent text-sm text-text-primary placeholder:text-text-tertiary outline-none w-full"
          />
        </div>

        {/* Notification Bell */}
        <button className="relative w-10 h-10 flex items-center justify-center rounded-full bg-bg-secondary border border-border text-text-secondary hover:text-text-primary hover:border-border-hover transition-all">
          <Bell className="w-4 h-4" />
          <span className="absolute top-2 right-2 w-2 h-2 bg-accent-lime rounded-full" />
        </button>

        {/* Avatar with dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 bg-bg-secondary border border-border rounded-full py-1 px-3 hover:border-border-hover transition-all"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center text-white text-xs font-bold">
              {user?.name?.[0] ?? "A"}
            </div>
            <span className="hidden sm:inline text-sm font-medium">{user?.name ?? "Admin"}</span>
            <ChevronDown className={`w-3.5 h-3.5 text-text-tertiary transition-transform ${dropdownOpen ? "rotate-180" : ""}`} />
          </button>

          {/* Dropdown */}
          {dropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-[#141414] border border-white/[0.08] rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.5)] overflow-hidden z-50">
              {/* User info */}
              <div className="px-4 py-3 border-b border-white/[0.06]">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-purple to-accent-pink flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                    {user?.name?.[0] ?? "A"}
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-bold text-text-primary truncate">{user?.name ?? "Admin"}</div>
                    <div className="text-[11px] text-text-tertiary truncate">{user?.email ?? ""}</div>
                  </div>
                </div>
              </div>

              {/* Menu items */}
              <div className="p-2">
                <button
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-text-secondary hover:text-text-primary hover:bg-white/[0.06] transition-all text-left"
                  onClick={() => setDropdownOpen(false)}
                >
                  <User className="w-4 h-4" />
                  Profile
                </button>
                <button
                  className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-danger hover:bg-danger/10 transition-all text-left mt-1"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4" />
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
