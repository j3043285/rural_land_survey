import React from 'react';
import { District, Taluka, Village } from '../../types';
import { Search } from 'lucide-react';

interface TopFilterBarProps {
  districts: District[];
  selectedDistrictId: number | null;
  onSelectDistrict: (id: number) => void;

  talukas: Taluka[];
  selectedTalukaId: number | null;
  onSelectTaluka: (id: number) => void;

  villages: Village[];
  selectedVillageId: number | null;
  onSelectVillage: (id: number) => void;

  searchQuery: string;
  onSearchChange: (q: string) => void;
  onSearchSubmit: (e: React.FormEvent) => void;

  mapType: 'map' | 'satellite' | 'hybrid' | 'terrain';
  onMapTypeChange: (type: 'map' | 'satellite' | 'hybrid' | 'terrain') => void;
}

export const TopFilterBar: React.FC<TopFilterBarProps> = ({
  districts,
  selectedDistrictId,
  onSelectDistrict,
  talukas,
  selectedTalukaId,
  onSelectTaluka,
  villages,
  selectedVillageId,
  onSelectVillage,
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  mapType,
  onMapTypeChange
}) => {
  const villageNameCounts = villages.reduce<Record<string, number>>((counts, village) => {
    const key = village.name.trim().toLowerCase();
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});

  return (
    <div className="bg-white rounded-xl shadow-2xs border border-slate-200 p-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
      {/* LEFT: Cascading Location Dropdowns */}
      <div className="flex flex-wrap items-center gap-2">
        {/* State */}
        <div className="flex flex-col">
          <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
            State
          </label>
          <select
            disabled
            value="Maharashtra"
            className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 font-semibold text-slate-800 outline-none cursor-default"
          >
            <option value="Maharashtra">Maharashtra</option>
          </select>
        </div>

        {/* District */}
        <div className="flex flex-col">
          <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
            District
          </label>
          <select
            value={selectedDistrictId || ''}
            onChange={(e) => onSelectDistrict(Number(e.target.value))}
            className="bg-white border border-slate-200 hover:border-slate-300 rounded-lg px-2.5 py-1.5 font-medium text-slate-800 outline-none focus:ring-1 focus:ring-blue-500 transition"
          >
            <option value="" disabled>Select District</option>
            {districts.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Taluka */}
        <div className="flex flex-col">
          <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
            Taluka
          </label>
          <select
            disabled={!selectedDistrictId}
            value={selectedTalukaId || ''}
            onChange={(e) => onSelectTaluka(Number(e.target.value))}
            className="bg-white border border-slate-200 hover:border-slate-300 rounded-lg px-2.5 py-1.5 font-medium text-slate-800 outline-none focus:ring-1 focus:ring-blue-500 transition"
          >
            <option value="" disabled>Select Taluka</option>
            {talukas.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        {/* Village */}
        <div className="flex flex-col">
          <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-0.5">
            Village
          </label>
          <select
            disabled={!selectedTalukaId}
            value={selectedVillageId || ''}
            onChange={(e) => onSelectVillage(Number(e.target.value))}
            className="bg-white border border-slate-200 hover:border-slate-300 rounded-lg px-2.5 py-1.5 font-medium text-slate-800 outline-none focus:ring-1 focus:ring-blue-500 transition"
          >
            <option value="" disabled>Select Village</option>
            {villages.map((v) => (
              <option key={v.id} value={v.id}>
                {villageNameCounts[v.name.trim().toLowerCase()] > 1 && v.code ? `${v.name} (${v.code})` : v.name}
              </option>
            ))}
          </select>
        </div>

        {/* SEARCH BOX */}
        <form onSubmit={onSearchSubmit} className="flex flex-col mt-auto">
          <div className="relative w-64">
            <input
              type="text"
              placeholder="Search survey no., plot/Gat no., Khata, owner..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full bg-slate-50 hover:bg-white focus:bg-white border border-slate-200 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 outline-none focus:ring-1 focus:ring-blue-500 transition"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5 pointer-events-none" />
          </div>
        </form>
      </div>

      {/* RIGHT: Map View Switcher Tabs */}
      <div className="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200 self-end">
        <button
          onClick={() => onMapTypeChange('map')}
          className={`px-3 py-1 rounded-md text-[11.5px] font-medium transition ${
            mapType === 'map'
              ? 'bg-blue-600 text-white shadow-2xs font-semibold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Map View
        </button>
        <button
          onClick={() => onMapTypeChange('satellite')}
          className={`px-3 py-1 rounded-md text-[11.5px] font-medium transition ${
            mapType === 'satellite'
              ? 'bg-[#1d72e8] text-white shadow-2xs font-semibold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Satellite
        </button>
        <button
          onClick={() => onMapTypeChange('hybrid')}
          className={`px-3 py-1 rounded-md text-[11.5px] font-medium transition ${
            mapType === 'hybrid'
              ? 'bg-blue-600 text-white shadow-2xs font-semibold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Hybrid
        </button>
        <button
          onClick={() => onMapTypeChange('terrain')}
          className={`px-3 py-1 rounded-md text-[11.5px] font-medium transition ${
            mapType === 'terrain'
              ? 'bg-blue-600 text-white shadow-2xs font-semibold'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Terrain
        </button>
      </div>
    </div>
  );
};
