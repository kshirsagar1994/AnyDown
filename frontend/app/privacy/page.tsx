import { Shield, Lock, EyeOff, Trash2 } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:py-16 space-y-8">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 text-xs font-semibold border border-emerald-200 dark:border-emerald-800">
          <Shield className="w-3.5 h-3.5" />
          <span>Privacy & Data Protection</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
          Privacy Policy & Retention Lifecycle
        </h1>
        <p className="text-xs text-slate-500">Effective Date: October 2026</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
          <Lock className="w-5 h-5 text-brand-600" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">Zero Credentials</h3>
          <p className="text-xs text-slate-500">We never ask for, collect, or store social media passwords, tokens, or session cookies.</p>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
          <Trash2 className="w-5 h-5 text-emerald-600" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">15-Min Auto Purge</h3>
          <p className="text-xs text-slate-500">Temporary download files and cached metadata are permanently deleted automatically.</p>
        </div>
        <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2">
          <EyeOff className="w-5 h-5 text-indigo-600" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">Redacted Logs</h3>
          <p className="text-xs text-slate-500">Server logs redact sensitive query parameters, signed tokens, and personal IP identities.</p>
        </div>
      </div>

      <div className="prose dark:prose-invert max-w-none space-y-6 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Information We Process</h2>
          <p>
            When you enter a URL into AnyDown, our server parses the URL only to identify the destination host and query the authorized media stream. We do not maintain an archive or catalog of past links analyzed.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Data Retention Policy</h2>
          <p>
            Any files created during video/audio transcoding are saved in isolated temporary directories on the worker disk. Our background storage daemon scans and deletes all temporary directories older than 15 minutes (900 seconds).
          </p>
        </section>
      </div>
    </div>
  );
}

