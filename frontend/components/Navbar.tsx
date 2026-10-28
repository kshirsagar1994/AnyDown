"use client";

import { useState } from "react";
import Link from "next/link";
import { DownloadCloud, Layers, Scale, Server } from "lucide-react";
import { BackendConfigModal } from "@/components/BackendConfigModal";

export function Navbar() {
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/25 group-hover:scale-105 transition-transform">
              <DownloadCloud className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-slate-900 via-brand-700 to-indigo-600 dark:from-white dark:via-brand-300 dark:to-indigo-400 bg-clip-text text-transparent">
                AnyDown
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 border border-brand-200 dark:border-brand-800">
                v1.0 MVP
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-3 text-sm font-medium">
            <Link
              href="/"
              className="px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              Downloader
            </Link>
            <Link
              href="/platforms"
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Layers className="w-4 h-4 text-brand-600" />
              <span>Platforms</span>
            </Link>
            <Link
              href="/terms"
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Scale className="w-4 h-4 text-brand-600" />
              <span>Legal</span>
            </Link>

            {/* Backend Server Settings Button */}
            <button
              type="button"
              onClick={() => setIsConfigOpen(true)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors"
              title="Configure Backend API URL"
            >
              <Server className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
              <span className="hidden xs:inline sm:inline">Server</span>
            </button>
          </nav>
        </div>
      </header>

      <BackendConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
      />
    </>
  );
}
