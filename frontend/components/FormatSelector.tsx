"use client";

import { useState } from "react";
import { MediaFormat, MediaType } from "@/types";
import { formatBytes } from "@/lib/utils";
import { Film, Music, Image as ImageIcon, Download, CheckCircle2, AlertCircle } from "lucide-react";

interface FormatSelectorProps {
  formats: MediaFormat[];
  onStartDownload: (formatId: string) => void;
  isStartingDownload: boolean;
}

export function FormatSelector({ formats, onStartDownload, isStartingDownload }: FormatSelectorProps) {
  const [selectedType, setSelectedType] = useState<MediaType>("video");
  const [selectedFormatId, setSelectedFormatId] = useState<string>(
    formats[0]?.format_id || ""
  );

  const videoFormats = formats.filter((f) => f.media_type === "video");
  const audioFormats = formats.filter((f) => f.media_type === "audio");
  const imageFormats = formats.filter((f) => f.media_type === "image");

  // Determine active tab
  const currentFormats =
    selectedType === "video"
      ? videoFormats
      : selectedType === "audio"
      ? audioFormats
      : imageFormats;

  // If active tab has no formats, auto-switch to first available tab
  if (currentFormats.length === 0 && formats.length > 0) {
    if (videoFormats.length > 0) setSelectedType("video");
    else if (audioFormats.length > 0) setSelectedType("audio");
    else if (imageFormats.length > 0) setSelectedType("image");
  }

  if (formats.length === 0) {
    return (
      <div className="w-full p-8 border border-dashed border-amber-300 dark:border-amber-700 bg-amber-50/50 dark:bg-amber-950/20 rounded-2xl text-center space-y-2">
        <AlertCircle className="w-8 h-8 text-amber-500 mx-auto" />
        <h3 className="text-base font-semibold text-amber-900 dark:text-amber-200">
          No Downloadable Formats Available
        </h3>
        <p className="text-xs text-amber-700 dark:text-amber-300 max-w-md mx-auto">
          The platform verified this media, but no public streams are available or permitted for lawful download.
        </p>
      </div>
    );
  }

  const handleDownloadClick = () => {
    if (!selectedFormatId) return;
    onStartDownload(selectedFormatId);
  };

  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-6 shadow-lg shadow-slate-200/50 dark:shadow-none space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white">
            Available Media Formats
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Select your preferred resolution or audio format (strictly verified available streams).
          </p>
        </div>

        {/* Media Type Tabs */}
        <div className="flex items-center gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          {videoFormats.length > 0 && (
            <button
              type="button"
              onClick={() => {
                setSelectedType("video");
                setSelectedFormatId(videoFormats[0]?.format_id || "");
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedType === "video"
                  ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <Film className="w-3.5 h-3.5" />
              <span>Video ({videoFormats.length})</span>
            </button>
          )}

          {audioFormats.length > 0 && (
            <button
              type="button"
              onClick={() => {
                setSelectedType("audio");
                setSelectedFormatId(audioFormats[0]?.format_id || "");
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedType === "audio"
                  ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <Music className="w-3.5 h-3.5" />
              <span>Audio ({audioFormats.length})</span>
            </button>
          )}

          {imageFormats.length > 0 && (
            <button
              type="button"
              onClick={() => {
                setSelectedType("image");
                setSelectedFormatId(imageFormats[0]?.format_id || "");
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedType === "image"
                  ? "bg-white dark:bg-slate-900 text-brand-600 dark:text-brand-400 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>Images ({imageFormats.length})</span>
            </button>
          )}
        </div>
      </div>

      {/* Format Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {currentFormats.map((f) => {
          const isSelected = selectedFormatId === f.format_id;
          return (
            <button
              key={f.format_id}
              type="button"
              onClick={() => setSelectedFormatId(f.format_id)}
              className={`relative flex flex-col p-3.5 rounded-xl border-2 text-left transition-all ${
                isSelected
                  ? "border-brand-600 dark:border-brand-500 bg-brand-50/50 dark:bg-brand-950/30 shadow-md shadow-brand-500/10"
                  : "border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-800/40"
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="text-sm font-bold text-slate-900 dark:text-white">
                  {f.quality_label}
                </span>
                <span className="text-xs px-2 py-0.5 rounded uppercase font-mono font-semibold bg-slate-200/70 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  .{f.container}
                </span>
              </div>

              <div className="text-xs text-slate-500 dark:text-slate-400 space-y-0.5">
                {f.width && f.height && (
                  <div>Resolution: {f.width}×{f.height}</div>
                )}
                <div>Size: {formatBytes(f.estimated_size_bytes)}</div>
                {f.note && <div className="text-[11px] text-brand-600 dark:text-brand-400">{f.note}</div>}
              </div>

              {isSelected && (
                <div className="absolute bottom-2.5 right-2.5 text-brand-600 dark:text-brand-400">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Primary Action Button */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-100 dark:border-slate-800/80">
        <div className="text-xs text-slate-500 dark:text-slate-400">
          Selected: <strong className="text-slate-900 dark:text-white">
            {formats.find((f) => f.format_id === selectedFormatId)?.quality_label || "None"}
          </strong>
        </div>

        <button
          type="button"
          onClick={handleDownloadClick}
          disabled={!selectedFormatId || isStartingDownload}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.98]"
        >
          <Download className="w-4 h-4" />
          <span>{isStartingDownload ? "Preparing Job..." : "Download File"}</span>
        </button>
      </div>
    </div>
  );
}

