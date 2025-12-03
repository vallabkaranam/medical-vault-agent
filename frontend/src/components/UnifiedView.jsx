import React from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid, FileText } from 'lucide-react';
import { api } from '../api';

export function UnifiedView({ 
  records, 
  handleRecordClick, 
  setViewMode, 
  selectedStandard, 
  setSelectedStandard, 
  setStandardizationResult, 
  setSelectedRecord 
}) {
  
  const handleGenerateReport = async () => {
    try {
      const report = await api.generateSessionReport(selectedStandard);
      setStandardizationResult(report);
      // Open a "Report View"
      setSelectedRecord({ 
        title: `${selectedStandard.replace('_', ' ').toUpperCase()} Compliance Report`,
        subtitle: `Generated on ${new Date().toLocaleDateString()}`,
        type: 'report',
        original_file: null, // No single file
        raw_data: null // We use standardizationResult directly
      });
    } catch (e) {
      console.error("Report generation failed", e);
      alert("Failed to generate report. Please try again.");
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
       <div className="flex items-center justify-between mb-6">
         <h2 className="text-3xl font-bold text-white">Unified Immunization History</h2>
         <div className="flex gap-3">
           <div className="flex items-center gap-2 bg-white/5 rounded-lg p-1 border border-white/10">
              <span className="text-sm text-slate-400 px-2">Format:</span>
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
              onClick={handleGenerateReport}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-cyan-900/20"
           >
             <FileText className="w-4 h-4" />
             Generate Report
           </button>
           <button 
              onClick={() => setViewMode('vault')}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 text-slate-300 rounded-lg border border-white/10 transition-colors flex items-center gap-2"
           >
             <LayoutGrid className="w-4 h-4" />
             Back to Vault
           </button>
         </div>
       </div>

       <div className="bg-[#0B1121] border border-white/10 rounded-3xl p-8 overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 text-sm uppercase tracking-wider">
                <th className="pb-4 font-medium">Vaccine</th>
                <th className="pb-4 font-medium">Date</th>
                <th className="pb-4 font-medium">Origin</th>
                <th className="pb-4 font-medium">Source Document</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {records.flatMap(r => r.items.map((item, idx) => (
                <tr key={`${r.id}-${idx}`} className="group hover:bg-white/5 transition-colors">
                  <td className="py-4 text-white font-medium">{item}</td>
                  <td className="py-4 text-slate-400">{r.date}</td>
                  <td className="py-4">
                    <span className="px-2 py-1 rounded-full bg-white/5 text-xs text-slate-300 border border-white/5">
                      {r.origin}
                    </span>
                  </td>
                  <td className="py-4 text-cyan-400 text-sm cursor-pointer hover:underline" onClick={() => handleRecordClick(r)}>
                    {r.title}
                  </td>
                </tr>
              )))}
            </tbody>
          </table>
          {records.length === 0 && (
            <div className="text-center py-12 text-slate-500">
              No records found. Upload a document to populate your history.
            </div>
          )}
       </div>
    </motion.div>
  );
}
