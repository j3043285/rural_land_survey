import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Discrepancy } from '../types';
import { CheckCircle, RefreshCw, Eye, ShieldAlert } from 'lucide-react';
import { CompareBoundaryModal } from '../components/modals/CompareBoundaryModal';

export const Resurvey: React.FC = () => {
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [selectedParcelForCompare, setSelectedParcelForCompare] = useState<any>(null);
  const [resolveId, setResolveId] = useState<number | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadData = () => {
    api.getDiscrepancies()
      .then(setDiscrepancies)
      .catch(console.error)
      .finally(() => {});
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolveId) return;
    setSubmitting(true);
    try {
      await api.resolveDiscrepancy(resolveId, resolutionNotes || 'Boundary verified during joint hearing with adjacent plot holder.');
      setResolveId(null);
      setResolutionNotes('');
      loadData();
    } catch (err: any) {
      alert(`Error resolving: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Resurvey & Boundary Discrepancies
          </h1>
          <p className="text-xs text-slate-500">
            Detected geometric anomalies, area mismatches, and cadastral encroachment hearings
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-semibold text-slate-700 shadow-2xs transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Discrepancies Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden text-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
          <div className="flex items-center gap-2 font-bold text-slate-800">
            <ShieldAlert className="w-4 h-4 text-red-600" />
            <span>Active Boundary Discrepancy Audits ({discrepancies.length})</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Gat / Survey</th>
                <th className="py-2.5 px-4">Owner Name</th>
                <th className="py-2.5 px-4">Village</th>
                <th className="py-2.5 px-4">Discrepancy Type</th>
                <th className="py-2.5 px-4 text-right">Old Area</th>
                <th className="py-2.5 px-4 text-right">New Area</th>
                <th className="py-2.5 px-4 text-right">Deviation</th>
                <th className="py-2.5 px-4 text-center">Status</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {discrepancies.map((d) => {
                const isOpen = d.status === 'Open';
                return (
                  <tr key={d.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 font-bold text-slate-900">
                      Gat {d.gat_number || d.survey_number}
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-medium">{d.owner_name}</td>
                    <td className="py-3 px-4 text-slate-600">{d.village_name || 'Pimpalgaon'}</td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-red-700 bg-red-50 border border-red-200 px-2 py-0.5 rounded text-[10.5px]">
                        {d.discrepancy_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono text-slate-600">{d.old_area_ha} ha</td>
                    <td className="py-3 px-4 text-right font-mono text-slate-900 font-semibold">{d.new_area_ha} ha</td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-red-600">
                      {d.diff_percent > 0 ? `+${d.diff_percent}%` : `${d.diff_percent}%`}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          isOpen ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                        }`}
                      >
                        {d.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => setSelectedParcelForCompare({ id: d.parcel_id, gat_number: d.gat_number, area_hectares: d.new_area_ha })}
                        className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Compare</span>
                      </button>

                      {isOpen && (
                        <button
                          onClick={() => setResolveId(d.id)}
                          className="inline-flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded text-[11px] font-semibold transition"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>Resolve</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Resolve Modal */}
      {resolveId && (
        <div className="fixed inset-0 bg-slate-900/60 flex items-center justify-center z-[2000] p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-5 text-xs space-y-4">
            <h3 className="font-bold text-sm text-slate-900">Resolve Boundary Discrepancy</h3>
            <p className="text-slate-500">Record officer hearing findings and confirm corrected boundary status.</p>
            <form onSubmit={handleResolve} className="space-y-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Resolution & Hearing Notes</label>
                <textarea
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="e.g. Joint ground inspection conducted with adjacent holder. Verified stone markers repositioned according to original 1968 Mojni Map."
                  className="w-full border border-slate-300 rounded-lg p-2 text-slate-800 outline-none"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setResolveId(null)}
                  className="px-3 py-1.5 font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-1.5 rounded-lg shadow-sm"
                >
                  {submitting ? 'Saving...' : 'Confirm Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Comparison Modal */}
      <CompareBoundaryModal
        parcel={selectedParcelForCompare}
        isOpen={Boolean(selectedParcelForCompare)}
        onClose={() => setSelectedParcelForCompare(null)}
      />
    </div>
  );
};
