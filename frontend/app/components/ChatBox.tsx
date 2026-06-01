"use client";

import { useState } from "react";
import { sendChat } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import MetricsPanel from "./MetricsPanel";

// Message ka type
interface Message {
  role: "user" | "assistant";
  content: string;
  metrics?: {
    decision: string;
    confidence: number;
    retries: number;
    retrieval_score: number;
  };
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    const question = input.trim();
    if (!question || loading) return;

    // User message add karo
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const result = await sendChat(question);

      // AI message add karo with metrics
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          metrics: {
            decision:        result.decision,
            confidence:      result.confidence,
            retries:         result.retries,
            retrieval_score: result.retrieval_score,
          },
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: " Error: Backend se connect nahi ho saka. Kya FastAPI chal rahi hai?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Enter key se send karo
  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleSend();
  }

  return (
    <div className="flex flex-col h-full">

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-20">
            <p className="text-2xl mb-2">🤖</p>
            <p className="text-sm">Kuch bhi pucho — documents ke baare mein</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            <MessageBubble role={msg.role} content={msg.content} />
            {/* Metrics sirf AI messages ke neeche dikhao */}
            {msg.role === "assistant" && msg.metrics && (
              <MetricsPanel {...msg.metrics} />
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 rounded-2xl rounded-tl-none px-4 py-3 text-sm text-gray-500">
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Question pucho..."
          disabled={loading}
          className="flex-1 border border-gray-300 rounded-xl px-4 py-2 text-sm text-gray-900 focus:outline-none focus:border-blue-400 disabled:bg-gray-50"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors"
        >
          Send
        </button>
      </div>

    </div>
  );
}