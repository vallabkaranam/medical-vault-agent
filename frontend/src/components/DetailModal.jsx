import React from 'react';
import { motion } from 'framer-motion';
import { X, Building2, Activity } from 'lucide-react';
import { CornellComplianceForm } from './CornellComplianceForm';

export function DetailModal({
  selectedRecord,
  setSelectedRecord,
  selectedStandard,
  setSelectedStandard,
  handleVerify,
  standardizationResult
}) {
  if (!selectedRecord) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="fixed inset-0 z-50 bg-[#030712] overflow-y-auto"
    >
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Detail Header */}
        <div className="flex justify-between items-center mb-8 sticky top-0 bg-[#030712]/90 backdrop-blur-xl py-4 z-10 border-b border-white/5">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSelectedRecord(null)}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <X className="w-6 h-6 text-slate-400" />
            </button>
            <div>
              <h2 className="text-2xl font-bold text-white">{selectedRecord.title}</h2>
              <p className="text-slate-400 text-sm">{selectedRecord.subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1 border border-white/10">
              <span className="text-sm text-slate-400 px-2">Verify against:</span>
              <select 
                value={selectedStandard}
                onChange={(e) => setSelectedStandard(e.target.value)}
                className="bg-transparent text-white text-sm font-medium focus:outline-none cursor-pointer"
              >
                <option value="cornell_tech">Cornell Tech</option>
                <option value="us_cdc">US CDC</option>
                <option value="uk_nhs">UK NHS</option>
              </select>
            </div>
            
            <button 
              onClick={handleVerify}
              className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-xl transition-colors flex items-center gap-2 shadow-lg shadow-cyan-900/20"
            >
              <Building2 className="w-4 h-4" />
              Verify Compliance
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-140px)]">
          {/* Left: Original Document (Only if NOT a report) */}
          {selectedRecord.type !== 'report' && (
            <div className="bg-[#0B1121] rounded-3xl border border-white/10 p-6 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">Original Document</span>
                <span className="px-2 py-1 bg-white/5 rounded text-xs text-slate-500">{selectedRecord.original_file.split('/').pop()}</span>
              </div>
              <div className="flex-1 bg-[#030712] rounded-2xl border border-white/5 overflow-hidden relative group">
                 <img 
                  src={selectedRecord.original_file} 
                  alt="Original" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}

          {/* Right: Extracted Data & Compliance (Full width if report) */}
          <div className={`${selectedRecord.type === 'report' ? 'col-span-2' : ''} bg-[#0B1121] rounded-3xl border border-white/10 p-6 flex flex-col overflow-y-auto custom-scrollbar`}>
            
            {/* Special Report View for Cornell Tech */}
            {selectedRecord.type === 'report' && selectedStandard === 'cornell_tech' ? (
              <CornellComplianceForm data={standardizationResult} />
            ) : (
              <>
                <div className="flex justify-between items-center mb-6">
                  <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">
                    {selectedRecord.type === 'report' ? 'Official Compliance Report' : 'Extracted Data'}
                  </span>
                  {standardizationResult && (
                      <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                        standardizationResult.is_compliant 
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {standardizationResult.is_compliant ? 'COMPLIANT' : 'NON-COMPLIANT'}
                      </span>
                  )}
                </div>

                {standardizationResult ? (
                  <div className="space-y-6">
                    {/* Compliance Result View */}
                    <div className="space-y-4">
                      {standardizationResult.records.map((rec, idx) => (
                        <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/5">
                          <div className="flex justify-between mb-2">
                            <h4 className="font-bold text-white">{rec.vaccine_name}</h4>
                            <span className="text-xs text-slate-400">{rec.date}</span>
                          </div>
                          <p className="text-sm text-slate-500 font-mono">"{rec.original_text}"</p>
                        </div>
                      ))}
                    </div>

                    {!standardizationResult.is_compliant && (
                      <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                        <h4 className="font-bold text-amber-400 mb-2 text-sm">Missing Requirements</h4>
                        <ul className="list-disc list-inside text-sm text-amber-200/70">
                          {standardizationResult.missing_vaccines.map((v, i) => (
                            <li key={i}>{v}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Raw Extraction View (Before Verification) */}
                    <div className="p-4 bg-cyan-500/5 border border-cyan-500/10 rounded-xl mb-6">
                      <p className="text-sm text-cyan-200/80">
                        <Activity className="w-4 h-4 inline mr-2" />
                        AI has extracted the following data. Click "Verify Compliance" to validate against {selectedStandard.replace('_', ' ')}.
                      </p>
                    </div>
                    
                    {selectedRecord.raw_data.extracted_vaccines.map((vax, idx) => (
                        <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/5">
                          <div className="flex justify-between mb-2">
                            <h4 className="font-bold text-white">{vax.vaccine_name}</h4>
                            <span className="text-xs text-slate-400">{vax.date}</span>
                          </div>
                          <p className="text-sm text-slate-500 font-mono">"{vax.original_text}"</p>
                        </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
