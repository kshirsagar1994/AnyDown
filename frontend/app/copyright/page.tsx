import { AlertCircle, Mail, FileText, CheckCircle2 } from "lucide-react";

export default function CopyrightPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:py-16 space-y-8">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 text-xs font-semibold border border-rose-200 dark:border-rose-800">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Intellectual Property</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
          DMCA Notice & Copyright Abuse Contact
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          AnyDown respects the intellectual property rights of creators and copyright owners worldwide.
        </p>
      </div>

      <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4 text-sm text-slate-700 dark:text-slate-300">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">
          Notice of Copyright Infringement (DMCA Procedure)
        </h2>
        <p>
          If you are a copyright owner or an agent thereof and believe that any functionality or content accessible via AnyDown infringes upon your copyright, you may submit a formal notification to our Designated Copyright Agent containing the following information:
        </p>

        <ol className="list-decimal pl-5 space-y-2 text-xs sm:text-sm text-slate-600 dark:text-slate-400">
          <li>A physical or electronic signature of a person authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.</li>
          <li>Identification of the copyrighted work claimed to have been infringed.</li>
          <li>Identification of the material that is claimed to be infringing or to be the subject of infringing activity, with sufficient detail to allow us to locate it.</li>
          <li>Contact information including an address, telephone number, and email address.</li>
          <li>A statement that you have a good faith belief that use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.</li>
          <li>A statement that the information in the notification is accurate, and under penalty of perjury, that you are authorized to act on behalf of the owner.</li>
        </ol>

        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center gap-3">
          <Mail className="w-5 h-5 text-brand-600 flex-shrink-0" />
          <div>
            <div className="font-semibold text-slate-900 dark:text-white text-sm">
              Designated Agent Email:
            </div>
            <a
              href="mailto:dmca@anydown.local"
              className="text-xs sm:text-sm text-brand-600 dark:text-brand-400 hover:underline"
            >
              dmca@anydown.local / abuse@anydown.local
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

