import { Loader2 } from 'lucide-react';

export const Loading = () => (
  <div className="min-h-[60vh] flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <Loader2 className="h-8 w-8 animate-spin text-primary-600 dark:text-primary-400" />
      <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Loading...</p>
    </div>
  </div>
);
