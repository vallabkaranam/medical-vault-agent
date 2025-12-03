import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Eye, Download, Share2, Shield } from 'lucide-react';
import { clsx } from 'clsx';

export function ResultCard({ data, imageSrc, standard }) {
  const isCompliant = data.is_compliant;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-6xl mx-auto bg-[#0B1121] rounded-3xl shadow-2xl overflow-hidden border border-white/10"
    >
      {/* Header */}
      <div className="bg-white/5 border-b border-white/10 p-6 flex justify-between items-center backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <div className={clsx(
            "px-4 py-1.5 rounded-full text-sm font-bold flex items-center gap-2 border",
            isCompliant 
              ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
              : "bg-amber-500/10 text-amber-400 border-amber-500/20"
          )}>
            {isCompliant ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            {isCompliant ? "VERIFIED COMPLIANT" : "ACTION NEEDED"}
          </div>
          <span className="text-slate-400 text-sm font-medium flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Standard: <span className="text-white">{standard.replace('_', ' ').toUpperCase()}</span>
          </span>
        </div>
        
        <div className="flex gap-2">
          <button className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
            <Download className="w-5 h-5" />
          </button>
          <button className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row h-[600px]">
        
        {/* Left: Digital Record */}
        <div className="flex-1 p-8 overflow-y-auto custom-scrollbar">
          <h3 className="text-2xl font-bold text-white mb-6">Digital Record</h3>
          
          <div className="space-y-4">
            {data.records.map((record, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-cyan-500/30 transition-all group"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-bold text-white text-lg group-hover:text-cyan-200 transition-colors">{record.vaccine_name}</h4>
                    <p className="text-sm text-slate-400">Administered: {record.date_administered}</p>
                  </div>
                  <span className={clsx(
                    "px-2 py-1 rounded text-xs font-semibold border",
                    record.status === "Compliant" 
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                      : "bg-red-500/10 text-red-400 border-red-500/20"
                  )}>
                    {record.status}
                  </span>
                </div>
                
                <div className="mt-3 pt-3 border-t border-white/5">
                  <p className="text-xs text-slate-500 font-mono flex items-center gap-2">
                    <Eye className="w-3 h-3" />
                    Detected: "{record.original_text}"
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {!isCompliant && (
             <div className="mt-8 p-6 bg-amber-500/5 rounded-xl border border-amber-500/20">
               <h4 className="font-bold text-amber-400 mb-3 flex items-center gap-2">
                 <AlertCircle className="w-5 h-5" />
                 Missing Requirements
               </h4>
               <ul className="list-disc list-inside text-sm text-amber-200/80 space-y-2 ml-2">
                 <li>Hepatitis B (Dose 2)</li>
                 <li>Meningococcal ACWY</li>
               </ul>
             </div>
          )}
        </div>

        {/* Right: Original Document */}
        <div className="w-full lg:w-[45%] bg-[#030712] p-8 flex flex-col relative border-l border-white/10">
          <div className="absolute top-6 right-6 z-10">
             <span className="bg-black/60 backdrop-blur-md border border-white/10 text-white text-xs px-3 py-1.5 rounded-full font-medium">
               Original Document
             </span>
          </div>
          
          <div className="flex-1 flex items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-[#0B1121] relative group">
            <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(6,182,212,0.05)_50%,transparent_75%,transparent_100%)] bg-[length:250%_250%] animate-[shimmer_3s_infinite]" />
            <img 
              src={imageSrc} 
              alt="Original" 
              className="max-w-full max-h-full object-contain opacity-90 group-hover:opacity-100 transition-opacity"
            />
          </div>
        </div>

      </div>
    </motion.div>
  );
}
