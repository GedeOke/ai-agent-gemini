type Stat = { label: string; value: string; color: string };

const defaultStats: Stat[] = [
  { label: "Visitors", value: "1,294", color: "bg-amber-100 text-amber-700" },
  { label: "Sales", value: "$1,345", color: "bg-emerald-100 text-emerald-700" },
  { label: "Subscribers", value: "1,303", color: "bg-rose-100 text-rose-700" },
  { label: "Orders", value: "576", color: "bg-indigo-100 text-indigo-700" },
];

export function StatCards({ stats = defaultStats }: { stats?: Stat[] }) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((item) => (
        <div
          key={item.label}
          className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 shadow-sm"
        >
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{item.label}</p>
          <p className={`text-xl font-bold ${item.color.split(" ")[1]}`}>{item.value}</p>
        </div>
      ))}
    </section>
  );
}
