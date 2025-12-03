import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Calendar, MapPin, CheckCircle2, Globe, Activity, Shield } from 'lucide-react';

export function VaultGrid({ records, onRecordClick }) {
  if (records.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center py-32 text-center border border-dashed border-white/10 rounded-3xl bg-white/5 backdrop-blur-sm"
      >
        <div className="w-24 h-24 bg-white/5 rounded-full flex items-center justify-center mb-6 ring-1 ring-white/10">
          <Shield className="w-10 h-10 text-slate-500" />
        </div>
        <h3 className="text-2xl font-bold text-white mb-3">Your vault is empty</h3>
        <p className="text-slate-400 max-w-sm text-lg">
          Add your first medical record to start building your unified health history.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {records.map((record, idx) => (
        <motion.div
          key={record.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          onClick={() => onRecordClick(record)}
          className="group relative bg-[#0B1121] rounded-3xl p-8 border border-white/5 hover:border-cyan-500/30 transition-all duration-500 hover:shadow-[0_0_40px_rgba(6,182,212,0.1)] overflow-hidden cursor-pointer"
        >
          {/* Glow Effect */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl -mr-32 -mt-32 transition-opacity group-hover:opacity-100 opacity-0" />

          <div className="relative z-10">
            <div className="flex justify-between items-start mb-6">
              <div className={`p-3.5 rounded-2xl transition-all duration-300 ${
                record.type === 'vaccine' 
                  ? 'bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500 group-hover:text-white' 
                  : 'bg-blue-500/10 text-blue-400 group-hover:bg-blue-500 group-hover:text-white'
              }`}>
                {record.type === 'vaccine' ? (
                  <Activity className="w-6 h-6" />
                ) : (
                  <FileText className="w-6 h-6" />
                )}
              </div>
              <span className="text-xs font-bold px-3 py-1.5 bg-white/5 text-slate-300 border border-white/5 rounded-full uppercase tracking-wide">
                {record.origin}
              </span>
            </div>

            <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-200 transition-colors">{record.title}</h3>
            <p className="text-slate-400 mb-6 font-medium">{record.subtitle}</p>

            <div className="space-y-3 text-sm text-slate-400 mb-8">
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-slate-500" />
                <span>{record.date}</span>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="w-4 h-4 text-slate-500" />
                <span>{record.location}</span>
              </div>
              {record.language !== 'English' && (
                <div className="flex items-center gap-3 text-cyan-400/80">
                  <Globe className="w-4 h-4" />
                  <span>Translated from {record.language}</span>
                </div>
              )}
            </div>

            <div className="pt-6 border-t border-white/5 flex items-center justify-between">
              <div className="flex -space-x-3">
                {record.items.slice(0, 3).map((item, i) => (
                  <div key={i} className="w-9 h-9 rounded-full bg-[#111827] border-2 border-[#0B1121] flex items-center justify-center text-[10px] font-bold text-slate-300 ring-1 ring-white/10" title={item}>
                    {item.substring(0, 2)}
                  </div>
                ))}
                {record.items.length > 3 && (
                  <div className="w-9 h-9 rounded-full bg-[#111827] border-2 border-[#0B1121] flex items-center justify-center text-[10px] text-slate-500 ring-1 ring-white/10">
                    +{record.items.length - 3}
                  </div>
                )}
              </div>
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 bg-emerald-500/10 px-2 py-1 rounded-lg border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Digitized
              </span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
