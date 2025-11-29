import { useState } from "react";
import type { ChatMessage } from "../types";

export function ChatTester() {
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { sender: "ai", text: "Hi, saya AI Agent. Coba uji respons di sini.", time: new Date().toLocaleTimeString() },
  ]);

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
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
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
  );
}
