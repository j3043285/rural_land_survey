import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { LandParcel } from '../types';
import { Compass, Crosshair, CheckCircle } from 'lucide-react';

export const FieldSurvey: React.FC = () => {
  const [searchParams] = useSearchParams();
  const villageId = Number(searchParams.get('village_id')) || 1;
  const [parcels, setParcels] = useState<LandParcel[]>([]);
  const [selectedParcelId, setSelectedParcelId] = useState<number | null>(null);
  const [currentGps, setCurrentGps] = useState<{ lat: number; lng: number; accuracy: number }>({
    lat: 19.1234,
    lng: 74.4321,
    accuracy: 0.45
  });
  const [capturedPoints, setCapturedPoints] = useState<Array<{ id: number; lat: number; lng: number }>>([]);
  const [surveyorRemarks, setSurveyorRemarks] = useState('');
  const [isCapturing, setIsCapturing] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    api.getParcels(villageId).then((data) => {
      setParcels(data);
      if (data.length > 0) setSelectedParcelId(data[0].id);
    });

    // Attempt browser GPS if permitted
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setCurrentGps({
            lat: Number(pos.coords.latitude.toFixed(5)),
            lng: Number(pos.coords.longitude.toFixed(5)),
            accuracy: Number(pos.coords.accuracy.toFixed(1))
          });
        },
        () => {
          // Keep calibrated demo coordinates
        }
      );
    }
  }, [villageId]);

  const handleCapturePoint = () => {
    setIsCapturing(true);
    setTimeout(() => {
      setCapturedPoints((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          lat: currentGps.lat + (prev.length * 0.0004),
          lng: currentGps.lng + (prev.length * 0.0004)
        }
      ]);
      setIsCapturing(false);
    }, 400);
  };

  const handleSubmitSurvey = async () => {
    if (!selectedParcelId) return;
    const p = parcels.find((item) => item.id === selectedParcelId);
    if (!p) return;

    try {
      await api.createSurvey({
        parcel_id: p.id,
        old_area_hectares: p.area_hectares,
        new_area_hectares: p.area_hectares,
        surveyor_remarks: surveyorRemarks || 'Field DGPS survey completed with RTK rover.',
        gps_accuracy_meters: currentGps.accuracy,
        points: capturedPoints.map((pt) => ({
          point_order: pt.id,
          latitude: pt.lat,
          longitude: pt.lng,
          point_type: 'Boundary Corner'
        }))
      });
      setSubmitted(true);
    } catch (err: any) {
      alert(`Error submitting field survey: ${err.message}`);
    }
  };

  return (
    <div className="p-4 md:p-6 max-w-2xl mx-auto space-y-5 text-xs">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Compass className="w-5 h-5 text-blue-600" />
            <span>Field Surveyor Mobile Tool</span>
          </h1>
          <p className="text-slate-500">Live GPS capture & ground boundary survey</p>
        </div>
        <div className="flex items-center gap-1.5 bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200 font-semibold">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>DGPS RTK Ready</span>
        </div>
      </div>

      {/* Live GPS Telemetry Card */}
      <div className="bg-[#0b1e36] text-white p-5 rounded-2xl shadow-lg border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-slate-400 font-medium">Receiver Position (WGS84)</span>
          <span className="text-emerald-400 font-mono text-[11px]">Accuracy: ± {currentGps.accuracy}m</span>
        </div>

        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="bg-[#122847] p-3 rounded-xl border border-sky-900/60">
            <span className="text-slate-400 text-[10px] block">Latitude</span>
            <span className="text-lg font-mono font-black text-sky-400 mt-0.5 block">{currentGps.lat}° N</span>
          </div>
          <div className="bg-[#122847] p-3 rounded-xl border border-sky-900/60">
            <span className="text-slate-400 text-[10px] block">Longitude</span>
            <span className="text-lg font-mono font-black text-sky-400 mt-0.5 block">{currentGps.lng}° E</span>
          </div>
        </div>

        <button
          onClick={handleCapturePoint}
          disabled={isCapturing}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl shadow-md transition text-xs"
        >
          <Crosshair className="w-4 h-4" />
          <span>{isCapturing ? 'Recording GPS Position...' : 'Record Current Corner Pillar Point'}</span>
        </button>
      </div>

      {/* Parcel Selector */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-slate-200 space-y-4">
        <div>
          <label className="font-semibold text-slate-700 block mb-1">Select Target Parcel</label>
          <select
            value={selectedParcelId || ''}
            onChange={(e) => setSelectedParcelId(Number(e.target.value))}
            className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-800 font-medium outline-none"
          >
            {parcels.map((p) => (
              <option key={p.id} value={p.id}>
                Gat {p.gat_number} • {p.owner_name} ({p.area_hectares} ha)
              </option>
            ))}
          </select>
        </div>

        {/* Captured Points List */}
        <div>
          <div className="flex justify-between items-center mb-1.5 font-semibold text-slate-700">
            <span>Captured Boundary Pillars ({capturedPoints.length})</span>
            {capturedPoints.length > 0 && (
              <button
                onClick={() => setCapturedPoints([])}
                className="text-red-600 text-[11px] hover:underline"
              >
                Clear All
              </button>
            )}
          </div>

          {capturedPoints.length === 0 ? (
            <p className="text-slate-400 text-center py-4 bg-slate-50 rounded-xl border border-dashed border-slate-200">
              No boundary points recorded yet. Stand at parcel corner and click "Record Current Corner".
            </p>
          ) : (
            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {capturedPoints.map((pt) => (
                <div key={pt.id} className="flex items-center justify-between p-2 bg-slate-50 rounded-lg border border-slate-100">
                  <span className="font-bold text-slate-800">Corner #{pt.id}</span>
                  <span className="font-mono text-slate-600">{pt.lat}, {pt.lng}</span>
                  <span className="text-emerald-600 font-medium">Logged</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="font-semibold text-slate-700 block mb-1">Field Surveyor Remarks</label>
          <textarea
            rows={2}
            value={surveyorRemarks}
            onChange={(e) => setSurveyorRemarks(e.target.value)}
            placeholder="Ground survey observations, physical boundaries, bund markers..."
            className="w-full border border-slate-300 rounded-lg p-2 text-slate-800 outline-none"
          />
        </div>

        {submitted ? (
          <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-xl flex items-center gap-2 text-emerald-800 font-bold">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <span>Field survey submitted to Verifier for digital sign-off!</span>
          </div>
        ) : (
          <button
            onClick={handleSubmitSurvey}
            disabled={capturedPoints.length === 0}
            className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold py-2.5 rounded-xl shadow-sm transition"
          >
            Submit Survey to Circle Officer
          </button>
        )}
      </div>
    </div>
  );
};
