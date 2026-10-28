"use client";

import { useState, useRef, useEffect } from "react";
import { UrlBar } from "@/components/UrlBar";
import { PlatformIcons } from "@/components/PlatformIcons";
import { ResultsCard } from "@/components/ResultsCard";
import { FormatSelector } from "@/components/FormatSelector";
import { ProgressBar } from "@/components/ProgressBar";
import { StatusBanner } from "@/components/StatusBanner";
import { AnalyzeResponse, UXState, DownloadJobResponse } from "@/types";
import { analyzeUrl, createDownloadJob, cancelJob, subscribeToJobEvents, ApiError } from "@/lib/api";
import { Shield, Sparkles, Check, DownloadCloud, Zap, Lock } from "lucide-react";

export default function HomePage() {
  const [uxState, setUxState] = useState<UXState>("idle");
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null);
  const [currentJob, setCurrentJob] = useState<DownloadJobResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastUrl, setLastUrl] = useState<string>("");
  const [isStartingDownload, setIsStartingDownload] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  const unsubscribeRef = useRef<(() => void) | null>(null);

  // Clean up SSE subscriptions on unmount
  useEffect(() => {
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
    };
  }, []);

  const handleAnalyze = async (url: string) => {
    setLastUrl(url);
    setErrorMessage(null);
    setUxState("analyzing");

    try {
      const data = await analyzeUrl(url);
      setAnalysisData(data);
      if (!data.formats || data.formats.length === 0) {
        setUxState("no_formats");
      } else {
        setUxState("complete");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to analyze URL. Please check the link and try again.");
      setUxState("failed");
    }
  };

  const handleStartDownload = async (formatId: string) => {
    if (!analysisData) return;
    setIsStartingDownload(true);
    setErrorMessage(null);

    try {
      const job = await createDownloadJob(analysisData.analysis_id, formatId);
      setCurrentJob(job);
      setUxState("downloading");
      setIsStartingDownload(false);

      // Subscribe to real-time Server-Sent Events
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }

      unsubscribeRef.current = subscribeToJobEvents(
        job.job_id,
        (progress) => {
          setCurrentJob((prev) =>
            prev
              ? {
                  ...prev,
                  status: progress.status as any,
                  percent: progress.percent,
                  message: progress.message,
                }
              : null
          );
        },
        (completed) => {
          setCurrentJob((prev) =>
            prev
              ? {
                  ...prev,
                  status: "completed",
                  percent: 100,
                  download_url: completed.download_url,
                  filename: completed.filename,
                  file_size: completed.file_size,
                  message: "Download complete!",
                }
              : null
          );
          setUxState("completed");

          // Automatically trigger browser download
          if (completed.download_url) {
            const a = document.createElement("a");
            a.href = completed.download_url;
            a.download = completed.filename || "media_download";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
          }
        },
        (errorMsg) => {
          setErrorMessage(errorMsg);
          setUxState("failed");
        }
      );
    } catch (err: any) {
      setIsStartingDownload(false);
      setErrorMessage(err.message || "Failed to initiate download job.");
      setUxState("failed");
    }
  };

  const handleCancel = async () => {
    if (!currentJob) return;
    setIsCancelling(true);
    try {
      await cancelJob(currentJob.job_id);
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
      }
      setUxState("cancelled");
    } catch {
      // Ignored
    } finally {
      setIsCancelling(false);
    }
  };

  const handleReset = () => {
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
    }
    setUxState("idle");
    setAnalysisData(null);
    setCurrentJob(null);
    setErrorMessage(null);
  };

  return (
    <div className="flex-1 flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full max-w-4xl mx-auto px-4 pt-10 sm:pt-16 pb-8 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-700 dark:text-brand-300 text-xs font-semibold shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-brand-500" />
          <span>Universal Social & Video Media Downloader</span>
        </div>

        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
          Analyze & Download Media in{" "}
          <span className="bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 bg-clip-text text-transparent">
            Original Quality
          </span>
        </h1>

        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Paste any public post, reel, story, video, or image link from YouTube, Instagram, TikTok, X, Reddit, Pinterest, or 6+ other networks. Inspect genuinely available resolutions and download safely.
        </p>

        {/* Central Search/Url Bar */}
        <div className="pt-2 max-w-2xl mx-auto">
          <UrlBar
            onAnalyze={handleAnalyze}
            isLoading={uxState === "analyzing"}
            initialUrl={lastUrl}
          />
        </div>
      </section>

      {/* Main Dynamic Workspace Area */}
      <section className="w-full max-w-4xl mx-auto px-4 pb-16 space-y-6">
        {/* State: Analyzing Loading Card */}
        {uxState === "analyzing" && (
          <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 text-center space-y-4 shadow-lg animate-in fade-in">
            <div className="w-12 h-12 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center mx-auto animate-pulse">
              <DownloadCloud className="w-6 h-6 animate-bounce" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Analyzing Media Stream...
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Verifying URL syntax, checking host allowlist, and extracting genuine available stream formats.
              </p>
            </div>
          </div>
        )}

        {/* State: Complete (Metadata Card + Format Selector) */}
        {(uxState === "complete" || uxState === "no_formats") && analysisData && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2">
            <ResultsCard
              metadata={analysisData.metadata}
              platform={analysisData.platform}
              contentType={analysisData.content_type}
              onReset={handleReset}
            />

            <FormatSelector
              formats={analysisData.formats}
              onStartDownload={handleStartDownload}
              isStartingDownload={isStartingDownload}
            />
          </div>
        )}

        {/* State: Downloading Active Progress */}
        {uxState === "downloading" && currentJob && (
          <div className="animate-in fade-in slide-in-from-bottom-2">
            <ProgressBar
              percent={currentJob.percent}
              message={currentJob.message}
              status={currentJob.status}
              onCancel={handleCancel}
              isCancelling={isCancelling}
            />
          </div>
        )}

        {/* State: Completed / Failed / Cancelled Banner */}
        {(uxState === "completed" || uxState === "failed" || uxState === "cancelled") && (
          <StatusBanner
            status={uxState}
            message={
              uxState === "failed"
                ? errorMessage
                : currentJob?.message || null
            }
            downloadUrl={currentJob?.download_url}
            filename={currentJob?.filename}
            fileSize={currentJob?.file_size}
            onRetry={lastUrl ? () => handleAnalyze(lastUrl) : undefined}
            onReset={handleReset}
          />
        )}

        {/* Platform Grid on Idle */}
        {uxState === "idle" && (
          <div className="pt-6 space-y-10 animate-in fade-in">
            <PlatformIcons onSelectExample={(url) => handleAnalyze(url)} />

            {/* Feature Highlights Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
                  <Zap className="w-4 h-4" />
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Truthful Formats
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  We query the platform directly and show only resolutions that actually exist—no upscaled or fabricated options.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
                  <Shield className="w-4 h-4" />
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Strict SSRF & Privacy
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  All links are validated against DNS rebinding and internal IP blocks. Temporary files expire automatically within 15 minutes.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm space-y-2">
                <div className="w-8 h-8 rounded-lg bg-cyan-50 dark:bg-cyan-950/60 text-cyan-600 dark:text-cyan-400 flex items-center justify-center">
                  <Lock className="w-4 h-4" />
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                  Lawful Media Only
                </h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  We respect access controls. We never collect passwords, bypass private accounts, or defeat DRM protections.
                </p>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

