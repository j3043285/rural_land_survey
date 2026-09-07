import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LandParcel } from '../types';
import { FileBarChart, Download } from 'lucide-react';

export const Reports: React.FC = () => {
  const [parcels, setParcels] = useState<LandParcel[]>([]);

  useEffect(() => {
    api.getParcels(1).then((data) => {
      setParcels(data);
    });
  }, []);

  const handleDownloadPdf = (id: number) => {
    window.open(api.getParcelPdfUrl(id), '_blank');
  };

  const handleExportCSV = () => {
    if (parcels.length === 0) return;
    const headers = ['Gat Number', 'Survey Number', 'Khata Number', 'Owner Name', 'Area (ha)', 'Area (acres)', 'Land Type', 'Status', 'Discrepancy'];
    const rows = parcels.map((p) => [
      p.gat_number,
      p.survey_number,
      p.khata_number,
      `"${p.owner_name || ''}"`,
      p.area_hectares,
      p.area_acres,
      `"${p.land_type}"`,
      p.boundary_status,
      `"${p.discrepancy_status}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'LandSetu_Pimpalgaon_Cadastral_Report.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-xs">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FileBarChart className="w-5 h-5 text-blue-600" />
            <span>Cadastral Survey & Resurvey Reports</span>
          </h1>
          <p className="text-slate-500">Generate certified Bhu-Aadhaar verification sheets, village summaries, and CSV registers</p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded-xl shadow-2xs transition"
        >
          <Download className="w-4 h-4" />
          <span>Export Village CSV</span>
        </button>
      </div>

      {/* Quick Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <span className="text-slate-400 font-medium block">Total Registered Parcels</span>
          <span className="text-2xl font-black text-slate-900 mt-1 block">248 Parcels</span>
          <span className="text-[11px] text-slate-500 mt-1 block">Village: Pimpalgaon, Yeola</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <span className="text-slate-400 font-medium block">Verified Land Records</span>
          <span className="text-2xl font-black text-emerald-700 mt-1 block">142 Certified</span>
          <span className="text-[11px] text-emerald-600 mt-1 block">57.3% total accuracy confirmed</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs">
          <span className="text-slate-400 font-medium block">Boundary Discrepancies</span>
          <span className="text-2xl font-black text-red-600 mt-1 block">18 Under Hearing</span>
          <span className="text-[11px] text-red-500 mt-1 block">Scheduled with Circle Inspector</span>
        </div>
      </div>

      {/* Individual Parcel Certificates Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
          <span className="font-bold text-slate-800">Parcels Available for Official PDF Certificate Generation</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-50 text-slate-500 font-semibold text-[11px] border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Gat Number</th>
                <th className="py-2.5 px-4">Landholder Name</th>
                <th className="py-2.5 px-4">Khata No.</th>
                <th className="py-2.5 px-4 text-right">Area (ha)</th>
                <th className="py-2.5 px-4">Land Type</th>
                <th className="py-2.5 px-4 text-center">Status</th>
                <th className="py-2.5 px-4 text-right">Download PDF</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {parcels.slice(0, 15).map((p) => (
                <tr key={p.id} className="hover:bg-slate-50 transition">
                  <td className="py-3 px-4 font-bold text-slate-900">Gat {p.gat_number}</td>
                  <td className="py-3 px-4 font-medium text-slate-700">{p.owner_name}</td>
                  <td className="py-3 px-4 font-mono text-slate-600">{p.khata_number}</td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-slate-800">{p.area_hectares} ha</td>
                  <td className="py-3 px-4 text-slate-600">{p.land_type}</td>
                  <td className="py-3 px-4 text-center">
                    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                      p.boundary_status === 'Verified' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {p.boundary_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => handleDownloadPdf(p.id)}
                      className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold text-[11px]"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Certificate</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
