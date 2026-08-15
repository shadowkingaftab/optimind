import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../../components/navigation/Sidebar'

const DashboardLayout: React.FC = () => {
  const sidebarItems = [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Upload', href: '/upload' },
    { label: 'History', href: '/predictions' },
    { label: 'Profile', href: '/profile' },
    { label: 'Settings', href: '/settings' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:block">
        <Sidebar items={sidebarItems} />
      </aside>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  )
}

export default DashboardLayout
