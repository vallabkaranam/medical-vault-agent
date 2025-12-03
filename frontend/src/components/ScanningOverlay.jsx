import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scan, Sparkles, CheckCircle2, Globe, FileSearch, Cpu } from 'lucide-react';

const STEPS = [
  { text: "Classifying Document Type...", icon: Scan, color: "text-blue-400" },
  { text: "Digitizing Handwriting...", icon: FileSearch, color: "text-cyan-400" },
  { text: "Translating to English (US Standard)...", icon: Globe, color: "text-purple-400" },
  { text: "Standardizing Units (ml → cc)...", icon: Sparkles, color: "text-pink-400" },
  { text: "Verifying Compliance...", icon: CheckCircle2, color: "text-emerald-400" },
];

export function ScanningOverlay({ imageSrc }) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % STEPS.length);
    }, 800);
    return () => clearInterval(interval);
  }, []);

  const CurrentIcon = STEPS[currentStep].icon;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[#030712]/95 backdrop-blur-xl">
      <div className="relative w-full max-w-4xl p-8 flex flex-col items-center">
        
        {/* Scanning Container */}
        <div className="relative w-full max-w-md aspect-[3/4] bg-[#0B1121] rounded-3xl overflow-hidden shadow-2xl border border-cyan-500/30 ring-4 ring-cyan-500/10">
          {/* Image being scanned */}
          <img 
            src={imageSrc} 
            alt="Scanning..." 
            className="w-full h-full object-cover opacity-40 grayscale mix-blend-luminosity"
          />
          
          {/* Laser Beam */}
          <motion.div
            initial={{ top: "-10%" }}
            animate={{ top: "110%" }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              ease: "linear" 
            }}
            className="absolute left-0 right-0 h-2 bg-cyan-400 shadow-[0_0_50px_rgba(34,211,238,1)] z-10"
          >
            <div className="absolute inset-0 bg-white/50 blur-sm" />
          </motion.div>
          
          {/* Grid Overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.1)_1px,transparent_1px)] bg-[size:40px_40px]" />
          
          {/* Corner Accents */}
          <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-500 rounded-tl-lg" />
          <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-500 rounded-tr-lg" />
          <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-500 rounded-bl-lg" />
          <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-500 rounded-br-lg" />
        </div>

        {/* Status Text */}
        <div className="mt-16 h-32 flex flex-col items-center justify-center w-full max-w-lg">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              className="flex flex-col items-center gap-6 text-center"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full animate-pulse" />
                <div className="relative p-5 bg-[#111827] rounded-2xl border border-white/10 shadow-xl">
                  <CurrentIcon className={`w-10 h-10 ${STEPS[currentStep].color}`} />
                </div>
              </div>
              
              <div className="space-y-2">
                <span className="text-3xl font-bold text-white tracking-tight block">
                  {STEPS[currentStep].text}
                </span>
                <div className="flex items-center justify-center gap-2 text-slate-400 text-sm font-mono">
                  <Cpu className="w-4 h-4" />
                  <span>AI PROCESSING NODE 01</span>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
          
          <div className="mt-10 flex gap-3">
            {STEPS.map((_, idx) => (
              <div 
                key={idx}
                className={`h-1.5 rounded-full transition-all duration-500 ease-out ${
                  idx <= currentStep 
                    ? 'w-16 bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.6)]' 
                    : 'w-2 bg-white/10'
                }`}
              />
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
