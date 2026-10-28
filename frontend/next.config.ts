import type { NextConfig } from "next";

const isExport = process.env.NEXT_EXPORT === "true";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  ...(isExport ? { output: "export" as const } : {}),
  images: {
    unoptimized: true,
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "**" },
    ],
  },
  ...(!isExport
    ? {
        async rewrites() {
          return [
            {
              source: "/api/v1/:path*",
              destination: "http://127.0.0.1:8000/api/v1/:path*",
            },
          ];
        },
      }
    : {}),
};

export default nextConfig;
