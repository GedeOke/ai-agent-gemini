import { useEffect, useMemo, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { HeaderBar } from "./components/HeaderBar";
import { StatCards } from "./components/StatCards";
import { ChatTester } from "./components/ChatTester";
import { ConfigCard } from "./components/ConfigCard";
import { FollowupWidget } from "./components/FollowupWidget";
import { SopWidget } from "./components/SopWidget";
import { UploadCard } from "./components/UploadCard";
import { ContactsCard } from "./components/ContactsCard";
import type { Config, Theme, FollowupCounts, Contact, ChatMessage } from "./types";

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
  const [followupCounts, setFollowupCounts] = useState<FollowupCounts>({ pending: 0, sent: 0, failed: 0 });
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [contactId, setContactId] = useState("");
  const [sopStep, setSopStep] = useState("reach out");
  const [uploadTags, setUploadTags] = useState("produk,harga");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { sender: "ai", text: "Hi, saya AI Agent. Coba uji respons di sini.", time: new Date().toLocaleTimeString() },
  ]);
  const [chatInput, setChatInput] = useState("");
  const headers = useMemo(
    () => ({
      "Content-Type": "application/json",
      "X-API-Key": config.apiKey,
      "X-Tenant-Id": config.tenantId,
    }),
    [config]
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  const loadSettings = async () => {
    try {
      const res = await fetch(`${config.baseUrl}/tenants/${config.tenantId}/settings`, { headers });
      if (!res.ok) throw new Error(await res.text());
      console.info("Settings loaded");
    } catch (err) {
      console.error(err);
    }
  };

  const saveSettings = async () => {
    // demo: just ping health to ensure connection
    try {
      const res = await fetch(`${config.baseUrl}/health`);
      if (!res.ok) throw new Error(await res.text());
      console.info("Connection OK");
    } catch (err) {
      console.error(err);
    }
  };

  const fetchFollowups = async () => {
    const counts: FollowupCounts = { pending: 0, sent: 0, failed: 0 };
    for (const status of ["pending", "sent", "failed"] as const) {
      const res = await fetch(`${config.baseUrl}/followup?status=${status}`, { headers });
      if (res.ok) {
        const data = (await res.json()) as any[];
        counts[status] = data.length;
      }
    }
    setFollowupCounts(counts);
  };

  const fetchContacts = async () => {
    const res = await fetch(`${config.baseUrl}/contacts`, { headers });
    if (!res.ok) return;
    const data = (await res.json()) as any[];
    const mapped: Contact[] = data.map((c) => ({ id: c.id, name: c.name, phone: c.phone, email: c.email }));
    setContacts(mapped);
    if (!contactId && mapped.length) setContactId(mapped[0].id);
  };

  const setSopState = async () => {
    if (!contactId) return;
    try {
      const res = await fetch(`${config.baseUrl}/sop/state`, {
        method: "PUT",
        headers,
        body: JSON.stringify({ tenant_id: config.tenantId, contact_id: contactId, user_id: "u1", current_step: sopStep }),
      });
      if (!res.ok) throw new Error(await res.text());
    } catch (err) {
      console.error(err);
    }
  };

  const uploadKb = async () => {
    if (!uploadFile) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("tenant_id", config.tenantId);
      fd.append("tags", uploadTags);
      fd.append("file", uploadFile);
      const res = await fetch(`${config.baseUrl}/kb/upload`, {
        method: "POST",
        headers: { "X-API-Key": config.apiKey, "X-Tenant-Id": config.tenantId },
        body: fd,
      });
      if (!res.ok) throw new Error(await res.text());
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    const time = new Date().toLocaleTimeString();
    const newMsg: ChatMessage = { sender: "user", text: chatInput, time };
    setChatMessages((prev) => [...prev, newMsg]);
    setChatInput("");
    try {
      const res = await fetch(`${config.baseUrl}/chat`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          tenant_id: config.tenantId,
          user_id: "tester",
          metadata: contactId ? { contact_id: contactId } : {},
          channel: "web",
          messages: [{ role: "user", content: newMsg.text }],
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      const reply: ChatMessage = {
        sender: "ai",
        text: data.full_text || "",
        time: new Date().toLocaleTimeString(),
        context: data.retrieved_context,
      };
      setChatMessages((prev) => [...prev, reply]);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchFollowups();
    fetchContacts();
  }, []); // initial

  const filteredContacts = contacts;

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
                <ConfigCard config={config} onChange={setConfig} onLoadSettings={loadSettings} onSaveSettings={saveSettings} />
              </div>
              <FollowupWidget counts={followupCounts} />
            </section>
            <section className="grid gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <ChatTester messages={chatMessages} input={chatInput} onInputChange={setChatInput} onSend={sendChat} />
              </div>
              <SopWidget
                contactId={contactId}
                sopStep={sopStep}
                onContactIdChange={setContactId}
                onSopStepChange={setSopStep}
                onSetState={setSopState}
              />
            </section>
            <section className="grid gap-4 lg:grid-cols-2">
              <UploadCard tags={uploadTags} onTagsChange={setUploadTags} onFileChange={setUploadFile} onUpload={uploadKb} uploading={uploading} />
              <ContactsCard contacts={filteredContacts} />
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
