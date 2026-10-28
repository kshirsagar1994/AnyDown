"use client";

import { useEffect, useState } from "react";
import { getPlatforms } from "@/lib/api";
import { PlatformCapability } from "@/types";
import { Layers, ShieldCheck, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

export default function PlatformsPage() {
  const [platforms, setPlatforms] = useState<PlatformCapability[]>([]);
  const [disclaimer, setDisclaimer] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getPlatforms();
        setPlatforms(res.platforms);
        setDisclaimer(res.legal_disclaimer);
      } catch (e) {
        console.error("Failed to load platforms", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-12 sm:py-16 space-y-8">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 text-xs font-semibold border border-brand-200 dark:border-brand-800">
          <Layers className="w-3.5 h-3.5" />
          <span>Platform Capability Registry</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
          Verified Supported Platforms
        </h1>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-3xl leading-relaxed">
          In accordance with our product principles, AnyDown discloses only genuine capabilities. Features are enabled only for public, lawful content and are never advertised until verified.
        </p>
      </div>

      {disclaimer && (
        <div className="p-4 rounded-xl border border-indigo-200 dark:border-indigo-900 bg-indigo-50/50 dark:bg-indigo-950/20 flex items-start gap-3 text-xs sm:text-sm text-indigo-900 dark:text-indigo-200">
          <ShieldCheck className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
          <p>{disclaimer}</p>
        </div>
      )}

      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-brand-600" />
          <span className="text-sm">Loading verified platform capabilities...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {platforms.map((p) => (
            <div
              key={p.id}
              className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {p.name}
                </h3>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  <span>Adapter Active</span>
                </span>
              </div>

              <div className="space-y-1.5 text-xs">
                <div>
                  <span className="text-slate-400">Supported Formats:</span>{" "}
                  <span className="font-semibold text-slate-800 dark:text-slate-200 uppercase">
                    {p.supported_formats.join(", ")}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Content Scope:</span>{" "}
                  <span className="font-medium text-slate-700 dark:text-slate-300 capitalize">
                    {p.supported_content_types.join(", ")}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Allowed Domains:</span>{" "}
                  <span className="font-mono text-[11px] text-slate-600 dark:text-slate-400">
                    {p.hostname_patterns.slice(0, 3).join(", ")}
                    {p.hostname_patterns.length > 3 ? "..." : ""}
                  </span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 text-[11px] text-slate-500 dark:text-slate-400 border border-slate-100 dark:border-slate-800">
                <strong>Policy:</strong> {p.policy_notice}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

