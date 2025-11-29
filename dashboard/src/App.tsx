import { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { HeaderBar } from "./components/HeaderBar";
import { StatCards } from "./components/StatCards";
import { ChatTester } from "./components/ChatTester";
import { ConfigCard } from "./components/ConfigCard";
import { FollowupWidget } from "./components/FollowupWidget";
import { SopWidget } from "./components/SopWidget";
import { UploadCard } from "./components/UploadCard";
import { ContactsCard } from "./components/ContactsCard";
import type { Config, Theme } from "./types";

const STORAGE_KEY = "agent_dashboard_config";

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
  const [theme, setTheme] = useState<Theme>(() =>
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  );
  const [collapsed, setCollapsed] = useState(false);
  const [config, setConfig] = useState<Config>(loadConfig);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
        <div className="flex-1 flex flex-col">
          <HeaderBar theme={theme} onToggleTheme={() => setTheme((t) => (t === "light" ? "dark" : "light"))} tenantId={config.tenantId} />
          <main className="p-4 lg:p-6 space-y-6">
            <StatCards />
            <section className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <ConfigCard config={config} onChange={setConfig} />
              </div>
              <FollowupWidget />
            </section>
            <section className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <ChatTester />
              </div>
              <SopWidget />
            </section>
            <section className="grid gap-4 lg:grid-cols-2">
              <UploadCard />
              <ContactsCard />
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
