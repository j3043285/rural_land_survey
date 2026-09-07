import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { LandSurvey } from './pages/LandSurvey';
import { Resurvey } from './pages/Resurvey';
import { ParcelRecords } from './pages/ParcelRecords';
import { FieldSurvey } from './pages/FieldSurvey';
import { Reports } from './pages/Reports';
import { Users } from './pages/Users';
import { Settings } from './pages/Settings';
import { Grievances } from './pages/Grievances';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="land-survey" element={<LandSurvey />} />
          <Route path="resurvey" element={<Resurvey />} />
          <Route path="parcel-records" element={<ParcelRecords />} />
          <Route path="field-survey" element={<FieldSurvey />} />
          <Route path="reports" element={<Reports />} />
          <Route path="users" element={<Users />} />
          <Route path="settings" element={<Settings />} />
          <Route path="grievances" element={<Grievances />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
