import type { Config } from "../types";

type Props = {
  config: Config;
  onChange: (cfg: Config) => void;
};

export function ConfigCard({ config, onChange }: Props) {
  const update = (field: keyof Config, value: string) => onChange({ ...config, [field]: value });

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">API Config</h2>
        <span className="text-xs text-slate-500 dark:text-slate-400">Headers: X-API-Key / X-Tenant-Id</span>
      </div>
      <div className="p-4 grid gap-3 sm:grid-cols-3">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500 dark:text-slate-400">Base URL</span>
          <input
            className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
            value={config.baseUrl}
            onChange={(e) => update("baseUrl", e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500 dark:text-slate-400">Tenant ID</span>
          <input
            className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
            value={config.tenantId}
            onChange={(e) => update("tenantId", e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500 dark:text-slate-400">API Key</span>
          <input
            className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
            value={config.apiKey}
            onChange={(e) => update("apiKey", e.target.value)}
          />
        </label>
      </div>
    </div>
  );
}
