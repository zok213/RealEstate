"use client";

import React, { useState, useCallback } from 'react';
import { Upload, X, Database, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { FloatingChatButton } from '@/components/floating-chat-button';

export default function UploadDXFPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      const fileName = file.name.toLowerCase();
      if (fileName.endsWith('.dxf') || fileName.endsWith('.dwg')) {
        setSelectedFile(file);
      } else {
        alert('Please upload a DXF or DWG file');
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const fileName = file.name.toLowerCase();
      if (fileName.endsWith('.dxf') || fileName.endsWith('.dwg')) {
        setSelectedFile(file);
      } else {
        alert('Please upload a DXF or DWG file');
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(interval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Call MVP Auto-Design endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'}/api/auto-design?output_format=json`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);
      setUploadProgress(100);

      if (response.ok) {
        const data = await response.json();
        console.log('Auto-design result:', data);

        // Store result in sessionStorage for analysis page
        sessionStorage.setItem('autoDesignResult', JSON.stringify(data));

        // Redirect to analysis page with new project
        setTimeout(() => {
          const projectId = data.filename?.replace('.dxf', '').replace('.dwg', '') || 'new-project';
          router.push(`/estate/${projectId}/analysis`);
        }, 500);
      } else {
        const errorData = await response.json();
        alert(`Upload failed: ${errorData.detail || 'Please try again.'}`);
        setUploadProgress(0);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please check your connection and ensure the backend is running.');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-[#254632] bg-[#0a120d] px-6 py-4 lg:px-10 z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="text-gray-300 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <h2 className="text-lg font-semibold leading-tight tracking-tight uppercase text-white">
            Upload DXF File
          </h2>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            className="border-[#254632] hover:bg-[#254632] text-white"
            onClick={() => router.back()}
          >
            Back
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full flex justify-center p-4 md:p-8 lg:p-12 overflow-y-auto">
        <div className="w-full max-w-4xl flex flex-col gap-10">

          {/* Progress Steps */}
          <nav className="flex items-center justify-between w-full max-w-2xl mx-auto mb-4">
            <div className="flex flex-col items-center gap-2 group">
              <div className="flex items-center justify-center size-10 rounded-full bg-primary text-[#0a120d] font-bold border-4 border-primary/20">
                1
              </div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-primary">
                File Upload
              </span>
            </div>
            <div className="h-px flex-1 bg-[#254632] mx-4 -mt-6"></div>
            <div className="flex flex-col items-center gap-2 opacity-100">
              <div className="flex items-center justify-center size-10 rounded-full border-2 border-[#254632] text-gray-300 font-bold bg-[#122118]">
                2
              </div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-gray-300">
                File Info
              </span>
            </div>
            <div className="h-px flex-1 bg-[#254632] mx-4 -mt-6"></div>
            <div className="flex flex-col items-center gap-2 opacity-100">
              <div className="flex items-center justify-center size-10 rounded-full border-2 border-[#254632] text-gray-300 font-bold bg-[#122118]">
                3
              </div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-gray-300">
                Parsing
              </span>
            </div>
          </nav>

          {/* Upload Section */}
          <section className="flex flex-col gap-6">
            <div className="flex flex-col gap-1">
              <h3 className="text-xs uppercase tracking-[0.2em] font-bold text-primary">
                Step 1
              </h3>
              <h2 className="text-2xl font-bold tracking-tight text-white">
                Upload CAD Data
              </h2>
            </div>

            {/* Upload Zone */}
            <div
              className={`group relative flex flex-col items-center gap-6 rounded-xl border-2 border-dashed ${dragActive ? 'border-primary bg-[#122118]' : 'border-[#254632] bg-[#122118]/60'
                } hover:border-primary px-6 py-20 transition-all duration-300 cursor-pointer upload-zone-glow`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-upload')?.click()}
            >
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".dxf"
                onChange={handleChange}
              />

              <div className={`size-20 rounded-full ${selectedFile ? 'bg-primary/20 border-primary/40' : 'bg-primary/10 border-primary/20'
                } flex items-center justify-center border group-hover:border-primary/40 transition-all`}>
                <Upload className="text-primary w-12 h-12" />
              </div>

              <div className="flex flex-col items-center gap-2 text-center">
                {selectedFile ? (
                  <>
                    <p className="text-xl font-medium leading-tight text-white">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-gray-300">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • Ready to upload
                    </p>
                  </>
                ) : (
                  <>
                    <p className="text-xl font-medium leading-tight text-white">
                      Drag & drop DXF file here
                    </p>
                    <p className="text-sm text-gray-300">
                      or <span className="text-primary font-bold hover:underline">Browse Files</span> from your device
                    </p>
                  </>
                )}
              </div>

              <div className="flex items-center gap-6 text-[11px] font-bold uppercase tracking-widest text-gray-200 bg-black/40 px-6 py-3 rounded-full border border-[#254632]">
                <span className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-primary" />
                  MAX: 50MB
                </span>
                <span className="w-px h-3 bg-[#254632]"></span>
                <span className="flex items-center gap-2">
                  <Settings className="w-4 h-4 text-primary" />
                  FORMAT: .DXF
                </span>
              </div>
            </div>

            {/* Upload Progress */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Uploading...</span>
                  <span className="text-primary font-bold">{uploadProgress}%</span>
                </div>
                <div className="h-2 bg-[#122118] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Upload Button */}
            {selectedFile && !isUploading && (
              <Button
                onClick={handleUpload}
                className="w-full bg-primary hover:bg-primary/90 text-[#0a120d] font-bold py-6 text-sm uppercase tracking-widest shadow-[0_0_20px_rgba(54,226,123,0.3)]"
              >
                Start Upload
              </Button>
            )}
          </section>

          {/* Info Section */}
          <section className="flex flex-col gap-6">
            <div className="flex flex-col gap-1">
              <h3 className="text-xs uppercase tracking-[0.2em] font-bold text-gray-300">
                Step 2
              </h3>
              <h2 className="text-2xl font-bold tracking-tight text-white/50">
                Verify File Information
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Complete Step 1 to continue
              </p>
            </div>
          </section>
        </div>
      </main>
      {/* Floating Chat Button */}
      <FloatingChatButton />    </div>
  );
}
