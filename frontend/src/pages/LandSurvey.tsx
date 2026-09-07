import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LandParcel } from '../types';
import { Plus, CheckCircle, Navigation } from 'lucide-react';

export const LandSurvey: React.FC = () => {
  const [parcels, setParcels] = useState<LandParcel[]>([]);
  const [selectedParcelId, setSelectedParcelId] = useState<number | null>(null);
  const [newArea, setNewArea] = useState<number>(1.82);
  const [remarks, setRemarks] = useState('');
  const [points, setPoints] = useState<Array<{ order: number; lat: number; lng: number }>>([
    { order: 1, lat: 19.1215, lng: 74.4305 },
    { order: 2, lat: 19.1228, lng: 74.4338 },
    { order: 3, lat: 19.1252, lng: 74.4322 },
    { order: 4, lat: 19.1238, lng: 74.4290 }
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [createdSurvey, setCreatedSurvey] = useState<any>(null);

  useEffect(() => {
    api.getParcels(1).then((data) => {
      setParcels(data);
      if (data.length > 0) {
        setSelectedParcelId(data[0].id);
        setNewArea(data[0].area_hectares);
      }
    });
  }, []);

  const handleParcelChange = (id: number) => {
    setSelectedParcelId(id);
    const p = parcels.find((item) => item.id === id);
    if (p) setNewArea(p.area_hectares);
  };

  const addPoint = () => {
    const last = points[points.length - 1];
    setPoints([
      ...points,
      {
        order: points.length + 1,
        lat: Number((last.lat + 0.0005).toFixed(5)),
        lng: Number((last.lng + 0.0005).toFixed(5))
      }
    ]);
  };

  const handleStartSurvey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedParcelId) return;
    const p = parcels.find((item) => item.id === selectedParcelId);
    if (!p) return;

    setSubmitting(true);
    try {
      const res = await api.createSurvey({
        parcel_id: p.id,
        old_area_hectares: p.area_hectares,
        new_area_hectares: Number(newArea),
        surveyor_remarks: remarks || 'Field survey completed using RTK DGPS receiver.',
        gps_accuracy_meters: 0.45,
        points: points.map((pt) => ({
          point_order: pt.order,
          latitude: pt.lat,
          longitude: pt.lng,
          point_type: 'Boundary Corner Pillar'
        }))
      });
      setCreatedSurvey(res);
    } catch (err: any) {
      alert(`Error creating survey: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const selectedParcel = parcels.find((p) => p.id === selectedParcelId);

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Land Survey & Resurvey Workflow</h1>
        <p className="text-xs text-slate-500">Record cadastral boundary points, ground markers, and initiate verification</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Form */}
        <div className="md:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
          <form onSubmit={handleStartSurvey} className="space-y-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Select Parcel for Survey</label>
              <select
                value={selectedParcelId || ''}
                onChange={(e) => handleParcelChange(Number(e.target.value))}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium"
              >
                {parcels.map((p) => (
                  <option key={p.id} value={p.id}>
                    Gat {p.gat_number} - {p.owner_name} ({p.area_hectares} ha)
                  </option>
                ))}
              </select>
            </div>

            {selectedParcel && (
              <div className="grid grid-cols-3 gap-3 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[10px]">Village</span>
                  <span className="font-bold text-slate-800">{selectedParcel.village_name || 'Pimpalgaon'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Current Area</span>
                  <span className="font-bold text-slate-800">{selectedParcel.area_hectares} ha</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Khata No.</span>
                  <span className="font-bold text-slate-800">{selectedParcel.khata_number}</span>
                </div>
              </div>
            )}

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Resurveyed Area (Hectares)</label>
              <input
                type="number"
                step="0.01"
                value={newArea}
                onChange={(e) => setNewArea(Number(e.target.value))}
                className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 font-bold text-slate-900"
              />
            </div>

            {/* GPS Ground Control Points */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="font-semibold text-slate-700">DGPS Boundary Points Captured</label>
                <button
                  type="button"
                  onClick={addPoint}
                  className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold text-[11px]"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add GPS Point</span>
                </button>
              </div>

              <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
                {points.map((pt, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 text-[11px] bg-slate-50/50">
                    <span className="font-bold text-slate-700">Pillar #{pt.order}</span>
                    <span className="font-mono text-slate-600">Lat: {pt.lat}</span>
                    <span className="font-mono text-slate-600">Lng: {pt.lng}</span>
                    <span className="text-emerald-600 font-semibold">± 0.45m</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Survey Remarks</label>
              <textarea
                rows={2}
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Field inspection remarks, adjacent neighbor consent, crop condition..."
                className="w-full border border-slate-300 rounded-lg p-2.5 text-slate-800 outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl font-bold text-xs transition shadow-sm"
            >
              {submitting ? 'Recording Field Survey...' : 'Save & Submit Field Survey'}
            </button>
          </form>
        </div>

        {/* Right Info Box */}
        <div className="space-y-4">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 text-xs space-y-3">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-blue-600" />
              <span>DGPS Device Status</span>
            </h3>
            <p className="text-slate-500">Connected to Maharashtra RTK CORS Network (Yeola Base Station).</p>
            <div className="space-y-1.5 pt-2 border-t border-slate-100">
              <div className="flex justify-between"><span className="text-slate-500">Receiver:</span> <b className="text-slate-800">Dual Frequency L1/L5</b></div>
              <div className="flex justify-between"><span className="text-slate-500">Horizontal RMS:</span> <b className="text-emerald-700">0.008 m</b></div>
              <div className="flex justify-between"><span className="text-slate-500">Satellites:</span> <b className="text-slate-800">28 (GPS + NavIC)</b></div>
              <div className="flex justify-between"><span className="text-slate-500">Fix Mode:</span> <b className="text-blue-700 font-mono">RTK FIX (Fixed)</b></div>
            </div>
          </div>

          {createdSurvey && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 text-xs space-y-2">
              <div className="flex items-center gap-2 font-bold text-emerald-900">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Survey Recorded Successfully!</span>
              </div>
              <p className="text-emerald-800">
                Survey Number: <b>{createdSurvey.survey_number}</b>
              </p>
              <p className="text-[11px] text-emerald-700">
                Forwarded to Circle Officer / Verifier for digital review and Bhu-Aadhaar certificate generation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
