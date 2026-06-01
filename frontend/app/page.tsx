import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-[calc(100vh-53px)] bg-gray-50 flex items-center justify-center">
      <div className="text-center max-w-2xl px-6">

        {/* Hero */}
        <p className="text-6xl mb-6">🧠</p>
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Self-Healing RAG
        </h1>
        <p className="text-gray-500 text-lg mb-2">
          LangGraph + Llama3.2 + BGE-M3 + ChromaDB
        </p>
        <p className="text-gray-400 text-sm mb-10">
          Upload karo, pucho, aur AI automatically self-heal karega
        </p>

        {/* Buttons */}
        <div className="flex gap-4 justify-center mb-16">
          <Link href="/chat"
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-medium transition-colors">
            💬 Start Chatting
          </Link>
          <Link href="/upload"
            className="bg-white hover:bg-gray-100 text-gray-700 border border-gray-200 px-6 py-3 rounded-xl font-medium transition-colors">
            📤 Upload Document
          </Link>
        </div>

        {/* How it works */}
        <div className="grid grid-cols-3 gap-4 text-left">
          <div className="bg-white rounded-xl border p-4">
            <p className="text-2xl mb-2">📄</p>
            <p className="font-semibold text-gray-700 text-sm mb-1">1. Upload</p>
            <p className="text-xs text-gray-400">PDF, TXT, DOCX upload karo — ChromaDB mein index hoga</p>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <p className="text-2xl mb-2">🔍</p>
            <p className="font-semibold text-gray-700 text-sm mb-1">2. Retrieve</p>
            <p className="text-xs text-gray-400">BGE-M3 embeddings se relevant chunks dhundhe jaate hain</p>
          </div>
          <div className="bg-white rounded-xl border p-4">
            <p className="text-2xl mb-2">🔄</p>
            <p className="font-semibold text-gray-700 text-sm mb-1">3. Self-Heal</p>
            <p className="text-xs text-gray-400">Critic fail kare toh auto rewrite + retry hota hai</p>
          </div>
        </div>

      </div>
    </div>
  );
}