"use client";

import { cn } from "@/lib/utils";

interface Platform {
  id: string;
  name: string;
  exampleUrl: string;
  badge: string;
  color: string;
}

const PLATFORMS: Platform[] = [
  { id: "youtube", name: "YouTube", exampleUrl: "https://www.youtube.com/watch?v=dQw4w9WgXcQ", badge: "Videos, Audio (MP3)", color: "hover:border-red-500 hover:text-red-500" },
  { id: "instagram", name: "Instagram", exampleUrl: "https://www.instagram.com/reel/example", badge: "Reels & Posts", color: "hover:border-pink-500 hover:text-pink-500" },
  { id: "tiktok", name: "TikTok", exampleUrl: "https://www.tiktok.com/@user/video/123", badge: "Videos & Sounds", color: "hover:border-cyan-500 hover:text-cyan-500" },
  { id: "twitter", name: "X (Twitter)", exampleUrl: "https://x.com/user/status/123", badge: "Posts & Clips", color: "hover:border-sky-500 hover:text-sky-500" },
  { id: "reddit", name: "Reddit", exampleUrl: "https://www.reddit.com/r/videos/comments/123", badge: "Video & Audio", color: "hover:border-orange-500 hover:text-orange-500" },
  { id: "pinterest", name: "Pinterest", exampleUrl: "https://www.pinterest.com/pin/123", badge: "Pins & Clips", color: "hover:border-red-600 hover:text-red-600" },
  { id: "facebook", name: "Facebook", exampleUrl: "https://www.facebook.com/watch/?v=123", badge: "Public Videos", color: "hover:border-blue-600 hover:text-blue-600" },
  { id: "snapchat", name: "Snapchat", exampleUrl: "https://www.snapchat.com/spotlight/123", badge: "Public Spotlight", color: "hover:border-yellow-500 hover:text-yellow-600" },
  { id: "linkedin", name: "LinkedIn", exampleUrl: "https://www.linkedin.com/posts/123", badge: "Shared Media", color: "hover:border-blue-700 hover:text-blue-700" },
  { id: "threads", name: "Threads", exampleUrl: "https://www.threads.net/@user/post/123", badge: "Public Posts", color: "hover:border-stone-500 hover:text-stone-700" },
  { id: "discord", name: "Discord", exampleUrl: "https://cdn.discordapp.com/attachments/123/video.mp4", badge: "CDN Attachments", color: "hover:border-indigo-500 hover:text-indigo-500" },
  { id: "quora", name: "Quora", exampleUrl: "https://www.quora.com/answer/123", badge: "Media Answers", color: "hover:border-red-700 hover:text-red-700" },
];

interface PlatformIconsProps {
  onSelectExample?: (url: string) => void;
}

export function PlatformIcons({ onSelectExample }: PlatformIconsProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Supported Platforms (Public & Authorized Media)
        </h3>
        <span className="text-xs text-brand-600 dark:text-brand-400 font-medium">
          12 Networks Connected
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2.5">
        {PLATFORMS.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => onSelectExample && onSelectExample(p.exampleUrl)}
            className={cn(
              "flex flex-col items-start p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur-sm text-left transition-all text-slate-700 dark:text-slate-300 shadow-sm",
              p.color
            )}
          >
            <span className="text-sm font-semibold truncate w-full">{p.name}</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 truncate w-full">
              {p.badge}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

