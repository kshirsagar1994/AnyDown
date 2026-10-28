"use client";

import { CheckCircle2, AlertTriangle, XCircle, Download, RotateCcw } from "lucide-react";
import { formatBytes } from "@/lib/utils";

interface StatusBannerProps {
  status: "completed" | "failed" | "cancelled";
  message?: string | null;
  downloadUrl?: string | null;
  filename?: string | null;
  fileSize?: number | null;
  onRetry?: () => void;
  onReset: () => void;
}

export function StatusBanner({
  status,
  message,
  downloadUrl,
  filename,
  fileSize,
  onRetry,
  onReset,
}: StatusBannerProps) {
  if (status === "completed") {
    return (
      <div className="w-full bg-emerald-50/80 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-2xl p-6 shadow-xl shadow-emerald-500/5 text-center space-y-4 animate-in fade-in zoom-in-95">
        <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-7 h-7" />
        </div>

        <div className="space-y-1">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            Download Ready!
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {message || "Media processing and container validation completed successfully."}
          </p>
          {filename && (
            <div className="inline-block mt-2 px-3 py-1 rounded-lg bg-emerald-100/70 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 font-mono text-xs font-semibold">
              {filename} ({formatBytes(fileSize)})
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          {downloadUrl && (
            <a
              href={downloadUrl}
              download={filename || "media_download"}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm shadow-md shadow-emerald-600/25 transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Save File to Device</span>
            </a>
          )}

          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-sm transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Analyze Another Link</span>
          </button>
        </div>
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div className="w-full bg-rose-50/80 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800 rounded-2xl p-6 shadow-xl shadow-rose-500/5 text-center space-y-4 animate-in fade-in">
        <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-900/60 text-rose-600 dark:text-rose-400 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-7 h-7" />
        </div>

        <div className="space-y-1">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            Processing Unsuccessful
          </h3>
          <p className="text-sm text-rose-700 dark:text-rose-300 max-w-md mx-auto">
            {message || "We encountered an issue analyzing or downloading media from this link."}
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 pt-1">
            Ensure the content is public, not protected by login/DRM access controls, and that the link is valid.
          </p>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm shadow-md shadow-rose-600/25 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retry</span>
            </button>
          )}

          <button
            type="button"
            onClick={onReset}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-sm transition-all"
          >
            <span>Try Another Link</span>
          </button>
        </div>
      </div>
    );
  }

  // Cancelled State
  return (
    <div className="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-2xl p-6 text-center space-y-4 animate-in fade-in">
      <div className="w-12 h-12 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center mx-auto">
        <XCircle className="w-7 h-7" />
      </div>

      <div className="space-y-1">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">
          Download Cancelled
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          The download operation was cancelled as requested.
        </p>
      </div>

      <div className="pt-2">
        <button
          type="button"
          onClick={onReset}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm transition-all"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Start Over</span>
        </button>
      </div>
    </div>
  );
}

