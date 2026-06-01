import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Self-Healing RAG",
  description: "LangGraph + Llama3.2 + ChromaDB",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧠</text></svg>",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">

        {/* Navbar */}
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          
          {/* Logo */}
          <a href="/" className="flex items-center gap-2">
            <span className="text-xl">🧠</span>
            <span className="font-bold text-gray-800">Self-Healing RAG</span>
          </a>

          {/* Links */}
          <div className="flex items-center gap-6">
            <a href="/chat" className="text-sm text-gray-600 hover:text-blue-500 transition-colors">
              💬 Chat
            </a>
            <a href="/upload" className="text-sm text-gray-600 hover:text-blue-500 transition-colors">
              📤 Upload
            </a>
            <a href="/status" className="text-sm text-gray-600 hover:text-blue-500 transition-colors">
              📊 Status
            </a>
          </div>

        </nav>

        {/* Page content */}
        {children}

      </body>
    </html>
  );
}