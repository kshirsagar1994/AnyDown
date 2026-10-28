"use client";

import { useState, useEffect } from "react";
import { Search, Loader2, Clipboard, X, Sparkles, CheckCircle2 } from "lucide-react";
import { detectPlatformFromUrl, cn } from "@/lib/utils";

interface UrlBarProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
  initialUrl?: string;
}

export function UrlBar({ onAnalyze, isLoading, initialUrl = "" }: UrlBarProps) {
  const [url, setUrl] = useState(initialUrl);
  const [detected, setDetected] = useState(detectPlatformFromUrl(initialUrl));
  const [clipboardCopied, setClipboardCopied] = useState(false);

  useEffect(() => {
    setDetected(detectPlatformFromUrl(url));
  }, [url]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || isLoading) return;
    onAnalyze(url.trim());
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setUrl(text);
        setClipboardCopied(true);
        setTimeout(() => setClipboardCopied(false), 2000);
      }
    } catch {
      // Clipboard permissions not granted
    }
  };

  const handleClear = () => {
    setUrl("");
    setDetected(null);
  };

  const handleUseMock = () => {
    const mockUrl = "https://mock-media.anydown.local/sample-video";
    setUrl(mockUrl);
    onAnalyze(mockUrl);
  };

  return (
    <div className="w-full space-y-3">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="relative flex items-center shadow-xl rounded-2xl bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 focus-within:border-brand-500 dark:focus-within:border-brand-500 transition-all p-1.5 sm:p-2">
          {/* Leading Icon */}
          <div className="pl-3 pr-2 text-slate-400">
            <Search className="w-5 h-5" />
          </div>

          {/* Main Input Field */}
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste video, reel, story, post, or media URL here..."
            disabled={isLoading}
            className="w-full bg-transparent border-none focus:outline-none text-slate-900 dark:text-white placeholder-slate-400 text-sm sm:text-base py-2.5 px-1"
            required
          />

          {/* Detected Platform Tag */}
          {detected && (
            <div className="hidden sm:flex items-center gap-1 mr-2 px-2.5 py-1 rounded-lg border text-xs font-semibold animate-in fade-in"
                 style={{ backgroundColor: "rgba(99, 102, 241, 0.08)" }}>
              <span className={detected.color}>{detected.name}</span>
            </div>
          )}

          {/* Action Buttons inside Input */}
          <div className="flex items-center gap-1 pr-1">
            {url && !isLoading && (
              <button
                type="button"
                onClick={handleClear}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg transition-colors"
                title="Clear input"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {!url && (
              <button
                type="button"
                onClick={handlePaste}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
              >
                {clipboardCopied ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Pasted</span>
                  </>
                ) : (
                  <>
                    <Clipboard className="w-3.5 h-3.5" />
                    <span>Paste</span>
                  </>
                )}
              </button>
            )}

            <button
              type="submit"
              disabled={isLoading || !url.trim()}
              className="flex items-center justify-center gap-2 px-5 py-2.5 sm:py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-medium text-sm shadow-md shadow-brand-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.98]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Analyze</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Quick Test Links */}
      <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-slate-500">
        <span>Instant testing:</span>
        <button
          type="button"
          onClick={handleUseMock}
          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 transition-colors font-medium"
        >
          <Sparkles className="w-3 h-3 text-emerald-500" />
          <span>Load Mock Demo (1080p, 720p, MP3)</span>
        </button>
        <span className="text-slate-300 dark:text-slate-700">•</span>
        <button
          type="button"
          onClick={() => setUrl("https://www.youtube.com/watch?v=jNQXAC9IVRw")}
          className="hover:text-brand-600 dark:hover:text-brand-400 underline underline-offset-2 transition-colors"
        >
          YouTube First Video
        </button>
      </div>
    </div>
  );
}

