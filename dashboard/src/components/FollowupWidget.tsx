import type { FollowupCounts } from "../types";

export function FollowupWidget({ counts }: { counts: FollowupCounts }) {
  const rows = [
    { label: "Pending", value: counts.pending, bar: "w-2/3", color: "bg-amber-500" },
    { label: "Sent", value: counts.sent, bar: "w-5/6", color: "bg-emerald-500" },
    { label: "Failed", value: counts.failed, bar: "w-1/6", color: "bg-rose-500" },
  ];
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold">Follow-up Status</h2>
      </div>
      <div className="p-4 space-y-3 text-sm">
        {rows.map((item) => (
          <div key={item.label}>
            <div className="flex justify-between">
              <span>{item.label}</span>
              <span className="font-semibold">{item.value}</span>
            </div>
            <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full mt-1">
              <div className={`h-2 ${item.color} rounded-full ${item.bar}`}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
