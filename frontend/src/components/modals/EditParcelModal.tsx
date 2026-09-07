import React, { useState } from 'react';
import { LandParcel } from '../../types';
import { api } from '../../services/api';
import { X, Save, Check } from 'lucide-react';

interface EditParcelModalProps {
  parcel: LandParcel | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdated: (updated: LandParcel) => void;
}

export const EditParcelModal: React.FC<EditParcelModalProps> = ({
  parcel,
  isOpen,
  onClose,
  onUpdated
}) => {
  if (!isOpen || !parcel) return null;

  const [areaHectares, setAreaHectares] = useState(parcel.area_hectares);
  const [landType, setLandType] = useState(parcel.land_type);
  const [boundaryStatus, setBoundaryStatus] = useState(parcel.boundary_status);
  const [remarks, setRemarks] = useState(parcel.remarks || '');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const updated = await api.updateParcel(parcel.id, {
        area_hectares: Number(areaHectares),
        land_type: landType,
        boundary_status: boundaryStatus as any,
        remarks
      });
      setSuccess(true);
      setTimeout(() => {
        onUpdated(updated);
        onClose();
        setSuccess(false);
      }, 600);
    } catch (err: any) {
      alert(`Update failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-[2000] p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden text-slate-800">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Edit Parcel: Gat {parcel.gat_number}</h3>
            <p className="text-xs text-slate-500">Update cadastral details and field survey remarks</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-600 block mb-1">Land Owner</label>
            <input
              type="text"
              disabled
              value={parcel.owner_name || 'Patil Shankar Bapu'}
              className="w-full bg-slate-100 border border-slate-200 rounded-lg px-3 py-2 text-slate-500 font-medium"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-600 block mb-1">Area (Hectares)</label>
              <input
                type="number"
                step="0.01"
                value={areaHectares}
                onChange={(e) => setAreaHectares(Number(e.target.value))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-semibold focus:ring-1 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-600 block mb-1">Area (Acres)</label>
              <input
                type="text"
                disabled
                value={(areaHectares * 2.47105).toFixed(2)}
                className="w-full bg-slate-100 border border-slate-200 rounded-lg px-3 py-2 text-slate-500 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">Land Type</label>
            <select
              value={landType}
              onChange={(e) => setLandType(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="Agricultural (Kharif)">Agricultural (Kharif)</option>
              <option value="Agricultural (Rabi)">Agricultural (Rabi)</option>
              <option value="Horticulture">Horticulture</option>
              <option value="Forest">Forest</option>
              <option value="Barren">Barren</option>
              <option value="Others">Others</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">Boundary Verification Status</label>
            <select
              value={boundaryStatus}
              onChange={(e) => setBoundaryStatus(e.target.value as any)}
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="Verified">Verified</option>
              <option value="In Progress">In Progress</option>
              <option value="Discrepancy">Discrepancy</option>
              <option value="Pending">Pending</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-600 block mb-1">Field Surveyor Remarks</label>
            <textarea
              rows={2}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="e.g. Boundary matched with GPS ground stones."
              className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            />
          </div>

          {/* Buttons */}
          <div className="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition shadow-sm"
            >
              {success ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>Saved!</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>{loading ? 'Saving...' : 'Save Changes'}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
