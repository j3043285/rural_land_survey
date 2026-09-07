import React, { FormEvent, useEffect, useState } from 'react';
import { CheckCircle2, Clock3, FileWarning, MessageSquare, Send } from 'lucide-react';
import { api } from '../services/api';

type Grievance = {
  id: number;
  ticket_number: string;
  parcel_id?: number | null;
  farmer_name: string;
  farmer_phone: string;
  preferred_language: string;
  grievance_type: string;
  description: string;
  status: string;
  assigned_officer?: string | null;
  resolution_notes?: string | null;
  due_date: string;
  created_at: string;
};

const statusStyles: Record<string, string> = {
  Open: 'bg-amber-50 text-amber-700 border-amber-200',
  'Under Review': 'bg-blue-50 text-blue-700 border-blue-200',
  'Field Visit Required': 'bg-orange-50 text-orange-700 border-orange-200',
  Resolved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Rejected: 'bg-red-50 text-red-700 border-red-200'
};

export const Grievances: React.FC = () => {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [form, setForm] = useState({
    farmer_name: '',
    farmer_phone: '',
    preferred_language: 'Marathi',
    grievance_type: 'Boundary dispute',
    parcel_id: '',
    description: ''
  });
  const [message, setMessage] = useState('');

  const loadGrievances = () => api.getGrievances().then(setGrievances).catch(() => setMessage('Unable to load grievance tickets.'));

  useEffect(() => {
    loadGrievances();
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const created = await api.createGrievance({
        ...form,
        parcel_id: form.parcel_id ? Number(form.parcel_id) : null
      });
      setGrievances((current) => [created, ...current]);
      setForm({ ...form, farmer_name: '', farmer_phone: '', parcel_id: '', description: '' });
      setMessage(`Ticket ${created.ticket_number} submitted successfully.`);
    } catch (error: any) {
      setMessage(error.message || 'Unable to submit grievance.');
    }
  };

  return (
    <div className="p-4 space-y-4 max-w-[1600px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-[0.18em] font-bold text-sky-600">Citizen Services</p>
          <h1 className="text-xl font-black text-slate-900 mt-1">Farmer Grievances</h1>
          <p className="text-xs text-slate-500 mt-1">Submit a parcel issue and track its official resolution.</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl px-4 py-3 flex items-center gap-3">
          <MessageSquare className="w-5 h-5 text-sky-600" />
          <div><p className="text-[10px] uppercase text-slate-400 font-bold">Open tickets</p><p className="text-lg font-black text-slate-900">{grievances.filter((item) => item.status !== 'Resolved' && item.status !== 'Rejected').length}</p></div>
        </div>
      </div>

      {message && <div className="bg-sky-50 border border-sky-200 text-sky-800 rounded-lg px-3 py-2 text-xs">{message}</div>}

      <div className="grid grid-cols-1 xl:grid-cols-[380px_1fr] gap-4 items-start">
        <form onSubmit={submit} className="bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-sm">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-100"><FileWarning className="w-4 h-4 text-orange-500" /><h2 className="font-bold text-sm text-slate-900">Submit a grievance</h2></div>
          <input required placeholder="Farmer name" value={form.farmer_name} onChange={(e) => setForm({ ...form, farmer_name: e.target.value })} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:ring-1 focus:ring-sky-500" />
          <input required placeholder="Mobile number" value={form.farmer_phone} onChange={(e) => setForm({ ...form, farmer_phone: e.target.value })} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none focus:ring-1 focus:ring-sky-500" />
          <div className="grid grid-cols-2 gap-2">
            <select value={form.preferred_language} onChange={(e) => setForm({ ...form, preferred_language: e.target.value })} className="border border-slate-200 rounded-lg px-2 py-2 text-xs"><option>Marathi</option><option>Hindi</option><option>English</option></select>
            <input type="number" min="1" placeholder="Parcel ID (optional)" value={form.parcel_id} onChange={(e) => setForm({ ...form, parcel_id: e.target.value })} className="border border-slate-200 rounded-lg px-3 py-2 text-xs outline-none" />
          </div>
          <select value={form.grievance_type} onChange={(e) => setForm({ ...form, grievance_type: e.target.value })} className="w-full border border-slate-200 rounded-lg px-2 py-2 text-xs"><option>Boundary dispute</option><option>Area mismatch</option><option>Ownership or mutation</option><option>Record correction</option><option>Other</option></select>
          <textarea required minLength={10} rows={5} placeholder="Describe the issue and the action you are requesting" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-xs resize-none outline-none focus:ring-1 focus:ring-sky-500" />
          <button className="w-full bg-sky-600 hover:bg-sky-700 text-white rounded-lg py-2.5 text-xs font-bold flex items-center justify-center gap-2"><Send className="w-3.5 h-3.5" />Submit ticket</button>
        </form>

        <div className="space-y-3">
          {grievances.length === 0 ? <div className="bg-white border border-dashed border-slate-300 rounded-xl p-10 text-center text-xs text-slate-500">No grievance tickets have been submitted.</div> : grievances.map((item) => (
            <article key={item.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div><p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">{item.ticket_number}</p><h3 className="font-bold text-sm text-slate-900 mt-1">{item.grievance_type} <span className="font-normal text-slate-500">by {item.farmer_name}</span></h3></div>
                <span className={`px-2 py-1 rounded-full border text-[10px] font-bold ${statusStyles[item.status] || 'bg-slate-50 text-slate-600 border-slate-200'}`}>{item.status}</span>
              </div>
              <p className="text-xs text-slate-600 mt-3 leading-relaxed">{item.description}</p>
              <div className="flex flex-wrap items-center gap-4 mt-4 pt-3 border-t border-slate-100 text-[10px] text-slate-500">
                <span className="flex items-center gap-1"><Clock3 className="w-3.5 h-3.5" />Due {new Date(item.due_date).toLocaleDateString()}</span>
                {item.parcel_id && <span>Parcel #{item.parcel_id}</span>}
                {item.assigned_officer && <span>Officer: {item.assigned_officer}</span>}
                {item.status === 'Resolved' && <span className="flex items-center gap-1 text-emerald-700"><CheckCircle2 className="w-3.5 h-3.5" />Resolution recorded</span>}
              </div>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
};