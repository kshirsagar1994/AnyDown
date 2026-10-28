import { Scale, CheckCircle2, AlertOctagon } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:py-16 space-y-8">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/60 text-brand-700 dark:text-brand-300 text-xs font-semibold border border-brand-200 dark:border-brand-800">
          <Scale className="w-3.5 h-3.5" />
          <span>Legal Agreement</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
          Terms of Service & Acceptable Use
        </h1>
        <p className="text-xs text-slate-500">Last updated: October 2026</p>
      </div>

      <div className="prose dark:prose-invert max-w-none space-y-6 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">1. Core User Authorization Requirement</h2>
          <p>
            AnyDown is provided exclusively as a technical media extraction utility for users who own the content, have explicit permission from the copyright owner, or where the relevant content is provided under a permissive license (such as Creative Commons) or lawful platform terms.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">2. Absolute Non-Circumvention Rule</h2>
          <p>
            AnyDown does not, and will never, bypass:
          </p>
          <ul className="list-disc pl-5 space-y-1 text-slate-600 dark:text-slate-400">
            <li>Digital Rights Management (DRM) encryption or technological protection measures.</li>
            <li>Private-account access controls, follower-only restrictions, or age-verification walls.</li>
            <li>Platform login barriers or subscriber-only paywalls.</li>
            <li>Anti-bot mechanisms or platform rate limits.</li>
          </ul>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">3. User Responsibility & Indemnification</h2>
          <p>
            Users are solely responsible for verifying their rights to download any media link processed through AnyDown. AnyDown disclaims all liability for unauthorized copying, redistribution, or infringement of third-party copyrights conducted by end users.
          </p>
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">4. Temporary Processing Only</h2>
          <p>
            AnyDown does not provide media hosting, cloud storage, or public indexing. All media processed during a download job is strictly short-lived and automatically purged from temporary buffers within 15 minutes of completion.
          </p>
        </section>
      </div>
    </div>
  );
}

