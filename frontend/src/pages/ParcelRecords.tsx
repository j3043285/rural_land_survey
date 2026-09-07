import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { LandParcel } from '../types';
import { Search, Download } from 'lucide-react';

export const ParcelRecords: React.FC = () => {
  const [searchParams] = useSearchParams();
  const villageId = Number(searchParams.get('village_id')) || 1;
  const [parcels, setParcels] = useState<LandParcel[]>([]);
  const [selectedParcel, setSelectedParcel] = useState<LandParcel | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | '712' | '8a' | 'ferfar' | 'crops' | 'documents'>('overview');

  useEffect(() => {
    api.getParcels(villageId).then((data) => {
      setParcels(data);
      if (data.length > 0) {
        api.getParcelDetail(data[0].id).then(setSelectedParcel);
      }
    });
  }, [villageId]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      api.getParcels(1).then(setParcels);
      return;
    }
    const results = await api.searchParcels(searchQuery);
    setParcels(results);
    if (results.length > 0) {
      api.getParcelDetail(results[0].id).then(setSelectedParcel);
    }
  };

  const handleSelectParcel = async (id: number) => {
    const detail = await api.getParcelDetail(id);
    setSelectedParcel(detail);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 text-xs">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Land Registry & Cadastral Records</h1>
        <p className="text-slate-500">Official 7/12 Extracts, 8A Khatavahi, Ferfar Mutations, and Agronomic Profiles</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Parcel List */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200 flex flex-col h-[650px]">
          <form onSubmit={handleSearch} className="mb-3">
            <div className="relative">
              <input
                type="text"
                placeholder="Search Gat, Survey or Farmer Name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-8 pr-3 py-2 text-xs outline-none focus:ring-1 focus:ring-blue-500"
              />
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </div>
          </form>

          <div className="overflow-y-auto divide-y divide-slate-100 flex-1">
            {parcels.map((p) => {
              const isSelected = selectedParcel?.id === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => handleSelectParcel(p.id)}
                  className={`p-3 rounded-xl cursor-pointer transition flex items-center justify-between ${
                    isSelected ? 'bg-blue-50 border border-blue-200' : 'hover:bg-slate-50'
                  }`}
                >
                  <div>
                    <span className="font-bold text-slate-900 block text-xs">Gat No. {p.gat_number}</span>
                    <span className="text-slate-500 text-[11px] block">{p.owner_name}</span>
                    <span className="text-[10px] text-slate-400">{p.land_type}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-mono font-bold text-slate-800 block text-xs">{p.area_hectares} ha</span>
                    <span className={`inline-block px-1.5 py-0.5 rounded text-[9.5px] font-bold mt-1 ${
                      p.boundary_status === 'Verified' ? 'bg-emerald-100 text-emerald-700' : (p.boundary_status === 'Discrepancy' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700')
                    }`}>
                      {p.boundary_status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Detail Card with Tabs */}
        {selectedParcel && (
          <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col h-[650px] overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="font-bold text-base text-slate-900">Gat {selectedParcel.gat_number}</h2>
                  <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-semibold text-[11px]">
                    Khata #{selectedParcel.khata_number}
                  </span>
                </div>
                <p className="text-slate-500 text-[11px] mt-0.5">
                  Village: {selectedParcel.village_name || 'Pimpalgaon'} • Taluka: {selectedParcel.taluka_name || 'Yeola'} • Nashik
                </p>
              </div>

              <button
                onClick={() => window.open(api.getParcelPdfUrl(selectedParcel.id), '_blank')}
                className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg font-semibold text-xs shadow-2xs transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export PDF</span>
              </button>
            </div>

            {/* Tab Navigation */}
            <div className="flex border-b border-slate-200 bg-slate-50/30 px-4 gap-4 overflow-x-auto text-[11.5px] font-semibold">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-2.5 border-b-2 transition ${
                  activeTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('712')}
                className={`py-2.5 border-b-2 transition ${
                  activeTab === '712' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Form 7/12 (Saat Bara)
              </button>
              <button
                onClick={() => setActiveTab('8a')}
                className={`py-2.5 border-b-2 transition ${
                  activeTab === '8a' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Form 8A (Khata)
              </button>
              <button
                onClick={() => setActiveTab('ferfar')}
                className={`py-2.5 border-b-2 transition ${
                  activeTab === 'ferfar' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Ferfar (Mutations)
              </button>
              <button
                onClick={() => setActiveTab('crops')}
                className={`py-2.5 border-b-2 transition ${
                  activeTab === 'crops' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Crops & Water
              </button>
            </div>

            {/* Tab Content */}
            <div className="p-5 flex-1 overflow-y-auto space-y-4">
              {activeTab === 'overview' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                      <span className="text-slate-400 block text-[10.5px]">Landholder Name</span>
                      <span className="font-bold text-slate-900 text-sm block mt-0.5">{selectedParcel.owner_name}</span>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                      <span className="text-slate-400 block text-[10.5px]">Registered Area</span>
                      <span className="font-bold text-slate-900 text-sm block mt-0.5">
                        {selectedParcel.area_hectares} ha ({selectedParcel.area_acres} acres)
                      </span>
                    </div>
                  </div>

                  <div className="border border-slate-200 rounded-xl p-4 space-y-2 bg-white">
                    <h4 className="font-bold text-slate-800">Spatial & Survey Attributes</h4>
                    <div className="grid grid-cols-2 gap-2 text-slate-600">
                      <div>Survey Status: <b className="text-emerald-700">{selectedParcel.boundary_status}</b></div>
                      <div>Discrepancy: <b className="text-slate-800">{selectedParcel.discrepancy_status}</b></div>
                      <div>Latitude: <b className="font-mono">{selectedParcel.center_lat}° N</b></div>
                      <div>Longitude: <b className="font-mono">{selectedParcel.center_lng}° E</b></div>
                      <div>Survey Remarks: <b>{selectedParcel.remarks}</b></div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === '712' && (
                <div className="border border-slate-300 rounded-xl p-5 bg-amber-50/20 font-serif space-y-3">
                  <div className="text-center border-b border-slate-300 pb-2">
                    <h3 className="font-bold text-sm text-slate-900 uppercase">गावाचे नाव: {selectedParcel.village_name || 'पिंपळगाव'}</h3>
                    <p className="text-[11px] text-slate-600">गाव नमुना सात (अधिकार अभिलेख पत्रक) व गाव नमुना बारा (पिकांची पाहणी)</p>
                  </div>
                  <div className="grid grid-cols-3 gap-3 border-b border-slate-200 pb-2">
                    <div><b>भूमापन क्रमांक / गट क्र:</b> {selectedParcel.gat_number}</div>
                    <div><b>क्षेत्र:</b> {selectedParcel.area_hectares} हेक्टर</div>
                    <div><b>खाते क्रमांक:</b> {selectedParcel.khata_number}</div>
                  </div>
                  <div>
                    <b>खातेदाराचे नाव:</b> {selectedParcel.owner_name} (भोगवटादार वर्ग - १)
                  </div>
                  <div className="text-[10px] text-slate-400 italic pt-2">
                    Note: Digitally certified extract reproduced from LandSetu Bhu-Abhilekh cadastral engine.
                  </div>
                </div>
              )}

              {activeTab === '8a' && (
                <div className="border border-slate-300 rounded-xl p-5 bg-slate-50 space-y-3">
                  <h3 className="font-bold text-sm text-slate-900 border-b pb-2">
                    गाव नमुना आठ-अ (खातेदाराची नोंदवही)
                  </h3>
                  <div className="space-y-1.5 text-slate-700">
                    <div><b>खातेदार:</b> {selectedParcel.owner_name}</div>
                    <div><b>खाते क्र.:</b> {selectedParcel.khata_number}</div>
                    <div><b>गावातील एकूण धारण जमीन:</b> {selectedParcel.area_hectares} हेक्टर ({selectedParcel.area_acres} एकर)</div>
                    <div><b>आकारणी (रुपये):</b> ₹ 18.50</div>
                  </div>
                </div>
              )}

              {activeTab === 'ferfar' && (
                <div className="space-y-3">
                  <h3 className="font-bold text-xs text-slate-800">फेरफार नोंदी (Mutations History)</h3>
                  {selectedParcel.mutations && selectedParcel.mutations.length > 0 ? (
                    selectedParcel.mutations.map((m) => (
                      <div key={m.id} className="border border-slate-200 rounded-xl p-3 bg-slate-50 space-y-1">
                        <div className="flex justify-between font-bold text-slate-800">
                          <span>फेरफार क्र. {m.ferfar_number}</span>
                          <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded text-[10px]">{m.status}</span>
                        </div>
                        <p className="text-slate-600">{m.details}</p>
                        <span className="text-[10px] text-slate-400">मंजूर करणारे अधिकारी: {m.approved_by}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-400 italic">No pending mutation records found.</p>
                  )}
                </div>
              )}

              {activeTab === 'crops' && (
                <div className="space-y-3">
                  <h3 className="font-bold text-xs text-slate-800">पिकांची पाहणी (E-Crop Survey / Pik Pahani)</h3>
                  {selectedParcel.crops && selectedParcel.crops.length > 0 ? (
                    selectedParcel.crops.map((c) => (
                      <div key={c.id} className="border border-slate-200 rounded-xl p-3 bg-emerald-50/40 flex justify-between items-center">
                        <div>
                          <span className="font-bold text-emerald-950 block">{c.crop_name}</span>
                          <span className="text-slate-500 text-[11px]">{c.season} {c.year} • {c.irrigation_source}</span>
                        </div>
                        <span className="font-mono font-bold text-emerald-800">{c.area_covered} ha</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-slate-400 italic">No crop survey records found.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
