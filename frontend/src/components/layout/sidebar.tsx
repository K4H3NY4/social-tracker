"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Settings,
  Zap,
  BarChart3,
  CalendarDays,
} from "lucide-react";
import { motion } from "framer-motion";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/clients", label: "Clients", icon: Users },
  { href: "/schedule", label: "Schedule", icon: CalendarDays },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <>
      {/* Desktop Sidebar — frosted glass pill design */}
      <aside className="hidden lg:flex flex-col w-[80px] h-screen fixed left-0 top-0 z-50 bg-[#0a0a0a]/60 backdrop-blur-2xl border-r border-white/[0.04]">
        {/* Logo */}
        <div className="flex items-center justify-center h-[72px]">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-accent-lime to-accent-lime/60 flex items-center justify-center shadow-[0_0_20px_rgba(204,243,129,0.3)]">
            <Zap className="w-5 h-5 text-[#050505]" strokeWidth={2.5} />
          </div>
        </div>

        {/* Nav Items — centered with floating pill active indicator */}
        <nav className="flex-1 flex flex-col items-center gap-2 pt-6 px-3">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="group relative flex items-center justify-center w-[52px] h-[52px] rounded-2xl transition-all duration-300"
                title={item.label}
              >
                {/* Active pill background */}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-2xl bg-white/[0.08] border border-white/[0.06]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                {/* Neon left bar */}
                {isActive && (
                  <motion.span
                    layoutId="sidebar-bar"
                    className="absolute -left-3 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full bg-accent-lime shadow-[0_0_8px_rgba(204,243,129,0.6)]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon
                  className={`relative z-10 w-5 h-5 transition-colors duration-200 ${
                    isActive
                      ? "text-accent-lime"
                      : "text-text-tertiary group-hover:text-text-secondary"
                  }`}
                />
                {/* Tooltip */}
                <span className="absolute left-full ml-4 px-3 py-1.5 rounded-xl bg-[#1a1a1a] text-text-primary text-xs font-semibold whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none shadow-xl border border-white/[0.06]">
                  {item.label}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Bottom glow accent */}
        <div className="p-3 flex justify-center">
          <div className="w-8 h-1 rounded-full bg-white/[0.06]" />
        </div>
      </aside>

      {/* Mobile Bottom Nav — floating pill bar */}
      <nav className="lg:hidden fixed bottom-4 left-4 right-4 bg-[#0a0a0a]/80 backdrop-blur-2xl border border-white/[0.06] rounded-[28px] z-50 shadow-[0_8px_32px_rgba(0,0,0,0.6)]">
        <div className="flex items-center justify-around h-16 px-2">
          {navItems.slice(0, 4).map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="relative flex flex-col items-center gap-0.5 px-4 py-2 rounded-2xl transition-all"
              >
                {isActive && (
                  <motion.div
                    layoutId="mobile-active"
                    className="absolute inset-0 rounded-2xl bg-white/[0.08]"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon className={`relative z-10 w-5 h-5 transition-colors ${isActive ? "text-accent-lime" : "text-text-tertiary"}`} />
                <span className={`relative z-10 text-[10px] font-semibold transition-colors ${isActive ? "text-accent-lime" : "text-text-tertiary"}`}>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}
