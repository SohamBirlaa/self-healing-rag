

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ====== types ========

export interface ChatResponse {
    answer: string;
    decision: string;
    confidence: number;
    retries: number;
    retrieval_score: number;
}

export interface IngestStatusResponse {
    total_chunks : number;
    message: string;
}

export interface DocumentsResponse {
    documents: string[];
    total: number;
}

export interface IngestFileResponse {
    message: string;
    chunks: number;
    filename: string;
}

//============ API FUNCTION ============

// chat
export async function sendChat(question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.statusText}`);
  return res.json();
}


// file upload

export async function uploadFile(file: File): Promise<IngestFileResponse> {
    const formData = new FormData();
    formData.append("file",file);
    const res = await fetch(`${API_URL}/ingest/file`, {
        method: "POST",
        body: formData
    });
    if (!res.ok){
        const error = await res.json();
        throw new Error(error.detail || "Upload failed");
    }
    return res.json()
    
}


// status

export async function getIngestStatus(): Promise<IngestStatusResponse> {
    const res = await fetch(`${API_URL}/ingest/status`);
    if (!res.ok) throw new Error("Status fetch failed");
    return res.json();
    
}


// documents list

export async function getDocuments(): Promise<DocumentsResponse> {
    const res = await fetch(`${API_URL}/ingest/documents`);
    if (!res.ok) throw new Error("Documents fetch failed");
    return res.json()
    
}

// clear chroma db

export async function clearDocuments(): Promise<{message: string}> {
    const res = await fetch(`${API_URL}/ingest/clear`,{method: "DELETE"});
    if (!res.ok) throw new Error("Clear failed");
    return res.json();
    
}