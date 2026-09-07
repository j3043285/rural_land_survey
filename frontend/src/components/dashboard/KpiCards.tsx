import React from 'react';
import { KpiStats } from '../../types';
import {
  Sprout,
  CheckCircle2,
  ShieldCheck,
  AlertTriangle,
  UserCheck
} from 'lucide-react';

interface KpiCardsProps {
  kpis: KpiStats | null;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ kpis }) => {
  const stats = kpis || {
    total_parcels: 248,
    surveyed_count: 186,
    surveyed_pct: 75.0,
    verified_count: 142,
    verified_pct: 57.3,
    discrepancy_count: 18,
    discrepancy_pct: 7.3,
    total_area_surveyed_ha: 342.6,
    area_surveyed_pct: 68.2
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      {/* 1. Total Parcels */}
      <div className="bg-white rounded-xl p-3.5 shadow-2xs border border-slate-200 flex items-center justify-between">
        <div>
          <span className="text-[11.5px] font-semibold text-slate-500 block">Total Parcels</span>
          <span className="text-2xl font-extrabold text-slate-900 tracking-tight block mt-0.5">
            {stats.total_parcels}
          </span>
          <span className="text-[10.5px] text-slate-400 mt-1 block">in selected village</span>
        </div>
        <div className="w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
          <Sprout className="w-5 h-5" />
        </div>
      </div>

      {/* 2. Surveyed */}
      <div className="bg-white rounded-xl p-3.5 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[11.5px] font-semibold text-slate-500 block">Surveyed</span>
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight block mt-0.5">
              {stats.surveyed_count}
            </span>
          </div>
          <div className="w-10 h-10 rounded-full bg-sky-50 text-sky-600 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-2">
          <div className="flex justify-between text-[10.5px] text-slate-500 mb-1">
            <span>{stats.surveyed_pct}% complete</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats.surveyed_pct}%` }}
            />
          </div>
        </div>
      </div>

      {/* 3. Verified */}
      <div className="bg-white rounded-xl p-3.5 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[11.5px] font-semibold text-slate-500 block">Verified</span>
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight block mt-0.5">
              {stats.verified_count}
            </span>
          </div>
          <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-2">
          <div className="flex justify-between text-[10.5px] text-slate-500 mb-1">
            <span>{stats.verified_pct}% verified</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats.verified_pct}%` }}
            />
          </div>
        </div>
      </div>

      {/* 4. Discrepancy Found */}
      <div className="bg-white rounded-xl p-3.5 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[11.5px] font-semibold text-slate-500 block">Discrepancy Found</span>
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight block mt-0.5">
              {stats.discrepancy_count}
            </span>
          </div>
          <div className="w-10 h-10 rounded-full bg-red-50 text-red-600 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-2">
          <div className="flex justify-between text-[10.5px] text-slate-500 mb-1">
            <span>{stats.discrepancy_pct}% of total</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-red-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats.discrepancy_pct}%` }}
            />
          </div>
        </div>
      </div>

      {/* 5. Total Area Surveyed */}
      <div className="bg-white rounded-xl p-3.5 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[11.5px] font-semibold text-slate-500 block">Total Area Surveyed</span>
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight block mt-0.5">
              {stats.total_area_surveyed_ha} ha
            </span>
          </div>
          <div className="w-10 h-10 rounded-full bg-purple-50 text-purple-600 flex items-center justify-center flex-shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-2">
          <div className="flex justify-between text-[10.5px] text-slate-500 mb-1">
            <span>{stats.area_surveyed_pct}% of total area</span>
          </div>
          <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
            <div
              className="bg-purple-600 h-full rounded-full transition-all duration-500"
              style={{ width: `${stats.area_surveyed_pct}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
