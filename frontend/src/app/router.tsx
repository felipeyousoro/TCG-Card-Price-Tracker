import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import RequireAuth from '../features/auth/RequireAuth'
import LoginPage from '../features/auth/pages/LoginPage'
import HomePage from '../features/home/pages/HomePage'
import ImportersPage from '../features/importers/pages/ImportersPage'
import SettingsPage from '../features/settings/pages/SettingsPage'
import AppShell from '../layouts/AppShell'
import AuthLayout from '../layouts/AuthLayout'

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route element={<RequireAuth />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/settings/importers" element={<ImportersPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
