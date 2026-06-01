"use client"

import React, { useState } from "react"
import { uploadFile } from "@/lib/api"

export default function FileUpload() {
    const[uploading, setUploading] = useState(false);
    const[message, setMessage] = useState("");
    const [error, setError] = useState("");

    async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;

        setUploading(true);
        setMessage("");
        setError("");

        try{
            const result = await uploadFile(file);
            setMessage(`"${result.filename}" uploaded - ${result.chunks} chunk indexed`);
        } catch (err:unknown){
            if(err instanceof Error){
                setError(`${err.message}`);
            } else{
                setError("Upload failed");
            }
        }finally{
            setUploading(false);
            e.target.value=""; // input reset karo
        }
        
    }

    return(
        <div className="bg-white border border-gray-200 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Upload Document
            </h3>

            {/*File input*/}
            <label className="flex items-center justify-center w-full h-24 border-dashed
            border-gray-300 rounded-lg cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors">
                <div className="text-center">
                    <p className="text-sm text-gray-500">
                        {uploading?"Uploading...":"Click to upload"}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                        PDF, TXT, DOCX, MD
                    </p>
                </div>
                <input type="file"
                       className="hidden"
                       accept=".pdf,.txt,.docx,.md"
                       onChange={handleFileChange}
                        />
            </label>

            {/* Success message*/}
            {message &&(
                <p className="mt-3 text-sm text-green-600 bg-gray-50 rounded-lg px-3 py-2">
                    {message}
                </p>
            )}

            {/* Error message*/}
            {error &&(
                <p className="mt-3 text-red-600 bg-red-50 rounded-lg px-3 py-2">
                    {error}
                </p>
            )}
        </div>
    );
}