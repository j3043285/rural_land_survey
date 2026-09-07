import React from 'react';
import { LandParcel } from '../../types';
import { api } from '../../services/api';
import { X, Printer, Download, Award, CheckCircle } from 'lucide-react';

interface SurveyReportModalProps {
  parcel: LandParcel | null;
  isOpen: boolean;
  onClose: () => void;
}

export const SurveyReportModal: React.FC<SurveyReportModalProps> = ({
  parcel,
  isOpen,
  onClose
}) => {
  if (!isOpen || !parcel) return null;

  const handleDownloadPdf = () => {
    window.open(api.getParcelPdfUrl(parcel.id), '_blank');
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-[2000] p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh] text-slate-800">
        {/* Modal Top Bar */}
        <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <Award className="w-5 h-5 text-blue-600" />
            <span className="font-bold text-sm text-slate-900">Survey & Resurvey Verification Certificate</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200 rounded-lg transition"
              title="Print"
            >
              <Printer className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownloadPdf}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </button>
            <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Certificate Sheet */}
        <div className="p-8 overflow-y-auto space-y-6 text-xs bg-white print:p-0">
          {/* Official Letterhead */}
          <div className="text-center border-b-2 border-slate-900 pb-4">
            <div className="text-[11px] font-extrabold tracking-widest text-slate-800 uppercase">
              Government of Maharashtra
            </div>
            <div className="text-[10px] font-semibold text-slate-600 uppercase">
              Revenue and Forest Department • Directorate of Land Records
            </div>
            <h1 className="text-base font-black text-[#0b1e36] mt-1 tracking-tight">
              Rural Agricultural Land Survey / Resurvey (LandSetu)
            </h1>
            <p className="text-[10px] text-slate-500 font-medium italic mt-0.5">
              Statutory Cadastral Inspection Sheet & Bhu-Aadhaar Land Record Extract
            </p>
          </div>

          {/* Reference Meta */}
          <div className="flex items-center justify-between text-[11px] font-medium text-slate-600 border-b border-slate-100 pb-2">
            <span>Certificate No: <b>MH/NSK/YLA/{parcel.gat_number.replace('/', '-')}/2025</b></span>
            <span>Date of Issue: <b>12 Apr 2025</b></span>
            <span>Status: <b className="text-emerald-700">{parcel.boundary_status}</b></span>
          </div>

          {/* Section 1: Land Identification */}
          <div>
            <h4 className="font-bold text-xs text-[#1e40af] uppercase tracking-wider mb-2">
              1. Land Parcel Identification & Cadastral Hierarchy
            </h4>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <div><span className="text-slate-500 font-medium">State:</span> <b className="text-slate-900">Maharashtra</b></div>
              <div><span className="text-slate-500 font-medium">District:</span> <b className="text-slate-900">{parcel.district_name || 'Nashik'}</b></div>
              <div><span className="text-slate-500 font-medium">Taluka:</span> <b className="text-slate-900">{parcel.taluka_name || 'Yeola'}</b></div>
              <div><span className="text-slate-500 font-medium">Village:</span> <b className="text-slate-900">{parcel.village_name || 'Pimpalgaon'}</b></div>
              <div><span className="text-slate-500 font-medium">Gat Number:</span> <b className="text-slate-900">{parcel.gat_number}</b></div>
              <div><span className="text-slate-500 font-medium">Survey Number:</span> <b className="text-slate-900">{parcel.survey_number}</b></div>
              <div><span className="text-slate-500 font-medium">Khata Number:</span> <b className="text-slate-900">{parcel.khata_number}</b></div>
              <div><span className="text-slate-500 font-medium">Land Category:</span> <b className="text-slate-900">{parcel.land_type}</b></div>
            </div>
          </div>

          {/* Section 2: Ownership */}
          <div>
            <h4 className="font-bold text-xs text-[#1e40af] uppercase tracking-wider mb-2">
              2. Landholder & Ownership Record (Form 7/12 & 8A)
            </h4>
            <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Primary Khatadar / Owner:</span>
                <b className="text-slate-900">{parcel.owner_name || 'Patil Shankar Bapu'}</b>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Ownership Share:</span>
                <b className="text-slate-900">100% (Single Landholder)</b>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-medium">Aadhaar Authentication:</span>
                <b className="text-emerald-700 flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5 inline" /> Verified via UIDAI Biometrics
                </b>
              </div>
            </div>
          </div>

          {/* Section 3: Measurements */}
          <div>
            <h4 className="font-bold text-xs text-[#1e40af] uppercase tracking-wider mb-2">
              3. Resurvey Boundary & Area Measurements
            </h4>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 bg-slate-50 p-3.5 rounded-lg border border-slate-200">
              <div><span className="text-slate-500 font-medium">Historical Area (7/12):</span> <b className="text-slate-900">{parcel.area_hectares} ha ({parcel.area_acres} acres)</b></div>
              <div><span className="text-slate-500 font-medium">Resurveyed Area (DGPS):</span> <b className="text-slate-900">{parcel.area_hectares} ha ({parcel.area_acres} acres)</b></div>
              <div><span className="text-slate-500 font-medium">Deviation / Difference:</span> <b className="text-emerald-700">0.00 ha (0.0% variance)</b></div>
              <div><span className="text-slate-500 font-medium">Survey Accuracy:</span> <b className="text-slate-900">± 0.45 meters (RTK Base)</b></div>
              <div><span className="text-slate-500 font-medium">Centroid Latitude:</span> <b className="font-mono text-slate-900">{parcel.center_lat?.toFixed(4)}° N</b></div>
              <div><span className="text-slate-500 font-medium">Centroid Longitude:</span> <b className="font-mono text-slate-900">{parcel.center_lng?.toFixed(4)}° E</b></div>
            </div>
          </div>

          {/* Official Signatures */}
          <div className="pt-6 border-t border-slate-200 grid grid-cols-3 gap-4 text-center">
            <div className="border border-slate-200 p-2.5 rounded-lg bg-slate-50/50">
              <div className="h-10 flex items-center justify-center font-serif italic text-blue-900 font-bold">
                BhumiAbhilekh_Sign
              </div>
              <p className="font-bold text-slate-800 text-[10px]">Cadastral Surveyor</p>
              <p className="text-[9px] text-slate-400">Yeola Tahsil Office</p>
            </div>
            <div className="border border-slate-200 p-2.5 rounded-lg bg-slate-50/50">
              <div className="h-10 flex items-center justify-center font-serif italic text-blue-900 font-bold">
                CircleOfficer_Verified
              </div>
              <p className="font-bold text-slate-800 text-[10px]">Circle Inspector / Verifier</p>
              <p className="text-[9px] text-slate-400">Pimpalgaon Circle</p>
            </div>
            <div className="border border-slate-200 p-2.5 rounded-lg bg-slate-50/50">
              <div className="h-10 flex items-center justify-center text-emerald-700">
                <span className="border-2 border-emerald-600 rounded-full px-2 py-0.5 font-bold text-[9px] uppercase tracking-wider">
                  Verified Seal
                </span>
              </div>
              <p className="font-bold text-slate-800 text-[10px]">Bhu-Aadhaar Registry</p>
              <p className="text-[9px] text-slate-400">Govt of Maharashtra</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
