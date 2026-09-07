import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ClipboardPlus, FileSearch, MapPinned, MessageSquare } from 'lucide-react';
import { District, Taluka, Village, LandParcel, DashboardStats } from '../types';
import { api } from '../services/api';
import { TopFilterBar } from '../components/dashboard/TopFilterBar';
import { CadastralMap } from '../components/maps/CadastralMap';
import { ParcelDetailsPanel } from '../components/dashboard/ParcelDetailsPanel';
import { KpiCards } from '../components/dashboard/KpiCards';
import { AnalyticsRow } from '../components/dashboard/AnalyticsRow';
import { EditParcelModal } from '../components/modals/EditParcelModal';
import { SurveyReportModal } from '../components/modals/SurveyReportModal';
import { UploadDocumentModal } from '../components/modals/UploadDocumentModal';
import { CompareBoundaryModal } from '../components/modals/CompareBoundaryModal';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  // Cascading Location States
  const [districts, setDistricts] = useState<District[]>([]);
  const [selectedDistrictId, setSelectedDistrictId] = useState<number | null>(null);

  const [talukas, setTalukas] = useState<Taluka[]>([]);
  const [selectedTalukaId, setSelectedTalukaId] = useState<number | null>(null);

  const [villages, setVillages] = useState<Village[]>([]);
  const [selectedVillageId, setSelectedVillageId] = useState<number | null>(null);

  // Search & Map States
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMessage, setSearchMessage] = useState('');
  const [mapType, setMapType] = useState<'map' | 'satellite' | 'hybrid' | 'terrain'>('satellite');

  // Parcels and Selection
  const [parcels, setParcels] = useState<LandParcel[]>([]);
  const [selectedParcel, setSelectedParcel] = useState<LandParcel | null>(null);

  // Stats
  const [stats, setStats] = useState<DashboardStats | null>(null);

  // Modals
  const [showEditModal, setShowEditModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);

  // 1. Load Initial Districts
  useEffect(() => {
    api.getDistricts().then((data) => {
      setDistricts(data);
    }).catch(console.error);

    api.getDashboardStats().then(setStats).catch(console.error);
  }, []);

  // 2. Load Talukas when District Changes
  useEffect(() => {
    setTalukas([]);
    setSelectedTalukaId(null);
    setVillages([]);
    setSelectedVillageId(null);
    if (!selectedDistrictId) return;
    api.getTalukas(selectedDistrictId).then((data) => {
      setTalukas(data);
    }).catch(console.error);
  }, [selectedDistrictId]);

  // 3. Load Villages when Taluka Changes
  useEffect(() => {
    if (!selectedTalukaId) return;
    setVillages([]);
    setSelectedVillageId(null);
    api.getVillages(selectedTalukaId).then((data) => {
      setVillages(data);
    }).catch(console.error);
  }, [selectedTalukaId]);

  // 4. Load Parcels when Village Changes
  useEffect(() => {
    if (!selectedVillageId) return;
    let active = true;
    setParcels([]);
    setSelectedParcel(null);
    api.getParcels(selectedVillageId).then((data) => {
      if (!active) return;
      setParcels(data);
      // Select 50/1 by default matching screenshot
      const defaultParcel = data.find((p) => p.survey_number === '50/1') || data[0] || null;
      if (defaultParcel) {
        api.getParcelDetail(defaultParcel.id).then((detail) => {
          if (active) setSelectedParcel(detail);
        }).catch(() => {
          if (active) setSelectedParcel(defaultParcel);
        });
      }
    }).catch(console.error);

    api.getDashboardStats(selectedVillageId).then(setStats).catch(console.error);
    return () => {
      active = false;
    };
  }, [selectedVillageId]);

  // Handle Search
  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const results = await api.searchParcels(searchQuery, selectedVillageId || undefined);
      if (results.length > 0) {
        setSearchMessage(`${results.length} matching parcel${results.length === 1 ? '' : 's'} found.`);
        const fullDetail = await api.getParcelDetail(results[0].id);
        setSelectedParcel(fullDetail);
      } else {
        setSearchMessage(`No parcel records found for "${searchQuery}". Official village data does not include parcel/Gat records yet.`);
      }
    } catch (err: any) {
      setSearchMessage(`Search error: ${err.message}`);
    }
  };

  const handleSelectParcel = async (p: LandParcel) => {
    try {
      const fullDetail = await api.getParcelDetail(p.id);
      setSelectedParcel(fullDetail);
    } catch (_) {
      setSelectedParcel(p);
    }
  };

  // Download Map GeoJSON file
  const handleDownloadMap = () => {
    if (!selectedParcel) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(
      JSON.stringify({
        type: "Feature",
        properties: {
          survey_number: selectedParcel.survey_number,
          gat_number: selectedParcel.gat_number,
          owner: selectedParcel.owner_name,
          area_ha: selectedParcel.area_hectares
        },
        geometry: selectedParcel.boundary_geojson ? JSON.parse(selectedParcel.boundary_geojson) : null
      }, null, 2)
    );
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Cadastral_Map_Gat_${selectedParcel.gat_number.replace('/', '_')}.geojson`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Generate Certificate (download PDF)
  const handleGenerateCertificate = () => {
    if (!selectedParcel) return;
    window.open(api.getParcelPdfUrl(selectedParcel.id), '_blank');
  };

  return (
    <div className="p-4 space-y-4 max-w-[1600px] mx-auto">
      {/* 1. TOP CONTROL & CASCADING FILTER BAR */}
      <TopFilterBar
        districts={districts}
        selectedDistrictId={selectedDistrictId}
        onSelectDistrict={setSelectedDistrictId}
        talukas={talukas}
        selectedTalukaId={selectedTalukaId}
        onSelectTaluka={setSelectedTalukaId}
        villages={villages}
        selectedVillageId={selectedVillageId}
        onSelectVillage={setSelectedVillageId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearchSubmit={handleSearchSubmit}
        mapType={mapType}
        onMapTypeChange={setMapType}
      />
      {searchMessage && <div className="bg-slate-800 text-white rounded-lg px-3 py-2 text-xs">{searchMessage}</div>}

      {selectedVillageId && (
        <div className="bg-white border border-slate-200 rounded-xl p-3 shadow-sm flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <MapPinned className="w-4 h-4 text-sky-600" />
            <div>
              <p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">Selected village</p>
              <p className="text-sm font-bold text-slate-900">{villages.find((v) => v.id === selectedVillageId)?.name || 'Loading village'}</p>
            </div>
            <span className="text-[11px] text-slate-500 ml-2">{parcels.length} parcel records available</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => navigate(`/field-survey?village_id=${selectedVillageId}`)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-sky-600 text-white text-[11px] font-bold hover:bg-sky-700"><ClipboardPlus className="w-3.5 h-3.5" />Start field survey</button>
            <button onClick={() => navigate(`/parcel-records?village_id=${selectedVillageId}`)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-[11px] font-bold hover:bg-slate-50"><FileSearch className="w-3.5 h-3.5" />View records</button>
            <button onClick={() => navigate('/grievances')} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-orange-200 text-orange-700 text-[11px] font-bold hover:bg-orange-50"><MessageSquare className="w-3.5 h-3.5" />Raise grievance</button>
            <button onClick={() => navigate('/reports')} className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-slate-200 text-slate-700 text-[11px] font-bold hover:bg-slate-50"><ArrowRight className="w-3.5 h-3.5" />Reports</button>
          </div>
        </div>
      )}

      {/* 2. MAIN CADASRAL MAP & PARCEL DETAILS ROW */}
      <div className="flex flex-col lg:flex-row gap-3.5 h-[500px]">
        {/* Cadastral Interactive GIS Map */}
        <div className="flex-1 h-full min-h-[350px]">
          <CadastralMap
            parcels={parcels}
            selectedParcel={selectedParcel}
            onSelectParcel={handleSelectParcel}
            mapType={mapType}
            villageCenter={villages.find((v) => v.id === selectedVillageId) ? {
              lat: villages.find((v) => v.id === selectedVillageId)!.center_lat,
              lng: villages.find((v) => v.id === selectedVillageId)!.center_lng
            } : undefined}
          />
        </div>

        {/* Right-Side Parcel Details Panel */}
        <div className="h-full flex-shrink-0">
          <ParcelDetailsPanel
            parcel={selectedParcel}
            onClose={() => setSelectedParcel(null)}
            onEdit={() => setShowEditModal(true)}
            onViewReport={() => setShowReportModal(true)}
            onUploadDocs={() => setShowUploadModal(true)}
            onDownloadMap={handleDownloadMap}
            onGenerateCertificate={handleGenerateCertificate}
            onCompareBoundary={() => setShowCompareModal(true)}
          />
        </div>
      </div>

      {/* 3. KPI METRIC SUMMARY CARDS */}
      <KpiCards kpis={stats?.kpis || null} />

      {/* 4. BOTTOM ANALYTICS & RECENT RECORDS ROW */}
      <AnalyticsRow
        landTypes={stats?.land_types || []}
        areaByTaluka={stats?.area_by_taluka || []}
        recentSurveys={stats?.recent_surveys || []}
        onSelectSurveyNo={async (sNo) => {
          const matched = parcels.find((p) => p.survey_number === sNo || p.gat_number === sNo);
          if (matched) {
            const detail = await api.getParcelDetail(matched.id);
            setSelectedParcel(detail);
          }
        }}
      />

      {/* MODALS */}
      <EditParcelModal
        parcel={selectedParcel}
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        onUpdated={(updated) => {
          setSelectedParcel(updated);
          setParcels((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
          api.getDashboardStats(selectedVillageId || undefined).then(setStats);
        }}
      />

      <SurveyReportModal
        parcel={selectedParcel}
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
      />

      <UploadDocumentModal
        parcel={selectedParcel}
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />

      <CompareBoundaryModal
        parcel={selectedParcel}
        isOpen={showCompareModal}
        onClose={() => setShowCompareModal(false)}
      />
    </div>
  );
};
