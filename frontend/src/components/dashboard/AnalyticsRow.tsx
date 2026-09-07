import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LabelList
} from 'recharts';
import { LandTypeItem, AreaByTalukaItem, RecentSurveyItem } from '../../types';
import { ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface AnalyticsRowProps {
  landTypes: LandTypeItem[];
  areaByTaluka: AreaByTalukaItem[];
  recentSurveys: RecentSurveyItem[];
  onSelectSurveyNo?: (surveyNo: string) => void;
}

export const AnalyticsRow: React.FC<AnalyticsRowProps> = ({
  landTypes,
  areaByTaluka,
  recentSurveys,
  onSelectSurveyNo
}) => {
  const pieData = landTypes?.length > 0 ? landTypes : [
    { name: 'Agricultural', percentage: 68.2, color: '#22c55e', area_ha: 233.6 },
    { name: 'Horticulture', percentage: 12.5, color: '#06b6d4', area_ha: 42.8 },
    { name: 'Forest', percentage: 8.7, color: '#15803d', area_ha: 29.8 },
    { name: 'Barren', percentage: 6.1, color: '#3b82f6', area_ha: 20.9 },
    { name: 'Others', percentage: 4.5, color: '#a855f7', area_ha: 15.4 }
  ];

  const barData = areaByTaluka?.length > 0 ? areaByTaluka : [
    { taluka: 'Yeola', area_ha: 145 },
    { taluka: 'Nashik', area_ha: 98 },
    { taluka: 'Sinnar', area_ha: 76 },
    { taluka: 'Dindori', area_ha: 62 },
    { taluka: 'Kalwan', area_ha: 48 }
  ];

  const tableData = recentSurveys?.length > 0 ? recentSurveys : [
    { id: 1, date: '12 Apr 2025', survey_no: '50/1', area_ha: 1.82, status: 'Verified' },
    { id: 2, date: '11 Apr 2025', survey_no: '48/3', area_ha: 2.15, status: 'Discrepancy' },
    { id: 3, date: '10 Apr 2025', survey_no: '53/2', area_ha: 3.12, status: 'In Progress' },
    { id: 4, date: '09 Apr 2025', survey_no: '51/1', area_ha: 2.76, status: 'Verified' },
    { id: 5, date: '08 Apr 2025', survey_no: '52/1', area_ha: 1.95, status: 'Verified' }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-3.5">
      {/* 1. LAND TYPE DISTRIBUTION (Donut Chart) */}
      <div className="bg-white rounded-xl p-4 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <h3 className="font-bold text-xs text-slate-800 tracking-tight mb-2">
          Land Type Distribution
        </h3>

        <div className="flex items-center justify-between h-44">
          {/* Donut Chart */}
          <div className="w-1/2 h-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={36}
                  outerRadius={62}
                  paddingAngle={2}
                  dataKey="percentage"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => [`${value}%`, 'Share']} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legend */}
          <div className="w-1/2 pl-2 space-y-1.5 text-xs">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <span
                    className="w-2.5 h-2.5 rounded-full inline-block flex-shrink-0"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="text-slate-600 text-[11px] font-medium">{item.name}</span>
                </div>
                <span className="font-bold text-slate-900 text-[11.5px]">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 2. AREA BY TALUKA (Bar Chart) */}
      <div className="bg-white rounded-xl p-4 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <h3 className="font-bold text-xs text-slate-800 tracking-tight mb-1">Area by Taluka</h3>

        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 18, right: 10, left: -24, bottom: 0 }}>
              <XAxis dataKey="taluka" tick={{ fontSize: 10.5, fill: '#475569' }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 200]} ticks={[0, 50, 100, 150, 200]} tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip formatter={(val: any) => [`${val} ha`, 'Area']} />
              <Bar dataKey="area_ha" fill="#2563eb" radius={[4, 4, 0, 0]}>
                <LabelList dataKey="area_ha" position="top" fill="#1e293b" fontSize={10} fontWeight="bold" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <span className="text-center text-[10px] text-slate-400 font-medium">Area (Hectares)</span>
      </div>

      {/* 3. RECENT SURVEY RECORDS (Table) */}
      <div className="bg-white rounded-xl p-4 shadow-2xs border border-slate-200 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-xs text-slate-800 tracking-tight">Recent Survey Records</h3>
          <Link
            to="/parcel-records"
            className="text-[11px] text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-0.5"
          >
            <span>View All</span>
            <ArrowUpRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-[10.5px] font-semibold text-slate-400 border-b border-slate-100 pb-1">
                <th className="py-1 font-semibold">Date</th>
                <th className="py-1 font-semibold">Survey No.</th>
                <th className="py-1 font-semibold text-right">Area (ha)</th>
                <th className="py-1 font-semibold text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 text-[11px]">
              {tableData.map((row) => {
                const isVerified = row.status === 'Verified';
                const isDiscrepancy = row.status === 'Discrepancy';
                return (
                  <tr
                    key={row.id}
                    onClick={() => onSelectSurveyNo && onSelectSurveyNo(row.survey_no)}
                    className="hover:bg-slate-50/80 cursor-pointer transition"
                  >
                    <td className="py-1.5 text-slate-600 font-medium">{row.date}</td>
                    <td className="py-1.5 font-bold text-slate-900">{row.survey_no}</td>
                    <td className="py-1.5 text-right font-medium text-slate-700">{row.area_ha}</td>
                    <td className="py-1.5 text-right">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          isVerified
                            ? 'bg-emerald-100 text-emerald-700'
                            : isDiscrepancy
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                        }`}
                      >
                        {row.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
