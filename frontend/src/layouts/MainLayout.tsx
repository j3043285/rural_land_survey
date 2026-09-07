import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  RefreshCw,
  FileText,
  Compass,
  FileBarChart,
  Users,
  Settings,
  Satellite,
  User,
  ChevronDown,
  Bell,
  MessageSquare
} from 'lucide-react';
import { api } from '../services/api';

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [sysStatus, setSysStatus] = useState<any>({
    gps_coordinates: { text: "19.0760° N, 72.8777° E" },
    last_sync: "12 Apr 2025, 14:32"
  });

  useEffect(() => {
    api.getSystemStatus().then(setSysStatus).catch(() => {});
    api.getNotifications().then(setNotifications).catch(() => {});
  }, []);

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/land-survey', label: 'Land Survey', icon: MapPin },
    { to: '/resurvey', label: 'Resurvey', icon: RefreshCw },
    { to: '/parcel-records', label: 'Parcel Records', icon: FileText },
    { to: '/field-survey', label: 'Field Survey', icon: Compass },
    { to: '/reports', label: 'Reports', icon: FileBarChart },
    { to: '/users', label: 'Users', icon: Users },
    { to: '/settings', label: 'Settings', icon: Settings },
    { to: '/grievances', label: 'Grievances', icon: MessageSquare },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f1f5f9]">
      {/* LEFT SIDEBAR - Deep Navy Blue Matching Reference Image */}
      <aside className="w-64 bg-[#0b1e36] text-white flex flex-col justify-between flex-shrink-0 z-30 select-none shadow-xl">
        <div>
          {/* Brand Logo & Header in Sidebar */}
          <div className="p-4 flex items-center gap-3 border-b border-[#1b3152]">
            <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400 shadow-sm">
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12c0 3.54 1.84 6.65 4.63 8.42.36-.6.76-1.18 1.21-1.72C5.6 17.38 4 14.88 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8c0 2.88-1.6 5.38-3.84 6.7.45.54.85 1.12 1.21 1.72C20.16 18.65 22 15.54 22 12c0-5.52-4.48-10-10-10zM12 6c-3.31 0-6 2.69-6 6 0 1.95.93 3.68 2.38 4.78.36-.5.77-.96 1.22-1.38C8.6 14.61 8 13.38 8 12c0-2.21 1.79-4 4-4s4 1.79 4 4c0 1.38-.6 2.61-1.6 3.4.45.42.86.88 1.22 1.38C17.07 15.68 18 13.95 18 12c0-3.31-2.69-6-6-6z" opacity="0.4" />
                <path d="M12 3c-4.97 0-9 4.03-9 9 0 2.12.74 4.07 1.97 5.61L12 8l7.03 9.61C20.26 16.07 21 14.12 21 12c0-4.97-4.03-9-9-9zm0 8a3 3 0 1 1 0 6 3 3 0 0 1 0-6z" />
              </svg>
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-wide leading-tight text-white">LandSetu</h1>
              <p className="text-[11px] text-sky-200/70 font-medium">Bhu-Abhilekh Portal</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.to;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-[13.5px] font-medium transition-all ${
                    isActive
                      ? 'bg-[#15345d] text-white shadow-sm font-semibold'
                      : 'text-slate-300 hover:bg-[#122847] hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {isActive && (
                    <span className="text-sky-400 text-xs font-bold">›</span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* BOTTOM SIDEBAR - Rural Landscape Silhouette Illustration */}
        <div className="p-4 relative border-t border-[#1b3152] bg-gradient-to-t from-[#071324] to-transparent">
          {/* Subtle Farm Silhouette Graphic */}
          <div className="h-16 mb-2 flex items-end justify-center opacity-30">
            <svg viewBox="0 0 200 60" className="w-full h-full fill-sky-200">
              <path d="M0,50 Q30,40 60,48 T120,44 T180,47 L200,50 L200,60 L0,60 Z" />
              <circle cx="45" cy="35" r="10" />
              <circle cx="55" cy="38" r="8" />
              <rect x="48" y="42" width="4" height="12" fill="#0b1e36" />
              <path d="M140,48 L145,40 L160,40 L165,48 Z" />
              <circle cx="145" cy="50" r="5" />
              <circle cx="160" cy="50" r="5" />
            </svg>
          </div>
          <div className="text-center">
            <p className="text-[12px] font-medium leading-snug text-slate-300">
              Better Land Records
            </p>
            <p className="text-[12px] font-medium leading-snug text-slate-300">
              for a Stronger Rural India
            </p>
          </div>
        </div>
      </aside>

      {/* MAIN CONTAINER */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* TOP HEADER - Exact Banner from Screenshot */}
        <header className="h-14 bg-[#0b1e36] text-white flex items-center justify-between px-6 border-b border-[#183459] shadow-sm z-20 flex-shrink-0">
          {/* Title & Subtitle */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400">
              <span className="text-base">🌱</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-[15px] tracking-tight text-white">
                  Rural Agricultural Land Survey / Resurvey
                </span>
              </div>
              <p className="text-[11px] text-slate-300 tracking-wider">
                Accurate <span className="text-sky-400">•</span> Transparent <span className="text-sky-400">•</span> Digital India
              </p>
            </div>
          </div>

          {/* Right Status Indicators */}
          <div className="flex items-center gap-6 text-xs">
            {/* GPS Connected */}
            <div className="flex items-center gap-2 bg-[#122847] px-3 py-1.5 rounded-full border border-sky-900/60">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <div>
                <span className="font-semibold text-white block text-[11px] leading-tight">GPS Connected</span>
                <span className="text-[10px] text-slate-300 font-mono">
                  {sysStatus?.gps_coordinates?.text || "19.0760° N, 72.8777° E"}
                </span>
              </div>
            </div>

            {/* Last Sync */}
            <div className="flex items-center gap-2">
              <Satellite className="w-4 h-4 text-sky-400" />
              <div>
                <span className="text-[10px] text-slate-400 block leading-tight">Last Sync</span>
                <span className="font-medium text-slate-200 text-[11px]">
                  {sysStatus?.last_sync || "12 Apr 2025, 14:32"}
                </span>
              </div>
            </div>

            {/* Notifications Button */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-1.5 rounded-lg hover:bg-[#15345d] text-slate-300 hover:text-white transition"
              >
                <Bell className="w-4 h-4" />
                {notifications.some(n => !n.is_read) && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-ping" />
                )}
              </button>

              {/* Notification dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-slate-200 text-slate-800 p-3 z-50">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                    <span className="font-semibold text-xs text-slate-900">Notifications & Alerts</span>
                    <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                      {notifications.length} New
                    </span>
                  </div>
                  <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 mt-2">
                    {notifications.map((n) => (
                      <div key={n.id} className="py-2 text-[11px]">
                        <p className="font-semibold text-slate-900">{n.title}</p>
                        <p className="text-slate-600 mt-0.5">{n.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* User Profile */}
            <div className="flex items-center gap-2 pl-2 border-l border-[#1b3152]">
              <div className="w-7 h-7 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-xs shadow-inner">
                <User className="w-3.5 h-3.5" />
              </div>
              <div className="text-left">
                <div className="flex items-center gap-1">
                  <span className="font-semibold text-slate-100 text-xs">Admin</span>
                  <ChevronDown className="w-3 h-3 text-slate-400" />
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* PAGE CONTENT CONTAINER */}
        <main className="flex-1 overflow-y-auto bg-[#f1f5f9]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
