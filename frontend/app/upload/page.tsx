"use client";

import { useState } from "react";
import { uploadFile, getIngestStatus } from "@/lib/api";

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage]     = useState("");
  const [error, setError]         = useState("");
  const [chunks, setChunks]       = useState<number | null>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage("");
    setError("");
    setChunks(null);

    try {
      const result = await uploadFile(file);
      setMessage(`✅ "${result.filename}" successfully uploaded!`);

      // Status bhi fetch karo
      const status = await getIngestStatus();
      setChunks(status.total_chunks);

    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(`❌ ${err.message}`);
      } else {
        setError("❌ Upload failed");
      }
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">📤 Upload Documents</h1>
          <p className="text-gray-500 text-sm mt-1">
            PDF, TXT, DOCX, MD files ChromaDB mein index honge
          </p>
        </div>

        {/* Upload Box */}
        <div className="bg-white rounded-xl border p-8 mb-6">
          <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors">
            <div className="text-center">
              <p className="text-4xl mb-3">📁</p>
              <p className="text-sm font-medium text-gray-600">
                {uploading ? "Uploading..." : "Click to select file"}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Supported: PDF, TXT, DOCX, MD
              </p>
            </div>
            <input
              type="file"
              className="hidden"
              accept=".pdf,.txt,.docx,.md"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </label>
        </div>

        {/* Success */}
        {message && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
            <p className="text-sm text-green-700 font-medium">{message}</p>
            {chunks !== null && (
              <p className="text-xs text-green-500 mt-1">
                Total chunks in DB: {chunks}
              </p>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="flex gap-4 mt-6">
          <a href="/" className="text-sm text-blue-500 hover:underline">
            ← Back to Chat
          </a>
          <a href="/status" className="text-sm text-blue-500 hover:underline">
            📊 View Status
          </a>
        </div>

      </div>
    </div>
  );
}