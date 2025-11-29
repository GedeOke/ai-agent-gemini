import { useEffect, useState } from "react";

type Theme = "light" | "dark";
type Config = { baseUrl: string; apiKey: string; tenantId: string };
type ChatMessage = { sender: "user" | "ai"; text: string; time: string };

const STORAGE_KEY = "agent_dashboard_config";

const navItems = [
  { label: "Dashboard", icon: "🏠" },
  { label: "Knowledge", icon: "📚" },
  { label: "Contacts", icon: "👥" },
  { label: "SOP", icon: "🧭" },
  { label: "Follow-up", icon: "⏰" },
  { label: "Settings", icon: "⚙️" },
];

function loadConfig(): Config {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Config;
  } catch {
    /* ignore */
  }
  return { baseUrl: "http://localhost:8000", apiKey: "", tenantId: "demo" };
}

function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    return "light";
  });
  const [config, setConfig] = useState<Config>(loadConfig);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { sender: "ai", text: "Hi, saya AI Agent. Coba uji respons di sini.", time: new Date().toLocaleTimeString() },
  ]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    const time = new Date().toLocaleTimeString();
    setChatMessages((prev) => [...prev, { sender: "user", text: chatInput, time }]);
    setChatInput("");
    setTimeout(
      () =>
        setChatMessages((prev) => [
          ...prev,
          { sender: "ai", text: "Ini respons dummy untuk preview UI.", time: new Date().toLocaleTimeString() },
        ]),
      500
    );
  };

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <aside className="hidden lg:flex w-64 flex-col border-r border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur">
          <div className="p-5 border-b border-slate-200 dark:border-slate-800">
            <div className="font-bold text-xl">AI Agent Admin</div>
            <p className="text-xs text-slate-500 dark:text-slate-400">CRM Assistant Dashboard</p>
          </div>
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.label}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-primary/10 dark:hover:bg-slate-800"
              >
                <span>{item.icon}</span>
                {item.label}
              </button>
            ))}
          </nav>
          <div className="p-4">
            <button className="w-full rounded-xl bg-primary text-white py-2 text-sm font-semibold shadow hover:bg-primary-dark">
              Upgrade Pro
            </button>
          </div>
        </aside>

        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="flex items-center justify-between px-4 lg:px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/80 backdrop-blur">
            <div className="flex items-center gap-3">
              <input
                placeholder="Search…"
                className="hidden md:block w-72 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-2 text-sm"
              />
              <div className="text-sm text-slate-500 dark:text-slate-400">Tenant: {config.tenantId || "demo"}</div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
                className="rounded-full border border-slate-200 dark:border-slate-700 px-3 py-2 text-sm font-semibold"
              >
                {theme === "light" ? "🌙 Dark" : "☀️ Light"}
              </button>
              <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary to-primary-dark text-white flex items-center justify-center font-bold">
                AI
              </div>
            </div>
          </header>

          {/* Main content */}
          <main className="p-4 lg:p-6 space-y-6">
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {[
                { label: "Visitors", value: "1,294", color: "bg-amber-100 text-amber-700" },
                { label: "Sales", value: "$1,345", color: "bg-emerald-100 text-emerald-700" },
                { label: "Subscribers", value: "1,303", color: "bg-rose-100 text-rose-700" },
                { label: "Orders", value: "576", color: "bg-indigo-100 text-indigo-700" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 shadow-sm"
                >
                  <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{item.label}</p>
                  <p className={`text-xl font-bold ${item.color.split(" ")[1]}`}>{item.value}</p>
                </div>
              ))}
            </section>

            <section className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-lg font-semibold">API Config</h2>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    Headers: X-API-Key / X-Tenant-Id
                  </span>
                </div>
                <div className="p-4 grid gap-3 sm:grid-cols-3">
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Base URL</span>
                    <input
                      className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
                      value={config.baseUrl}
                      onChange={(e) => setConfig((c) => ({ ...c, baseUrl: e.target.value }))}
                    />
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Tenant ID</span>
                    <input
                      className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
                      value={config.tenantId}
                      onChange={(e) => setConfig((c) => ({ ...c, tenantId: e.target.value }))}
                    />
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">API Key</span>
                    <input
                      className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm"
                      value={config.apiKey}
                      onChange={(e) => setConfig((c) => ({ ...c, apiKey: e.target.value }))}
                    />
                  </label>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-lg font-semibold">Follow-up Status</h2>
                </div>
                <div className="p-4 space-y-3 text-sm">
                  {[
                    { label: "Pending", value: 3, bar: "w-2/3", color: "bg-amber-500" },
                    { label: "Sent", value: 12, bar: "w-5/6", color: "bg-emerald-500" },
                    { label: "Failed", value: 0, bar: "w-1/6", color: "bg-rose-500" },
                  ].map((item) => (
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
            </section>

            <section className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Chatbot Tester</h2>
                  <span className="text-xs text-slate-500 dark:text-slate-400">Dummy preview</span>
                </div>
                <div className="p-4 space-y-3">
                  <div className="h-72 overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 p-3 space-y-3">
                    {chatMessages.map((m, idx) => (
                      <div key={idx} className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}>
                        <div
                          className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm shadow ${
                            m.sender === "user"
                              ? "bg-primary text-white"
                              : "bg-white dark:bg-slate-900/80 text-slate-900 dark:text-slate-100 border border-slate-200 dark:border-slate-700"
                          }`}
                        >
                          <div>{m.text}</div>
                          <div className="text-[10px] opacity-70 mt-1">{m.time}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                      placeholder="Ketik pesan uji..."
                      className="flex-1 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
                    />
                    <button
                      onClick={handleSendChat}
                      className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-lg font-semibold">SOP Quick Set</h2>
                </div>
                <div className="p-4 space-y-3 text-sm">
                  <label className="flex flex-col gap-1">
                    <span className="text-slate-500 dark:text-slate-400">Contact (ID)</span>
                    <input className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-3 py-2" placeholder="Contact ID" />
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
            </section>

            <section className="grid gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-lg font-semibold">Upload Knowledge</h2>
                </div>
                <div className="p-4 grid gap-3 sm:grid-cols-2">
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">Tags</span>
                    <input className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 px-3 py-2" placeholder="produk,harga" />
                  </label>
                  <label className="flex flex-col gap-1 text-sm">
                    <span className="text-slate-500 dark:text-slate-400">File</span>
                    <input type="file" className="text-sm" />
                  </label>
                  <div className="col-span-full flex gap-2">
                    <button className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark">
                      Upload (mock)
                    </button>
                    <button className="rounded-lg border border-slate-200 dark:border-slate-800 px-4 py-2 text-sm text-slate-700 dark:text-slate-200">
                      Lihat KB (mock)
                    </button>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">
                  <h2 className="text-lg font-semibold">Contacts Snapshot</h2>
                </div>
                <div className="p-4 space-y-2 text-sm">
                  {[
                    { name: "Budi", phone: "+62 812 3456 7890", status: "Active" },
                    { name: "Ana", phone: "+62 811 1111", status: "Pending" },
                    { name: "Celine", phone: "+62 899 8888", status: "Follow-up" },
                  ].map((c) => (
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
            </section>
          </main>

          <footer className="px-4 lg:px-6 py-4 text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-900/80">
            © {new Date().getFullYear()} AI Agent Dashboard. Preview UI with theme toggle.
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
