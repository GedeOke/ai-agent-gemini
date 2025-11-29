import { useEffect, useMemo, useState } from "react";

type Theme = "light" | "dark";

type Config = {
  baseUrl: string;
  apiKey: string;
  tenantId: string;
};

type ChatMessage = { sender: "user" | "ai"; text: string; time: string };

const STORAGE_KEY = "agent_dashboard_config";

function loadConfig(): Config {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Config;
  } catch (err) {
    console.warn("Failed to load config", err);
  }
  return { baseUrl: "http://localhost:8000", apiKey: "", tenantId: "" };
}

function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    return "light";
  });
  const [config, setConfig] = useState<Config>(loadConfig);
  const [toast, setToast] = useState<string | null>(null);
  const [kbTags, setKbTags] = useState("produk,harga");
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [sopStep, setSopStep] = useState("reach out");
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { sender: "ai", text: "Hi, saya AI Agent. Ayo uji respons di sini.", time: new Date().toLocaleTimeString() },
  ]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  const headersPreview = useMemo(
    () => ({
      "X-API-Key": config.apiKey || "<tenant_api_key>",
      "X-Tenant-Id": config.tenantId || "<tenant_id>",
    }),
    [config]
  );

  const toggleTheme = () => setTheme((t) => (t === "light" ? "dark" : "light"));

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  };

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    const time = new Date().toLocaleTimeString();
    setChatMessages((prev) => [...prev, { sender: "user", text: chatInput, time }]);
    // mock AI response
    setTimeout(() => {
      setChatMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Ini respons dummy untuk pengujian UI chatbot.", time: new Date().toLocaleTimeString() },
      ]);
    }, 600);
    setChatInput("");
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">AI Agent Dashboard</p>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">CRM Assistant Control Center</h1>
            <p className="text-slate-600 dark:text-slate-400 text-sm">
              Atur tenant, knowledge base, SOP, dan uji chatbot dalam satu tempat.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="rounded-full border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-100 bg-white dark:bg-slate-800 shadow-sm"
            >
              {theme === "light" ? "🌙 Dark" : "☀️ Light"}
            </button>
            <button
              onClick={() => showToast("Config disimpan lokal")}
              className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold shadow-sm hover:bg-primary-dark"
            >
              Simpan Config
            </button>
          </div>
        </header>

        {toast && (
          <div className="rounded-lg bg-emerald-500 text-white px-4 py-2 text-sm inline-block shadow-soft">{toast}</div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Tenant", value: config.tenantId || "demo" },
            { label: "Channel", value: "Web/Telegram (planned)" },
            { label: "Follow-up Pending", value: "3" },
            { label: "KB Items", value: "—" },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 px-4 py-3 shadow-sm"
            >
              <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">{item.label}</p>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">{item.value}</p>
            </div>
          ))}
        </div>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm lg:col-span-2 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Konfigurasi API</h2>
              <span className="text-xs text-slate-500 dark:text-slate-400">Headers: {headersPreview["X-API-Key"]}</span>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">Base URL</span>
                <input
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                  value={config.baseUrl}
                  onChange={(e) => setConfig((c) => ({ ...c, baseUrl: e.target.value }))}
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">Tenant ID</span>
                <input
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                  value={config.tenantId}
                  onChange={(e) => setConfig((c) => ({ ...c, tenantId: e.target.value }))}
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">API Key</span>
                <input
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                  value={config.apiKey}
                  onChange={(e) => setConfig((c) => ({ ...c, apiKey: e.target.value }))}
                />
              </label>
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400">
              Headers preview: X-API-Key: {headersPreview["X-API-Key"]}, X-Tenant-Id: {headersPreview["X-Tenant-Id"]}
            </div>
          </div>

          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm space-y-3">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Upload Knowledge</h2>
            <label className="flex flex-col gap-2 text-sm">
              <span className="text-slate-600 dark:text-slate-300">Tags</span>
              <input
                value={kbTags}
                onChange={(e) => setKbTags(e.target.value)}
                className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2"
              />
            </label>
            <label className="flex flex-col gap-2 text-sm">
              <span className="text-slate-600 dark:text-slate-300">File</span>
              <input type="file" className="text-sm" />
            </label>
            <button className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary-dark">
              Upload (mock)
            </button>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm space-y-3 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Kontak & SOP State</h2>
              <span className="text-xs text-slate-500 dark:text-slate-400">Demo form</span>
            </div>
            <div className="grid sm:grid-cols-3 gap-3">
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">Nama Kontak</span>
                <input
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">Phone</span>
                <input
                  value={contactPhone}
                  onChange={(e) => setContactPhone(e.target.value)}
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                />
              </label>
              <label className="flex flex-col gap-1 text-sm">
                <span className="text-slate-600 dark:text-slate-300">SOP Step</span>
                <select
                  value={sopStep}
                  onChange={(e) => setSopStep(e.target.value)}
                  className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
                >
                  {["reach out", "keluhan", "konsultasi", "rekomendasi", "harga"].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
            </div>
            <div className="flex gap-2">
              <button className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark">
                Simpan Kontak (mock)
              </button>
              <button className="rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                Set SOP State (mock)
              </button>
            </div>
          </div>

          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm space-y-3">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Follow-up Status</h2>
            <div className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
              <div className="flex justify-between">
                <span>Pending</span>
                <span className="font-semibold">3</span>
              </div>
              <div className="flex justify-between">
                <span>Sent</span>
                <span className="font-semibold">12</span>
              </div>
              <div className="flex justify-between">
                <span>Failed</span>
                <span className="font-semibold">0</span>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm space-y-3">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Chatbot Tester</h2>
            <div className="h-64 overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 p-3 space-y-3">
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
                className="flex-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-800 px-3 py-2 text-sm"
              />
              <button
                onClick={handleSendChat}
                className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark"
              >
                Send
              </button>
            </div>
          </div>

          <div className="rounded-2xl bg-white dark:bg-slate-900/70 border border-slate-200/80 dark:border-slate-700 p-4 shadow-sm space-y-3">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Docs / Tips</h2>
            <ul className="list-disc pl-5 text-sm text-slate-600 dark:text-slate-300 space-y-2">
              <li>Isi Base URL, Tenant ID, dan API Key sekali; simpan di localStorage.</li>
              <li>Upload dokumen (PDF/CSV/XLSX) untuk pengetahuan bisnis, lalu uji di Chatbot.</li>
              <li>SOP state tersimpan per contact/user, bisa di-set manual atau otomatis dari chat.</li>
              <li>Switch tema Light/Dark untuk preview tampilan di mode berbeda.</li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
