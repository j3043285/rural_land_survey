import React from 'react';
import { LandParcel } from '../../types';
import {
  X,
  FileCheck,
  MapPin,
  Edit,
  FileText,
  Upload,
  Download,
  Award,
  GitCompare
} from 'lucide-react';

interface ParcelDetailsPanelProps {
  parcel: LandParcel | null;
  onClose: () => void;
  onEdit: () => void;
  onViewReport: () => void;
  onUploadDocs: () => void;
  onDownloadMap: () => void;
  onGenerateCertificate: () => void;
  onCompareBoundary: () => void;
}

export const ParcelDetailsPanel: React.FC<ParcelDetailsPanelProps> = ({
  parcel,
  onClose,
  onEdit,
  onViewReport,
  onUploadDocs,
  onDownloadMap,
  onGenerateCertificate,
  onCompareBoundary
}) => {
  if (!parcel) {
    return (
      <div className="w-80 h-full bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 mb-3">
          <MapPin className="w-6 h-6" />
        </div>
        <p className="font-semibold text-slate-700 text-sm">No Parcel Selected</p>
        <p className="text-xs text-slate-400 mt-1">Click on any cadastral parcel on the map or search above to view complete details.</p>
      </div>
    );
  }

  const isVerified = parcel.boundary_status === 'Verified';
  const isDiscrepancy = parcel.boundary_status === 'Discrepancy' || parcel.discrepancy_status?.includes('Discrepancy');

  return (
    <div className="w-80 h-full bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between overflow-hidden text-slate-800">
      {/* HEADER */}
      <div className="p-3.5 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <FileCheck className="w-4 h-4" />
          </div>
          <h2 className="font-bold text-sm text-slate-900 tracking-tight">Parcel Details</h2>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-700 p-1 rounded-md transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* BODY - DATA FIELDS MATCHING REFERENCE IMAGE */}
      <div className="p-3.5 space-y-2.5 overflow-y-auto text-xs flex-1">
        {/* Survey Number */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Survey Number</span>
          <span className="font-bold text-slate-900 text-[13px]">{parcel.survey_number}</span>
        </div>

        {/* Area (Hectares) */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Area (Hectares)</span>
          <span className="font-bold text-slate-900">{parcel.area_hectares} ha</span>
        </div>

        {/* Area (Acres) */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Area (Acres)</span>
          <span className="font-bold text-slate-900">{parcel.area_acres} acres</span>
        </div>

        {/* Land Type */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Land Type</span>
          <span className="font-semibold text-slate-800">{parcel.land_type}</span>
        </div>

        {/* Owner Name */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Owner Name</span>
          <span className="font-bold text-slate-900 text-right">{parcel.owner_name || 'Patil Shankar Bapu'}</span>
        </div>

        {/* Boundary Status Badge */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Boundary Status</span>
          <span
            className={`px-2 py-0.5 rounded-md font-bold text-[11px] ${
              isVerified
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                : isDiscrepancy
                ? 'bg-red-100 text-red-700 border border-red-300'
                : 'bg-amber-100 text-amber-700 border border-amber-300'
            }`}
          >
            {parcel.boundary_status}
          </span>
        </div>

        {/* Last Survey Date */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Last Survey Date</span>
          <span className="font-semibold text-slate-800">
            {parcel.last_survey_date ? new Date(parcel.last_survey_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '12 Apr 2025'}
          </span>
        </div>

        {/* Remarks */}
        <div className="flex items-start justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium flex-shrink-0">Remarks</span>
          <span className="text-slate-700 text-right text-[11px] leading-snug pl-2">
            {parcel.remarks || 'Boundary matched with GPS'}
          </span>
        </div>

        {/* Discrepancy Status */}
        <div className="flex items-center justify-between py-1 border-b border-slate-50">
          <span className="text-slate-500 font-medium">Discrepancy</span>
          <span
            className={`px-2 py-0.5 rounded-md text-[11px] font-semibold ${
              isDiscrepancy
                ? 'bg-red-100 text-red-700 border border-red-200'
                : 'bg-rose-50 text-rose-600 border border-rose-200'
            }`}
          >
            {parcel.discrepancy_status || 'No Discrepancy'}
          </span>
        </div>

        {/* Coordinates Box */}
        <div className="bg-sky-50/70 border border-sky-100 rounded-lg p-2.5 flex items-center gap-2 mt-1">
          <MapPin className="w-4 h-4 text-sky-600 flex-shrink-0" />
          <div className="text-[11px]">
            <span className="font-bold text-sky-950 block">Coordinates</span>
            <span className="text-slate-600 font-mono text-[10.5px]">
              Lat: {parcel.center_lat?.toFixed(4)}° N | Long: {parcel.center_lng?.toFixed(4)}° E
            </span>
          </div>
        </div>
      </div>

      {/* FOOTER ACTION BUTTONS MATCHING SCREENSHOT */}
      <div className="p-3 border-t border-slate-100 space-y-1.5 bg-slate-50/50">
        {/* Edit Parcel (Primary Blue Button) */}
        <button
          onClick={onEdit}
          className="w-full flex items-center justify-center gap-2 bg-[#1d72e8] hover:bg-[#155fc0] text-white py-2 px-3 rounded-lg font-semibold text-xs transition shadow-sm"
        >
          <Edit className="w-3.5 h-3.5" />
          <span>Edit Parcel</span>
        </button>

        {/* View Survey Report */}
        <button
          onClick={onViewReport}
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 py-1.5 px-3 rounded-lg font-medium text-xs transition shadow-2xs"
        >
          <FileText className="w-3.5 h-3.5 text-slate-500" />
          <span>View Survey Report</span>
        </button>

        {/* Upload Documents */}
        <button
          onClick={onUploadDocs}
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 py-1.5 px-3 rounded-lg font-medium text-xs transition shadow-2xs"
        >
          <Upload className="w-3.5 h-3.5 text-slate-500" />
          <span>Upload Documents</span>
        </button>

        {/* Download Map */}
        <button
          onClick={onDownloadMap}
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 py-1.5 px-3 rounded-lg font-medium text-xs transition shadow-2xs"
        >
          <Download className="w-3.5 h-3.5 text-slate-500" />
          <span>Download Map</span>
        </button>

        {/* Generate Certificate */}
        <button
          onClick={onGenerateCertificate}
          className="w-full flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 py-1.5 px-3 rounded-lg font-medium text-xs transition shadow-2xs"
        >
          <Award className="w-3.5 h-3.5 text-slate-500" />
          <span>Generate Certificate</span>
        </button>

        {/* Compare Old vs New (Special bonus action for discrepancy/resurvey) */}
        {parcel.old_boundary_geojson && (
          <button
            onClick={onCompareBoundary}
            className="w-full flex items-center justify-center gap-2 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 py-1.5 px-3 rounded-lg font-medium text-xs transition shadow-2xs"
          >
            <GitCompare className="w-3.5 h-3.5 text-amber-600" />
            <span>Compare Old vs New</span>
          </button>
        )}
      </div>
    </div>
  );
};
