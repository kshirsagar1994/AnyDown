"use client";

import { MediaMetadata } from "@/types";
import { formatDuration, detectPlatformFromUrl } from "@/lib/utils";
import { Clock, User, ExternalLink, PlaySquare, Image as ImageIcon } from "lucide-react";

interface ResultsCardProps {
  metadata: MediaMetadata;
  platform: string;
  contentType: string;
  onReset: () => void;
}

export function ResultsCard({ metadata, platform, contentType, onReset }: ResultsCardProps) {
  const platformInfo = detectPlatformFromUrl(metadata.source_url);

  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-6 shadow-lg shadow-slate-200/50 dark:shadow-none transition-all">
      <div className="flex flex-col sm:flex-row gap-5 items-start">
        {/* Media Thumbnail */}
        <div className="relative w-full sm:w-56 h-36 rounded-xl overflow-hidden bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex-shrink-0 group">
          {metadata.thumbnail_url ? (
            <img
              src={metadata.thumbnail_url}
              alt={metadata.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => {
                // If thumbnail fails to load, replace with clean placeholder
                (e.target as HTMLElement).style.display = "none";
              }}
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-slate-400 gap-2">
              {contentType === "video" ? (
                <PlaySquare className="w-8 h-8" />
              ) : (
                <ImageIcon className="w-8 h-8" />
              )}
              <span className="text-xs">Media Preview</span>
            </div>
          )}

          {metadata.duration_seconds && metadata.duration_seconds > 0 && (
            <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/75 backdrop-blur-sm text-white text-xs font-mono font-medium">
              {formatDuration(metadata.duration_seconds)}
            </div>
          )}
        </div>

        {/* Media Details */}
        <div className="flex-1 min-w-0 space-y-2 w-full">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 border border-brand-200 dark:border-brand-800 uppercase tracking-wide">
              {platformInfo ? platformInfo.name : platform}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-medium">
              {contentType}
            </span>
          </div>

          <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white line-clamp-2 leading-snug">
            {metadata.title}
          </h2>

          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400 pt-1">
            {metadata.creator && (
              <div className="flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" />
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  {metadata.creator}
                </span>
              </div>
            )}
            {metadata.duration_seconds && metadata.duration_seconds > 0 && (
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                <span>{formatDuration(metadata.duration_seconds)} duration</span>
              </div>
            )}
            <a
              href={metadata.source_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 text-brand-600 dark:text-brand-400 hover:underline"
            >
              <span>Source URL</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="pt-2">
            <button
              type="button"
              onClick={onReset}
              className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 underline underline-offset-2"
            >
              Analyze a different link
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

