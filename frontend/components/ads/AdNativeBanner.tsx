"use client";

import { useEffect, useRef } from "react";

export function AdNativeBanner() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Check if script already appended to prevent duplicates
    const scriptId = "adsterra-native-banner-script";
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.async = true;
      script.setAttribute("data-cfasync", "false");
      script.src = "https://bellnewyork.org/21/793c0b65bb7a09a035194e02bf98a7f4";
      document.body.appendChild(script);
    }
  }, []);

  return (
    <div className="w-full my-6 p-4 rounded-2xl bg-white/70 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-sm text-center">
      <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500 mb-2">
        Recommended For You
      </div>
      <div ref={containerRef} className="w-full min-h-[90px] flex items-center justify-center">
        <div id="container-793c0b65bb7a09a035194e02bf98a7f4" />
      </div>
    </div>
  );
}

