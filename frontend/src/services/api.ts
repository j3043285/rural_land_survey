import {
  District,
  Taluka,
  Village,
  LandParcel,
  DashboardStats,
  Discrepancy,
  SurveyRecord,
  DocumentRecord
} from '../types';

// Use environment variable for API base URL in production
const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options?.headers || {})
  };

  // Ensure full URL in production
  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;
  
  const response = await fetch(fullUrl, {
    ...options,
    headers
  });

  if (!response.ok) {
    let errorMsg = `Error ${response.status}: ${response.statusText}`;
    try {
      const err = await response.json();
      if (err.detail) errorMsg = err.detail;
    } catch {}
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // Locations
  getDistricts: () => fetchJSON<District[]>('/districts'),
  getTalukas: (districtId?: number) =>
    fetchJSON<Taluka[]>(`/talukas${districtId ? `?district_id=${districtId}` : ''}`),
  getVillages: (talukaId?: number) =>
    fetchJSON<Village[]>(`/villages${talukaId ? `?taluka_id=${talukaId}` : ''}`),
  getGrievances: () => fetchJSON<any[]>('/grievances'),
  createGrievance: (data: any) => fetchJSON<any>('/grievances', { method: 'POST', body: JSON.stringify(data) }),
  registerUser: (data: any) => fetchJSON<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  // Parcels
  getParcels: (villageId?: number) =>
    fetchJSON<LandParcel[]>(`/parcels${villageId ? `?village_id=${villageId}` : ''}`),
  searchParcels: (q: string, villageId?: number) =>
    fetchJSON<LandParcel[]>(`/parcels/search?q=${encodeURIComponent(q)}${villageId ? `&village_id=${villageId}` : ''}`),
  getParcelDetail: (id: number) => fetchJSON<LandParcel>(`/parcels/${id}`),
  getVillageGeoJSON: (villageId: number) =>
    fetchJSON<any>(`/parcels/geojson/village/${villageId}`),
  updateParcel: (id: number, data: Partial<LandParcel>) =>
    fetchJSON<LandParcel>(`/parcels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    }),
  compareParcelBoundary: (id: number) =>
    fetchJSON<any>(`/parcels/${id}/compare-boundary`, { method: 'POST' }),

  // Surveys
  getSurveys: (parcelId?: number) =>
    fetchJSON<SurveyRecord[]>(`/surveys${parcelId ? `?parcel_id=${parcelId}` : ''}`),
  createSurvey: (data: any) =>
    fetchJSON<SurveyRecord>('/surveys', {
      method: 'POST',
      body: JSON.stringify(data)
    }),
  submitSurvey: (id: number, remarks?: string) =>
    fetchJSON<SurveyRecord>(`/surveys/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ remarks })
    }),
  verifySurvey: (id: number, remarks?: string) =>
    fetchJSON<SurveyRecord>(`/surveys/${id}/verify`, {
      method: 'POST',
      body: JSON.stringify({ remarks })
    }),
  rejectSurvey: (id: number, remarks?: string) =>
    fetchJSON<SurveyRecord>(`/surveys/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ remarks })
    }),

  // Discrepancies
  getDiscrepancies: (status?: string, villageId?: number) =>
    fetchJSON<Discrepancy[]>(
      `/discrepancies?${status ? `status=${status}&` : ''}${villageId ? `village_id=${villageId}` : ''}`
    ),
  resolveDiscrepancy: (id: number, resolution_notes: string) =>
    fetchJSON<Discrepancy>(`/discrepancies/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_notes, status: 'Resolved' })
    }),

  // Documents
  getDocuments: (parcelId?: number) =>
    fetchJSON<DocumentRecord[]>(`/documents${parcelId ? `?parcel_id=${parcelId}` : ''}`),
  uploadDocument: async (formData: FormData): Promise<DocumentRecord> => {
    const token = localStorage.getItem('access_token');
    const fullUrl = `/documents/upload`.startsWith('http') ? `/documents/upload` : `${API_BASE}/documents/upload`;
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData
    });
    if (!response.ok) throw new Error('Upload failed');
    return response.json();
  },

  // Dashboard Analytics
  getDashboardStats: (villageId?: number) =>
    fetchJSON<DashboardStats>(`/dashboard/statistics${villageId ? `?village_id=${villageId}` : ''}`),

  // Reports
  getParcelPdfUrl: (parcelId: number) => `${API_BASE.replace('/api', '')}/api/reports/parcel/${parcelId}/pdf`,

  // System & AI
  getSystemStatus: () => fetchJSON<any>('/system/status'),
  getNotifications: () => fetchJSON<any[]>('/system/notifications'),
  aiQuery: (query: string) =>
    fetchJSON<any>('/ai/query', {
      method: 'POST',
      body: JSON.stringify({ query })
    }),
  
  // Blockchain Verification
  getBlockchainVerification: (parcelId: number) =>
    fetchJSON<any>(`/blockchain/verify/${parcelId}`),
  generateBlockchainCertificate: (parcelId: number) =>
    fetchJSON<any>(`/blockchain/generate/${parcelId}`, { method: 'POST' }),
  
  // Dispute Prediction
  predictDispute: (parcelId: number) =>
    fetchJSON<any>(`/dispute-prediction/predict/${parcelId}`),
  getDisputeRiskAnalysis: (villageId?: number) =>
    fetchJSON<any>(`/dispute-prediction/analysis${villageId ? `?village_id=${villageId}` : ''}`)
};
