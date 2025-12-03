import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadZone } from './components/UploadZone';
import { ScanningOverlay } from './components/ScanningOverlay';
import { VaultGrid } from './components/VaultGrid';
import { UnifiedView } from './components/UnifiedView';
import { DetailModal } from './components/DetailModal';
import { ShieldCheck, Plus, CheckCircle2, Activity, Lock, List, LayoutGrid } from 'lucide-react';
import { api } from './api';

function App() {
  const [records, setRecords] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [scanImage, setScanImage] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [standardizationResult, setStandardizationResult] = useState(null);
  const [selectedStandard, setSelectedStandard] = useState('cornell_tech');
  const [viewMode, setViewMode] = useState('vault'); // 'vault' or 'unified'

  // Load records on mount
  useEffect(() => {
    loadRecords();
  }, []);

  const loadRecords = async () => {
    try {
      const data = await api.getSessionRecords();
      // Transform backend data to frontend format if needed, or just use as is
      // For now, let's map it to match our UI expectations
      const mappedRecords = data.map(r => ({
        id: r.record_id,
        type: 'vaccine', // Default for now
        title: 'Vaccination Record',
        subtitle: `Uploaded ${new Date(r.uploaded_at).toLocaleDateString()}`,
        date: r.transcription.structured_data?.dates?.[0] || new Date().toISOString().split('T')[0],
        location: 'Unknown Location', // AI could extract this
        origin: r.transcription.detected_language === 'en' ? 'USA' : 'International',
        language: r.transcription.detected_language,
        items: r.extracted_vaccines.map(v => v.vaccine_name),
        original_file: r.image_url,
        raw_data: r // Keep full data for detail view
      }));
      setRecords(mappedRecords);
    } catch (error) {
      console.error("Failed to load records:", error);
    }
  };

  const handleFileSelect = async (file) => {
    setShowUpload(false);
    setScanImage(URL.createObjectURL(file));
    setIsScanning(true);

    try {
      // 1. Upload to Backend
      const uploadResult = await api.uploadRecord(file);
      
      // 2. Wait a bit for the "Scanning" effect (UX)
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setIsScanning(false);
      setScanImage(null);
      
      // 3. Reload records
      await loadRecords();
      
    } catch (error) {
      console.error("Upload failed:", error);
      setIsScanning(false);
      alert("Upload failed. Please try again.");
    }
  };

  const handleRecordClick = async (record) => {
    setSelectedRecord(record);
    // Reset previous standardization result when opening new record
    setStandardizationResult(null);
    
    // Auto-standardize on open (or we could wait for user action)
    // Let's wait for user action in the modal to simulate "Verify against X"
  };

  const handleVerify = async () => {
    if (!selectedRecord) return;
    
    try {
      const result = await api.standardizeRecord(selectedRecord.id, selectedStandard);
      setStandardizationResult(result);
    } catch (error) {
      console.error("Verification failed:", error);
    }
  };

  return (
    <div className="min-h-screen font-sans text-slate-200 selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-40 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => {setSelectedRecord(null); setViewMode('vault');}}>
            <div className="w-10 h-10 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <span className="font-bold text-xl tracking-tight text-white">Personal Vault</span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-2 text-sm font-medium text-slate-400 bg-white/5 px-4 py-2 rounded-full border border-white/5">
              <Lock className="w-3.5 h-3.5" />
              <span>{records.length} Records Secured</span>
            </div>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 ring-2 ring-white/10" />
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-32 pb-20">
        
        {/* Hero Section (Only show on Vault View) */}
        {!selectedRecord && viewMode === 'vault' && (
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16">
            <div className="space-y-4 max-w-3xl">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2"
              >
                <Activity className="w-3 h-3" />
                <span>AI-Powered Compliance</span>
              </motion.div>
              
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-5xl md:text-7xl font-extrabold text-white tracking-tight leading-[1.1]"
              >
                Global Health History. <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 animate-gradient-x">
                  Unified & Verified.
                </span>
              </motion.h1>
              
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-xl text-slate-400 max-w-2xl leading-relaxed"
              >
                Securely aggregate your fragmented medical records from around the world into one standardized digital vault.
              </motion.p>
            </div>

            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="flex gap-4"
            >
              <button 
                onClick={() => setViewMode(viewMode === 'vault' ? 'unified' : 'vault')}
                className="glass-button px-8 py-4 text-slate-200 font-semibold rounded-2xl flex items-center gap-3 hover:text-white group"
              >
                {viewMode === 'vault' ? <List className="w-5 h-5" /> : <LayoutGrid className="w-5 h-5" />}
                {viewMode === 'vault' ? 'Unified View' : 'Vault View'}
              </button>
              <button 
                onClick={() => setShowUpload(true)}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-2xl hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] transition-all flex items-center gap-3 hover:scale-105 active:scale-95"
              >
                <Plus className="w-5 h-5" />
                Add Record
              </button>
            </motion.div>
          </div>
        )}

        {/* Unified View */}
        {viewMode === 'unified' && !selectedRecord && (
          <UnifiedView 
            records={records}
            handleRecordClick={handleRecordClick}
            setViewMode={setViewMode}
            selectedStandard={selectedStandard}
            setSelectedStandard={setSelectedStandard}
            setStandardizationResult={setStandardizationResult}
            setSelectedRecord={setSelectedRecord}
          />
        )}

        {/* Vault Grid View */}
        {viewMode === 'vault' && !selectedRecord && (
          <VaultGrid records={records} onRecordClick={handleRecordClick} />
        )}

        {/* Footer with Trust Signals */}
        {!selectedRecord && (
          <div className="mt-20 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 text-slate-500 text-sm">
            <div className="flex items-center gap-6">
              <span className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-500/50" />
                HIPAA Compliant
              </span>
              <span className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-emerald-500/50" />
                End-to-End Encrypted
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500/50" />
                SOC2 Type II Ready
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2 text-xs font-mono text-emerald-500/80 bg-emerald-500/5 px-3 py-1 rounded-full border border-emerald-500/10">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                SYSTEM ONLINE
              </div>
            </div>
            <div>
              © 2025 Personal Vault Inc.
            </div>
          </div>
        )}

      </main>

      {/* Record Detail View (Modal/Overlay) */}
      <AnimatePresence>
        {selectedRecord && (
          <DetailModal 
            selectedRecord={selectedRecord}
            setSelectedRecord={setSelectedRecord}
            selectedStandard={selectedStandard}
            setSelectedStandard={setSelectedStandard}
            handleVerify={handleVerify}
            standardizationResult={standardizationResult}
          />
        )}
      </AnimatePresence>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUpload && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
            onClick={() => setShowUpload(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl"
            >
              <UploadZone onFileSelect={handleFileSelect} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scanning Overlay */}
      {isScanning && (
        <ScanningOverlay imageSrc={scanImage} />
      )}

    </div>
  );
}

export default App;
