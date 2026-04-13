"use client";

import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import type { ReactNode } from "react";
import {
  FacebookIcon,
  InstagramIcon,
  TikTokIcon,
} from "@/components/icons/social-icons";

interface PlatformCardProps {
  platform: "facebook" | "instagram" | "tiktok";
  score: number;
  stats: { label: string; value: string | number }[];
  username?: string | null;
  children?: ReactNode;
}

const platformConfig = {
  facebook: {
    name: "Facebook",
    Icon: FacebookIcon,
    color: "var(--color-facebook)",
    urlPrefix: "https://facebook.com/",
  },
  instagram: {
    name: "Instagram",
    Icon: InstagramIcon,
    color: "var(--color-instagram)",
    urlPrefix: "https://instagram.com/",
  },
  tiktok: {
    name: "TikTok",
    Icon: TikTokIcon,
    color: "var(--color-tiktok)",
    urlPrefix: "https://tiktok.com/@",
  },
};

export function PlatformCard({ platform, score, stats, username, children }: PlatformCardProps) {
  const config = platformConfig[platform];
  const profileUrl = username ? `${config.urlPrefix}${username}` : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-gradient-to-b from-[#1a1a1a] to-[#121212] rounded-[32px] border border-border overflow-hidden hover:border-border-hover hover:-translate-y-0.5 transition-all duration-300"
    >
      <div className="h-1 w-full" style={{ background: config.color }} />

      <div className="p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center"
              style={{ background: `${config.color}15` }}
            >
              <config.Icon className="w-5 h-5" />
            </div>
            <span className="text-sm font-bold">{config.name}</span>
          </div>

          <div className="flex items-center gap-2">
            <div
              className="px-3 py-1.5 rounded-full text-xs font-bold"
              style={{
                background: `${config.color}15`,
                color: config.color,
              }}
            >
              {score}%
            </div>
            {profileUrl && (
              <a
                href={profileUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 rounded-full flex items-center justify-center text-text-tertiary hover:text-text-primary hover:bg-white/5 transition-all"
                title={`Visit ${config.name} profile`}
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </div>
        </div>

        {/* Score Progress Bar */}
        <div className="mb-5">
          <div className="h-2 rounded-full bg-[#0a0a0a] overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: config.color }}
              initial={{ width: 0 }}
              animate={{ width: `${score}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="bg-[#0a0a0a] rounded-2xl p-3 text-center"
            >
              <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold">{stat.value}</div>
              <div className="text-[9px] font-semibold uppercase tracking-wider text-text-tertiary mt-0.5">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {children}
      </div>
    </motion.div>
  );
}
