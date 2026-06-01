"use client";

import { useEffect, useState } from "react";
import { getIngestStatus, getDocuments, clearDocuments } from "@/lib/api";

export default function StatusPage() {
  const [chunks, setChunks]     = useState<number>(0);
  const [docs, setDocs]         = useState<string[]>([]);
  const [clearing, setClearing] = useState(false);
  const [message, setMessage]   = useState("");

  async function loadStatus() {
    const status = await getIngestStatus();
    const docsRes = await getDocuments();
    setChunks(status.total_chunks);
    setDocs(docsRes.documents);
  }

  async function handleClear() {
    if (!confirm("Saare documents delete karna chahte ho?")) return;
    setClearing(true);
    await clearDocuments();
    setMessage("✅ ChromaDB cleared!");
    await loadStatus();
    setClearing(false);
  }

  useEffect(() => { loadStatus(); }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">📊 Database Status</h1>
          <p className="text-gray-500 text-sm mt-1">ChromaDB indexed documents</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white rounded-xl border p-6">
            <p className="text-sm text-gray-500">Total Chunks</p>
            <p className="text-3xl font-bold text-blue-500 mt-1">{chunks}</p>
          </div>
          <div className="bg-white rounded-xl border p-6">
            <p className="text-sm text-gray-500">Indexed Files</p>
            <p className="text-3xl font-bold text-green-500 mt-1">{docs.length}</p>
          </div>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-xl border p-6 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Indexed Documents</h2>
          {docs.length === 0 ? (
            <p className="text-sm text-gray-400">Koi documents indexed nahi hain.</p>
          ) : (
            <ul className="space-y-2">
              {docs.map((doc, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-green-500">📄</span> {doc}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Clear Button */}
        <button
          onClick={handleClear}
          disabled={clearing}
          className="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-6 py-2 rounded-xl text-sm font-medium transition-colors"
        >
          {clearing ? "Clearing..." : "🗑️ Clear ChromaDB"}
        </button>

        {message && (
          <p className="mt-4 text-sm text-green-600">{message}</p>
        )}

        {/* Back to chat */}
        <a href="/" className="block mt-6 text-sm text-blue-500 hover:underline">
          ← Back to Chat
        </a>

      </div>
    </div>
  );
}