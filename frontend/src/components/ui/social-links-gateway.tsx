"use client";

import { motion } from "framer-motion";
import { ExternalLink, Users } from "lucide-react";
import type { CSSProperties } from "react";
import { FacebookIcon, InstagramIcon, TikTokIcon } from "@/components/icons/social-icons";
import type { SocialLink } from "@/lib/mock-data";

const platformIcons: Record<string, React.ComponentType<{ className?: string; style?: CSSProperties }>> = {
  facebook: FacebookIcon,
  instagram: InstagramIcon,
  tiktok: TikTokIcon,
};

const platformColors: Record<string, string> = {
  facebook: "var(--color-facebook)",
  instagram: "var(--color-instagram)",
  tiktok: "var(--color-tiktok)",
};

const platformLabels: Record<string, string> = {
  facebook: "Facebook",
  instagram: "Instagram",
  tiktok: "TikTok",
};

interface SocialLinksGatewayProps {
  links: SocialLink[];
  clientName: string;
}

export function SocialLinksGateway({ links, clientName }: SocialLinksGatewayProps) {
  return (
    <div className="bg-bg-card rounded-xl border border-border p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider">
          Social Profiles
        </h3>
        <span className="text-xs text-text-muted">{clientName}</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {links.map((link, i) => {
          const Icon = platformIcons[link.platform] ?? FacebookIcon;
          const color = platformColors[link.platform] ?? "var(--color-accent)";
          return (
            <motion.a
              key={link.platform}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1, duration: 0.3 }}
              className="group flex items-center gap-3 bg-bg-elevated rounded-xl p-4 border border-transparent hover:border-border-hover transition-all duration-300 cursor-pointer"
              style={{
                // @ts-expect-error CSS variable
                "--hover-glow": color,
              }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-transform duration-300 group-hover:scale-110"
                style={{ backgroundColor: `color-mix(in srgb, ${color} 15%, transparent)` }}
              >
                <Icon className="w-5 h-5" style={{ color }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold" style={{ color }}>
                  {platformLabels[link.platform]}
                </p>
                <p className="text-xs text-text-secondary truncate">{link.handle}</p>
              </div>
              <div className="flex flex-col items-end gap-1 shrink-0">
                {link.followers && (
                  <span className="flex items-center gap-1 text-xs font-mono text-text-muted">
                    <Users className="w-3 h-3" />
                    {link.followers}
                  </span>
                )}
                <ExternalLink className="w-3.5 h-3.5 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </motion.a>
          );
        })}
      </div>
    </div>
  );
}
