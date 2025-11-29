import type { Theme } from "../types";

type HeaderBarProps = {
  theme: Theme;
  onToggleTheme: () => void;
  tenantId: string;
};

export function HeaderBar({ theme, onToggleTheme, tenantId }: HeaderBarProps) {
  return (
    <header className="flex items-center justify-between px-4 lg:px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/80 backdrop-blur">
      <div className="flex items-center gap-3">
        <input
          placeholder="Search…"
          className="hidden md:block w-72 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-2 text-sm"
        />
        <div className="text-sm text-slate-500 dark:text-slate-400">Tenant: {tenantId || "demo"}</div>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleTheme}
          className="rounded-full border border-slate-200 dark:border-slate-700 px-3 py-2 text-sm font-semibold"
        >
          {theme === "light" ? "🌙 Dark" : "☀️ Light"}
        </button>
        <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary to-primary-dark text-white flex items-center justify-center font-bold">
          AI
        </div>
      </div>
    </header>
  );
}
