import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../../components/navigation/Sidebar'

const AdminLayout: React.FC = () => {
  const sidebarItems = [
    { label: 'Dashboard', href: '/admin' },
    { label: 'Users', href: '/admin/users' },
    { label: 'Models', href: '/admin/models' },
    { label: 'Audit Logs', href: '/admin/audit-logs' },
    { label: 'Health', href: '/admin/health' },
    { label: 'Performance', href: '/admin/performance' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-gray-800 text-white hidden md:block">
        <Sidebar items={sidebarItems} />
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default AdminLayout
