import type { ChatMessage } from "../types";

type Props = {
  messages: ChatMessage[];
  input: string;
  onInputChange: (v: string) => void;
  onSend: () => void;
};

export function ChatTester({ messages, input, onInputChange, onSend }: Props) {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Chatbot Tester</h2>
        <span className="text-xs text-slate-500 dark:text-slate-400">Live call to /chat</span>
      </div>
      <div className="p-4 space-y-3">
        <div className="h-72 overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 p-3 space-y-3">
          {messages.map((m, idx) => (
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
                {m.context && m.context.length > 0 && (
                  <div className="text-[10px] opacity-80 mt-1">ctx: {m.context.slice(0, 2).join(" | ")}</div>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSend()}
            placeholder="Ketik pesan uji..."
            className="flex-1 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
          />
          <button
            onClick={onSend}
            className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary-dark"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
