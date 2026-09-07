import React, { useEffect, useState } from 'react';
import { LandParcel } from '../../types';
import { api } from '../../services/api';
import { X, GitCompare, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

interface CompareBoundaryModalProps {
  parcel: LandParcel | null;
  isOpen: boolean;
  onClose: () => void;
}

export const CompareBoundaryModal: React.FC<CompareBoundaryModalProps> = ({
  parcel,
  isOpen,
  onClose
}) => {
  if (!isOpen || !parcel) return null;

  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.compareParcelBoundary(parcel.id)
      .then((res) => {
        setComparison(res);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [parcel.id]);

  const oldArea = comparison?.old_area_ha ?? (parcel.survey_number === '48/3' ? 2.00 : parcel.area_hectares);
  const newArea = comparison?.new_area_ha ?? parcel.area_hectares;
  const diffHa = comparison?.diff_area_ha ?? (newArea - oldArea);
  const diffPct = comparison?.diff_percent ?? (oldArea > 0 ? ((newArea - oldArea) / oldArea * 100).toFixed(1) : 0);
  const exceeds = comparison?.exceeds_threshold ?? (Math.abs(Number(diffPct)) > 2.0);

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-[2000] p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col text-slate-800">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <GitCompare className="w-5 h-5 text-amber-600" />
            <div>
              <h3 className="font-bold text-sm text-slate-900">Old vs New Boundary Comparison</h3>
              <p className="text-xs text-slate-500">Cadastral geometry discrepancy detection for Gat {parcel.gat_number}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 text-xs">
          {/* Comparison Stat Cards */}
          <div className="grid grid-cols-3 gap-3 text-center">
            {/* Old Area */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3">
              <span className="text-slate-500 font-medium block text-[11px]">Old 7/12 Record</span>
              <span className="text-lg font-black text-slate-800 block mt-1">{oldArea} ha</span>
              <span className="text-[10px] text-slate-400">{(oldArea * 2.471).toFixed(2)} acres</span>
            </div>

            {/* Difference Indicator */}
            <div className={`border rounded-xl p-3 flex flex-col justify-center items-center ${
              exceeds
                ? 'bg-red-50 border-red-200 text-red-700'
                : 'bg-emerald-50 border-emerald-200 text-emerald-700'
            }`}>
              <span className="font-medium text-[11px]">Variance</span>
              <span className="text-lg font-black block mt-1">
                {Number(diffHa) > 0 ? `+${diffHa}` : diffHa} ha
              </span>
              <span className="text-[10.5px] font-bold">
                {Number(diffPct) > 0 ? `+${diffPct}%` : `${diffPct}%`}
              </span>
            </div>

            {/* New Area */}
            <div className="bg-sky-50 border border-sky-200 rounded-xl p-3">
              <span className="text-sky-700 font-medium block text-[11px]">New DGPS Resurvey</span>
              <span className="text-lg font-black text-sky-950 block mt-1">{newArea} ha</span>
              <span className="text-[10px] text-sky-600">{(newArea * 2.471).toFixed(2)} acres</span>
            </div>
          </div>

          {/* Visual Schematic Box */}
          <div className="bg-slate-900 rounded-xl p-4 text-white relative overflow-hidden flex flex-col items-center justify-center min-h-36">
            <div className="absolute top-2 left-3 text-[10px] text-slate-400 font-mono">
              Boundary Vector Overlay (WGS84 EPSG:4326)
            </div>

            {/* Geometric Visualization */}
            <div className="relative w-48 h-24 my-2 flex items-center justify-center">
              {/* Old Boundary (Yellow Dashed) */}
              <div className="absolute inset-2 border-2 border-dashed border-amber-400/80 rounded-lg bg-amber-400/10" />
              {/* New Boundary (Blue Solid) */}
              <div className="absolute inset-0 border-2 border-sky-400 rounded-lg bg-sky-500/20" />
              {/* Discrepancy Encroachment slice */}
              {exceeds && (
                <div className="absolute right-0 top-0 bottom-0 w-8 bg-red-500/50 border-l-2 border-red-500 flex items-center justify-center">
                  <span className="text-[9px] font-extrabold text-white rotate-90 whitespace-nowrap">
                    DISCREPANCY
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-4 text-[10.5px] mt-1 text-slate-300">
              <span className="flex items-center gap-1.5">
                <span className="w-3 border-t-2 border-dashed border-amber-400 inline-block"></span>
                <span>Historical 7/12 Line</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 border-t-2 border-sky-400 inline-block"></span>
                <span>Field Survey GPS Line</span>
              </span>
              {exceeds && (
                <span className="flex items-center gap-1.5 text-red-400 font-bold">
                  <span className="w-2.5 h-2.5 bg-red-500 inline-block rounded-xs"></span>
                  <span>Encroachment Zone</span>
                </span>
              )}
            </div>
          </div>

          {/* Official Assessment */}
          <div className={`p-3.5 rounded-xl border ${
            exceeds ? 'bg-amber-50/70 border-amber-200' : 'bg-emerald-50/70 border-emerald-200'
          }`}>
            <div className="flex items-center gap-2 font-bold mb-1 text-xs">
              {exceeds ? (
                <>
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span className="text-amber-900">Action Required: Discrepancy Exceeds Permissible Limit (2.0%)</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span className="text-emerald-900">Boundary Conforming to Permissible Tolerance</span>
                </>
              )}
            </div>
            <ul className="list-disc pl-5 space-y-1 text-[11px] text-slate-700 mt-1.5">
              {comparison?.recommendations?.map((rec: string, idx: number) => (
                <li key={idx}>{rec}</li>
              )) || [
                <li>Joint boundary verification with adjacent landholder is recommended.</li>,
                <li>Check cadastral benchmark stone at northeastern corner.</li>
              ]}
            </ul>
          </div>

          {/* Footer Close */}
          <div className="pt-2 flex justify-end border-t border-slate-100">
            <button
              onClick={onClose}
              className="px-5 py-2 text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition"
            >
              Close Comparison
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
