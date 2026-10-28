import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "AnyDown — Universal Media Analysis & Format Downloader",
  description: "Analyze and download public videos, audio tracks, and images in truthful available formats with real-time progress.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script src="/config.js" />
        {/* Adsterra Popunder Ad */}
        <script
          data-cfasync="false"
          src="https://accountut.com/1/e4a8db086145e255eb3dd3e35c07d1e4"
        />
        {/* Adsterra Social Bar Ad */}
        <script
          data-cfasync="false"
          src="https://bellnewyork.org/14/719dbaa2b0800fd9cb1801ece80b6cd9"
        />
      </head>
      <body className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 flex flex-col">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

