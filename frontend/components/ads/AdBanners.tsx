"use client";

import { useEffect, useRef } from "react";

interface AdIframeProps {
  adKey: string;
  width: number;
  height: number;
  className?: string;
  label?: string;
}

export function AdIframe({ adKey, width, height, className = "", label = "Advertisement" }: AdIframeProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";

    const iframe = document.createElement("iframe");
    iframe.width = width.toString();
    iframe.height = height.toString();
    iframe.style.border = "none";
    iframe.style.overflow = "hidden";
    iframe.scrolling = "no";

    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {
              margin: 0;
              padding: 0;
              display: flex;
              justify-content: center;
              align-items: center;
              background: transparent;
              overflow: hidden;
            }
          </style>
        </head>
        <body>
          <script type="text/javascript">
            atOptions = {
              'key' : '${adKey}',
              'format' : 'iframe',
              'height' : ${height},
              'width' : ${width},
              'params' : {}
            };
          </script>
          <script type="text/javascript" src="https://bellnewyork.org/22/${adKey}"></script>
        </body>
      </html>
    `;

    containerRef.current.appendChild(iframe);
    const doc = iframe.contentWindow?.document || iframe.contentDocument;
    if (doc) {
      doc.open();
      doc.write(htmlContent);
      doc.close();
    }
  }, [adKey, width, height]);

  return (
    <div className={`flex flex-col items-center justify-center my-4 ${className}`}>
      {label && (
        <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500 mb-1">
          {label}
        </span>
      )}
      <div
        ref={containerRef}
        className="flex items-center justify-center overflow-hidden max-w-full rounded-lg"
        style={{ minHeight: `${height}px`, minWidth: `${Math.min(width, 320)}px` }}
      />
    </div>
  );
}

export function Banner728x90({ className = "" }: { className?: string }) {
  return (
    <AdIframe
      adKey="cba33abdbb228a5d54e43a0b748203d8"
      width={728}
      height={90}
      className={className}
      label="Sponsored"
    />
  );
}

export function Banner160x600({ className = "" }: { className?: string }) {
  return (
    <AdIframe
      adKey="658ad484883b0dacc600771800e4617c"
      width={160}
      height={600}
      className={className}
      label="Advertisement"
    />
  );
}
