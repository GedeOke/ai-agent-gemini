type SidebarProps = {
  collapsed: boolean;
  onToggle: () => void;
};

const navItems = [
  { label: "Dashboard", icon: "🏠" },
  { label: "Knowledge", icon: "📚" },
  { label: "Contacts", icon: "👥" },
  { label: "SOP", icon: "🧭" },
  { label: "Follow-up", icon: "⏰" },
  { label: "Settings", icon: "⚙️" },
];

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`${
        collapsed ? "w-16" : "w-64"
      } transition-all duration-200 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur`}
    >
      <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800">
        {!collapsed && (
          <div>
            <div className="font-bold text-lg">AI Agent</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">Admin Dashboard</p>
          </div>
        )}
        <button
          onClick={onToggle}
          className="h-8 w-8 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-center text-sm"
          aria-label="Toggle sidebar"
        >
          {collapsed ? "›" : "‹"}
        </button>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.label}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-primary/10 dark:hover:bg-slate-800"
          >
            <span className="text-lg">{item.icon}</span>
            {!collapsed && item.label}
          </button>
        ))}
      </nav>
      {!collapsed && (
        <div className="p-4">
          <button className="w-full rounded-xl bg-primary text-white py-2 text-sm font-semibold shadow hover:bg-primary-dark">
            Upgrade Pro
          </button>
        </div>
      )}
    </aside>
  );
}
