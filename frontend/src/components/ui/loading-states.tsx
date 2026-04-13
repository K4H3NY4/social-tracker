"use client";

import { Loader2 } from "lucide-react";

export function LoadingState() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-2 border-border" />
          <Loader2 className="w-12 h-12 text-accent-lime animate-spin absolute inset-0" />
        </div>
        <span className="text-sm text-text-tertiary font-medium">
          Analyzing compliance...
        </span>
      </div>
    </div>
  );
}

export function EmptyState() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="flex flex-col items-center gap-3 text-center">
        <div className="w-16 h-16 rounded-[24px] bg-gradient-to-b from-[#1a1a1a] to-[#121212] border border-border flex items-center justify-center text-3xl">
          📊
        </div>
        <h3 className="font-[family-name:var(--font-space-grotesk)] text-base font-bold text-text-primary">No Data Available</h3>
        <p className="text-sm text-text-tertiary max-w-xs">
          Select a client and date range to view compliance data
        </p>
      </div>
    </div>
  );
}
