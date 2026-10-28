"use client";

import { Loader2, XCircle } from "lucide-react";

interface ProgressBarProps {
  percent?: number | null;
  message?: string | null;
  status: string;
  onCancel?: () => void;
  isCancelling?: boolean;
}

export function ProgressBar({ percent, message, status, onCancel, isCancelling }: ProgressBarProps) {
  const isDeterminate = percent != null && percent >= 0;
  const clampedPercent = Math.min(100, Math.max(0, percent || 0));

  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-lg shadow-slate-200/50 dark:shadow-none space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Loader2 className="w-5 h-5 text-brand-600 animate-spin" />
          <span className="text-sm font-bold text-slate-900 dark:text-white capitalize">
            {status}...
          </span>
        </div>

        {isDeterminate && (
          <span className="text-sm font-mono font-bold text-brand-600 dark:text-brand-400">
            {Math.round(clampedPercent)}%
          </span>
        )}
      </div>

      {/* Bar container */}
      <div
        className="w-full h-3 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden relative"
        role="progressbar"
        aria-valuenow={isDeterminate ? Math.round(clampedPercent) : undefined}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        {isDeterminate ? (
          <div
            className="h-full bg-gradient-to-r from-brand-600 to-indigo-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${clampedPercent}%` }}
          />
        ) : (
          <div className="h-full w-1/3 bg-gradient-to-r from-brand-600 to-indigo-500 rounded-full animate-indeterminate" />
        )}
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <p className="text-slate-600 dark:text-slate-400">
          {message || "Processing media pipeline..."}
        </p>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isCancelling}
            className="flex items-center gap-1 text-rose-500 hover:text-rose-600 dark:text-rose-400 font-medium transition-colors"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>{isCancelling ? "Cancelling..." : "Cancel Download"}</span>
          </button>
        )}
      </div>
    </div>
  );
}

