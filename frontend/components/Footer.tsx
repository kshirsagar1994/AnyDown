import Link from "next/link";
import { ShieldCheck, Heart } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 mt-20 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              AnyDown Media Engine
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md leading-relaxed">
              AnyDown provides a unified, lawful interface to analyze and download accessible public media in genuine formats. We enforce truthful format availability and strictly prohibit unauthorized circumvention.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-500 pt-2">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Zero credentials stored • Automatic temporary file lifecycle</span>
            </div>
          </div>

          {/* Platform & Resources */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Navigation
            </h4>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>
                <Link href="/" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                  Media Downloader
                </Link>
              </li>
              <li>
                <Link href="/platforms" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                  Supported Platforms
                </Link>
              </li>
              <li>
                <a
                  href="http://127.0.0.1:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
                >
                  API Documentation
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-white mb-3">
              Compliance & Legal
            </h4>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li>
                <Link href="/terms" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/copyright" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                  DMCA & Abuse Takedown
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-200 dark:border-slate-800 mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-500">
          <p>© {new Date().getFullYear()} AnyDown. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 text-center sm:text-right">
            Platform names and logos are trademarks of their respective owners. AnyDown is not endorsed by or affiliated with them.
          </p>
        </div>
      </div>
    </footer>
  );
}

