"use client";

import { Zap, ExternalLink, ShieldCheck } from "lucide-react";

export const ADSTERRA_SMARTLINK = "https://ardance.org/4/945a8cce411b1587d855795338599345";

export function SmartlinkButton({
  label = "High-Speed Direct Download (Fast Server)",
  className = "",
}: {
  label?: string;
  className?: string;
}) {
  return (
    <a
      href={ADSTERRA_SMARTLINK}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-white font-semibold text-xs sm:text-sm shadow-md shadow-orange-500/25 transition-all active:scale-[0.98] ${className}`}
    >
      <Zap className="w-4 h-4 fill-white text-white" />
      <span>{label}</span>
      <ExternalLink className="w-3.5 h-3.5 opacity-80" />
    </a>
  );
}

export function SmartlinkBanner() {
  return (
    <div className="w-full my-4 p-3 rounded-xl bg-gradient-to-r from-brand-50 via-indigo-50 to-orange-50 dark:from-slate-900 dark:via-indigo-950/30 dark:to-orange-950/20 border border-brand-200/60 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
        <span className="px-2 py-0.5 rounded font-bold uppercase text-[10px] bg-orange-500 text-white">
          Sponsored
        </span>
        <span className="font-medium">
          Looking for unlimited high-bandwidth downloads? Try our recommended partner server.
        </span>
      </div>
      <a
        href={ADSTERRA_SMARTLINK}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-shrink-0 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold hover:opacity-90 transition-opacity"
      >
        <span>Access Server</span>
        <ExternalLink className="w-3 h-3" />
      </a>
    </div>
  );
}
