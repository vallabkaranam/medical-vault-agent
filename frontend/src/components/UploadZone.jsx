import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, Image as ImageIcon } from 'lucide-react';
import { motion } from 'framer-motion';

export function UploadZone({ onFileSelect }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles?.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  return (
    <div className="w-full">
      <div className="bg-[#0B1121] border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Upload Record</h2>
          <p className="text-slate-400">
            We support JPG, PNG, and PDF files up to 10MB.
          </p>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`
            relative group cursor-pointer
            border-2 border-dashed rounded-2xl p-12
            transition-all duration-300 ease-in-out
            flex flex-col items-center justify-center gap-4
            ${isDragActive 
              ? 'border-cyan-500 bg-cyan-500/10 scale-[1.02]' 
              : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
            }
          `}
        >
          <input {...getInputProps()} />
          
          <div className={`
            w-20 h-20 rounded-full flex items-center justify-center
            transition-all duration-300
            ${isDragActive ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30' : 'bg-[#111827] text-slate-400 group-hover:text-white group-hover:scale-110'}
          `}>
            <UploadCloud className="w-10 h-10" />
          </div>

          <div className="text-center space-y-1">
            <p className="text-lg font-semibold text-white">
              {isDragActive ? 'Drop it like it\'s hot!' : 'Click or drag file here'}
            </p>
            <p className="text-sm text-slate-500">
              Securely encrypted & processed locally
            </p>
          </div>
        </div>

        {/* Supported Types */}
        <div className="mt-8 flex justify-center gap-8">
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <ImageIcon className="w-4 h-4" />
            <span>High-Res Images</span>
          </div>
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <File className="w-4 h-4" />
            <span>PDF Documents</span>
          </div>
        </div>

      </div>
    </div>
  );
}
