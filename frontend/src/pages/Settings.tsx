import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, Check, Database, Shield } from 'lucide-react';

export const Settings: React.FC = () => {
  const [provider, setProvider] = useState('mock');
  const [threshold, setThreshold] = useState('2.0');
  const [apiUrl, setApiUrl] = useState('https://mahabhulekh.maharashtra.gov.in/api/v1');
  const [apiKey, setApiKey] = useState('••••••••••••••••••••••••');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6 text-xs text-slate-800">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-blue-600" />
          <span>System & Integration Settings</span>
        </h1>
        <p className="text-slate-500">Configure official Maharashtra land-record adapters, boundary discrepancy limits, and DGPS parameters</p>
      </div>

      <form onSubmit={handleSave} className="space-y-5">
        {/* 1. Government Data Integration Adapter */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900 border-b border-slate-100 pb-2">
            <Database className="w-4 h-4 text-blue-600" />
            <span>Maharashtra Land Record Integration Layer</span>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Active Land Data Provider</label>
            <div className="grid grid-cols-2 gap-3">
              <label
                onClick={() => setProvider('mock')}
                className={`p-3 rounded-xl border cursor-pointer transition flex flex-col ${
                  provider === 'mock'
                    ? 'border-blue-600 bg-blue-50/50 text-blue-900'
                    : 'border-slate-200 hover:bg-slate-50'
                }`}
              >
                <span className="font-bold">MockLandRecordProvider (Demo Mode)</span>
                <span className="text-[11px] text-slate-500 mt-0.5">
                  Safe synthetic demo records for Pimpalgaon, Yeola, Nashik. No live credentials required.
                </span>
              </label>

              <label
                onClick={() => setProvider('official')}
                className={`p-3 rounded-xl border cursor-pointer transition flex flex-col ${
                  provider === 'official'
                    ? 'border-blue-600 bg-blue-50/50 text-blue-900'
                    : 'border-slate-200 hover:bg-slate-50'
                }`}
              >
                <span className="font-bold">OfficialLandRecordProvider (Mahabhulekh)</span>
                <span className="text-[11px] text-slate-500 mt-0.5">
                  Connects to authorized Maharashtra Revenue Department REST & OAuth endpoints.
                </span>
              </label>
            </div>
          </div>

          {provider === 'official' && (
            <div className="space-y-3 pt-2">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Official API Gateway URL</label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2 font-mono text-slate-800"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Authorized Department API Key / JWT Token</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2 font-mono text-slate-800"
                />
              </div>
            </div>
          )}
        </div>

        {/* 2. Geometric Discrepancy Threshold */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900 border-b border-slate-100 pb-2">
            <Shield className="w-4 h-4 text-amber-600" />
            <span>Boundary Discrepancy Tolerance Limits</span>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">
              Permissible Area Deviation Threshold (%)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                step="0.1"
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                className="w-32 border border-slate-300 rounded-lg p-2 font-bold text-slate-900"
              />
              <span className="text-slate-500 text-[11px]">
                Any resurvey exceeding {threshold}% variance against 7/12 records triggers a boundary discrepancy audit.
              </span>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded-xl shadow-sm transition"
          >
            {saved ? (
              <>
                <Check className="w-4 h-4" />
                <span>Settings Saved!</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Configuration</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
