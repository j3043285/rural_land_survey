import React, { useState } from 'react';
import { Users as UsersIcon, Shield, CheckCircle2, UserPlus } from 'lucide-react';
import { api } from '../services/api';

export const Users: React.FC = () => {
  const [users, setUsers] = useState([
    {
      id: 1,
      name: 'Rajendra Deshmukh',
      username: 'admin',
      role: 'ADMIN',
      badge: 'MH-ADM-001',
      email: 'admin@landsetu.gov.in',
      phone: '+91 98220 12345',
      status: 'Active'
    },
    {
      id: 2,
      name: 'Bhumi Abhilekh Surveyor',
      username: 'surveyor',
      role: 'SURVEYOR',
      badge: 'MH-SURV-089',
      email: 'surveyor@landsetu.gov.in',
      phone: '+91 94231 67890',
      status: 'Active'
    },
    {
      id: 3,
      name: 'Circle Officer / Verifier',
      username: 'verifier',
      role: 'VERIFIER',
      badge: 'MH-VERIF-042',
      email: 'verifier@landsetu.gov.in',
      phone: '+91 98810 54321',
      status: 'Active'
    },
    {
      id: 4,
      name: 'Public Citizen Viewer',
      username: 'viewer',
      role: 'VIEWER',
      badge: 'MH-PUB-101',
      email: 'viewer@landsetu.gov.in',
      phone: '+91 97654 11223',
      status: 'Active'
    }
  ]);
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ full_name: '', email: '', username: '', password: '', role: 'SURVEYOR', phone: '', badge_number: '' });

  const createUser = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      const created = await api.registerUser(form);
      setUsers((current) => [...current, { id: created.id, name: created.full_name, username: created.username, role: created.role, badge: created.badge_number || '-', email: created.email, phone: created.phone || '-', status: created.is_active ? 'Active' : 'Inactive' }]);
      setForm({ full_name: '', email: '', username: '', password: '', role: 'SURVEYOR', phone: '', badge_number: '' });
      setShowForm(false);
      setMessage(`User ${created.username} created with role ${created.role}.`);
    } catch (error: any) {
      setMessage(error.message || 'Unable to create user.');
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6 text-xs">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <UsersIcon className="w-5 h-5 text-blue-600" />
            <span>User & Access Control (RBAC)</span>
          </h1>
          <p className="text-slate-500">Authorized survey officers, circle verifiers, and tahsil administrators</p>
        </div>
        <button onClick={() => setShowForm((current) => !current)} className="flex items-center gap-2 bg-blue-600 text-white px-3 py-2 rounded-lg font-bold text-xs hover:bg-blue-700"><UserPlus className="w-4 h-4" />Add User</button>
      </div>

      {message && <div className="bg-sky-50 border border-sky-200 text-sky-800 rounded-lg px-3 py-2">{message}</div>}

      {showForm && <form onSubmit={createUser} className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200 grid grid-cols-1 md:grid-cols-2 gap-3">
        <input required placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="border rounded-lg p-2" />
        <input required type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="border rounded-lg p-2" />
        <input required placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} className="border rounded-lg p-2" />
        <input required type="password" placeholder="Temporary password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="border rounded-lg p-2" />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="border rounded-lg p-2 font-semibold"><option value="SUPER_ADMIN">Super Admin</option><option value="ADMIN">Admin</option><option value="SURVEYOR">Surveyor</option><option value="VERIFIER">Verifier</option><option value="VIEWER">Viewer</option></select>
        <input placeholder="Badge number" value={form.badge_number} onChange={(e) => setForm({ ...form, badge_number: e.target.value })} className="border rounded-lg p-2" />
        <input placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="border rounded-lg p-2" />
        <button className="bg-emerald-600 text-white rounded-lg p-2 font-bold">Create user</button>
      </form>}

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-500 font-semibold text-[11px] border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Officer Name</th>
              <th className="py-3 px-4">Role</th>
              <th className="py-3 px-4">Badge ID</th>
              <th className="py-3 px-4">Official Email</th>
              <th className="py-3 px-4">Contact</th>
              <th className="py-3 px-4 text-center">Account Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {users.map((u) => (
              <tr key={u.id} className="hover:bg-slate-50 transition">
                <td className="py-3 px-4 font-bold text-slate-900">{u.name}</td>
                <td className="py-3 px-4">
                  <span className={`inline-flex items-center gap-1 font-bold text-[10px] px-2 py-0.5 rounded-full ${
                    u.role === 'ADMIN'
                      ? 'bg-purple-100 text-purple-700'
                      : u.role === 'SURVEYOR'
                      ? 'bg-blue-100 text-blue-700'
                      : u.role === 'VERIFIER'
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-slate-100 text-slate-700'
                  }`}>
                    <Shield className="w-3 h-3" />
                    <span>{u.role}</span>
                  </span>
                </td>
                <td className="py-3 px-4 font-mono font-semibold text-slate-700">{u.badge}</td>
                <td className="py-3 px-4 text-slate-600">{u.email}</td>
                <td className="py-3 px-4 text-slate-600">{u.phone}</td>
                <td className="py-3 px-4 text-center">
                  <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold text-[11px]">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Active</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
