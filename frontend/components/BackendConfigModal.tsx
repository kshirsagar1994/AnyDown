"use client";

import { useState, useEffect } from "react";
import { getApiBase, setApiBase } from "@/lib/api";
import { Server, Check, X, ExternalLink, RefreshCw } from "lucide-react";

interface BackendConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

export function BackendConfigModal({ isOpen, onClose, onSaved }: BackendConfigModalProps) {
  const [apiUrl, setApiUrl] = useState("");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [testingStatus, setTestingStatus] = useState<"idle" | "testing" | "ok" | "failed">("idle");
  const [testMessage, setTestMessage] = useState("");

  useEffect(() => {
    if (isOpen) {
      setApiUrl(getApiBase());
      setSavedSuccess(false);
      setTestingStatus("idle");
      setTestMessage("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    const clean = apiUrl.trim().replace(/\/+$/, "");
    setApiBase(clean);
    setSavedSuccess(true);
    setTimeout(() => {
      if (onSaved) onSaved();
      onClose();
    }, 800);
  };

  const handleTestConnection = async () => {
    const target = apiUrl.trim().replace(/\/+$/, "");
    if (!target) {
      setTestingStatus("failed");
      setTestMessage("Please enter a valid URL (e.g. https://anydown-backend.onrender.com)");
      return;
    }

    setTestingStatus("testing");
    setTestMessage("Testing connection to backend...");

    try {
      const res = await fetch(`${target}/api/v1/health`, { method: "GET" });
      if (res.ok) {
        const json = await res.json();
        if (json.status === "healthy") {
          setTestingStatus("ok");
          setTestMessage("Connected successfully! Backend is healthy and ready.");
        } else {
          setTestingStatus("failed");
          setTestMessage("Backend responded, but status was not healthy.");
        }
      } else {
        setTestingStatus("failed");
        setTestMessage(`Received HTTP ${res.status}. Verify the URL.`);
      }
    } catch {
      setTestingStatus("failed");
      setTestMessage("Cannot reach URL. If Render is asleep, it may take 45s to wake up. Check CORS and URL format.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-md p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Backend API Connection
              </h3>
              <p className="text-xs text-slate-500">Connect to your live Render backend</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 text-xs">
          <p className="text-slate-600 dark:text-slate-400">
            Enter your deployed backend service URL. If you deployed on Render, paste your Render web service URL below:
          </p>

          <div className="space-y-1">
            <label className="font-semibold text-slate-700 dark:text-slate-300">
              API Base URL
            </label>
            <input
              type="url"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="https://anydown-backend.onrender.com"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm font-mono"
            />
          </div>

          {testingStatus !== "idle" && (
            <div
              className={`p-2.5 rounded-xl text-xs font-medium flex items-start gap-2 ${
                testingStatus === "ok"
                  ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
                  : testingStatus === "testing"
                  ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800"
                  : "bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
              }`}
            >
              {testingStatus === "testing" && <RefreshCw className="w-4 h-4 animate-spin flex-shrink-0 mt-0.5" />}
              {testingStatus === "ok" && <Check className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />}
              {testingStatus === "failed" && <X className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />}
              <span>{testMessage}</span>
            </div>
          )}

          <div className="text-[11px] text-slate-500 pt-1">
            💡 <em>Tip: You can also edit <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono">config.js</code> in your shared hosting File Manager.</em>
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
          <button
            type="button"
            onClick={handleTestConnection}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Test Connection
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-500/20 transition-all"
            >
              {savedSuccess ? (
                <>
                  <Check className="w-3.5 h-3.5 text-white" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save & Apply</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
