export interface District {
  id: number;
  name: string;
  state: string;
  code?: string;
  center_lat?: number;
  center_lng?: number;
}

export interface Taluka {
  id: number;
  name: string;
  code?: string;
  district_id: number;
  center_lat?: number;
  center_lng?: number;
}

export interface Village {
  id: number;
  name: string;
  code?: string;
  taluka_id: number;
  center_lat: number;
  center_lng: number;
  boundary_geojson?: string;
}

export interface CropRecord {
  id: number;
  season: string;
  year: number;
  crop_name: string;
  area_covered: number;
  irrigation_source: string;
}

export interface MutationRecord {
  id: number;
  ferfar_number: string;
  mutation_date: string;
  mutation_type: string;
  details: string;
  approved_by: string;
  status: string;
}

export interface ParcelOwner {
  id: number;
  farmer: {
    id: number;
    full_name: string;
    aadhaar_masked?: string;
    mobile?: string;
    address?: string;
  };
  ownership_share: number;
  is_primary: number;
}

export interface LandParcel {
  id: number;
  survey_number: string;
  gat_number: string;
  khata_number: string;
  village_id: number;
  area_hectares: number;
  area_acres: number;
  land_type: string;
  boundary_status: 'Verified' | 'In Progress' | 'Discrepancy' | 'Pending';
  discrepancy_status: string;
  center_lat: number;
  center_lng: number;
  remarks?: string;
  last_survey_date?: string;
  owner_name?: string;
  village_name?: string;
  taluka_name?: string;
  district_name?: string;
  boundary_geojson?: string;
  old_boundary_geojson?: string;
  owners?: ParcelOwner[];
  crops?: CropRecord[];
  mutations?: MutationRecord[];
}

export interface KpiStats {
  total_parcels: number;
  surveyed_count: number;
  surveyed_pct: number;
  verified_count: number;
  verified_pct: number;
  discrepancy_count: number;
  discrepancy_pct: number;
  total_area_surveyed_ha: number;
  area_surveyed_pct: number;
}

export interface LandTypeItem {
  name: string;
  percentage: number;
  color: string;
  area_ha: number;
}

export interface AreaByTalukaItem {
  taluka: string;
  area_ha: number;
}

export interface RecentSurveyItem {
  id: number;
  date: string;
  survey_no: string;
  area_ha: number;
  status: string;
}

export interface DashboardStats {
  kpis: KpiStats;
  land_types: LandTypeItem[];
  area_by_taluka: AreaByTalukaItem[];
  recent_surveys: RecentSurveyItem[];
}

export interface Discrepancy {
  id: number;
  parcel_id: number;
  survey_id?: number;
  discrepancy_type: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'Open' | 'Under Review' | 'Resolved' | 'Dismissed';
  old_geometry_geojson?: string;
  new_geometry_geojson?: string;
  difference_geometry_geojson?: string;
  old_area_ha: number;
  new_area_ha: number;
  diff_area_ha: number;
  diff_percent: number;
  assigned_officer: string;
  detected_date: string;
  resolved_date?: string;
  resolution_notes?: string;
  survey_number?: string;
  gat_number?: string;
  owner_name?: string;
  village_name?: string;
}

export interface SurveyRecord {
  id: number;
  survey_number: string;
  parcel_id: number;
  surveyor_id: number;
  status: 'Draft' | 'In Progress' | 'Submitted' | 'Under Review' | 'Verified' | 'Rejected';
  survey_date: string;
  old_area_hectares: number;
  new_area_hectares: number;
  area_diff_hectares: number;
  area_diff_percent: number;
  gps_accuracy_meters: number;
  surveyor_remarks?: string;
  verification_remarks?: string;
  rejection_reason?: string;
  points?: Array<{
    id: number;
    point_order: number;
    latitude: number;
    longitude: number;
    elevation: number;
    accuracy: number;
    point_type: string;
    remarks?: string;
  }>;
}

export interface DocumentRecord {
  id: number;
  title: string;
  document_type: string;
  file_path: string;
  file_name: string;
  file_size_kb: number;
  mime_type: string;
  parcel_id?: number;
  uploaded_by: string;
  is_verified: boolean;
  ocr_extracted_text?: string;
  created_at: string;
}
