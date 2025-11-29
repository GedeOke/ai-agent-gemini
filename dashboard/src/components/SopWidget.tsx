export function SopWidget() {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold">SOP Quick Set</h2>
      </div>
      <div className="p-4 space-y-3 text-sm">
        <label className="flex flex-col gap-1">
          <span className="text-slate-500 dark:text-slate-400">Contact (ID)</span>
          <input
            className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-3 py-2"
            placeholder="Contact ID"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-slate-500 dark:text-slate-400">Current Step</span>
          <select className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-3 py-2">
            {["reach out", "keluhan", "konsultasi", "rekomendasi", "harga"].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </label>
        <button className="w-full rounded-lg bg-primary text-white py-2 font-semibold">Set SOP State (mock)</button>
      </div>
    </div>
  );
}
