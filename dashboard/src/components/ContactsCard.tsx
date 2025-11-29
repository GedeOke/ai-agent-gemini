import type { Contact } from "../types";

export function ContactsCard({ contacts }: { contacts: Contact[] }) {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
        <h2 className="text-lg font-semibold">Contacts Snapshot</h2>
      </div>
      <div className="p-4 space-y-2 text-sm">
        {contacts.map((c) => (
          <div
            key={c.name}
            className="flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-800 px-3 py-2"
          >
            <div>
              <p className="font-semibold">{c.name}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{c.phone}</p>
            </div>
            <span className="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              {c.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
