import React from 'react'
import Card from '../components/common/Card'
import UserTable from '../components/admin/UserTable'
import ModelVersionTable from '../components/admin/ModelVersionTable'
import AuditLogTable from '../components/admin/AuditLogTable'
import SystemHealthPanel from '../components/admin/SystemHealthPanel'
import PerformanceDashboard from '../components/admin/PerformanceDashboard'

const mockUsers = [
  { id: '1', name: 'Admin User', email: 'admin@eyedx.com', role: 'admin' as const, status: 'active' as const, createdAt: new Date().toISOString() },
  { id: '2', name: 'Regular User', email: 'user@example.com', role: 'user' as const, status: 'active' as const, createdAt: new Date().toISOString() }
]

const mockVersions = [
  { id: '1', name: 'EyeDx Retina', version: '2.1.0', status: 'active' as const, accuracy: 0.96, deployedAt: new Date().toISOString() },
  { id: '2', name: 'EyeDx Retina', version: '2.0.0', status: 'staging' as const, accuracy: 0.94, deployedAt: new Date().toISOString() }
]

const mockLogs = [
  { id: '1', action: 'LOGIN', user: 'admin@eyedx.com', timestamp: new Date().toISOString(), details: 'Successful login', ipAddress: '127.0.0.1' }
]

const mockHealth = [
  { name: 'API', status: 'healthy' as const, uptime: '99.9%', lastChecked: new Date().toISOString() },
  { name: 'Model Service', status: 'healthy' as const, uptime: '99.8%', lastChecked: new Date().toISOString() }
]

const AdminPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
      <PerformanceDashboard
        metrics={[
          { title: 'Total Users', value: 1240, change: 12 },
          { title: 'Predictions', value: 5680, change: 8 },
          { title: 'Avg Latency', value: 240, unit: 'ms', change: -5 },
          { title: 'Uptime', value: '99.9', unit: '%', change: 0 }
        ]}
      />
      <SystemHealthPanel metrics={mockHealth} />
      <Card>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Users</h2>
        <UserTable users={mockUsers} />
      </Card>
      <Card>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Model Versions</h2>
        <ModelVersionTable versions={mockVersions} />
      </Card>
      <Card>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Audit Logs</h2>
        <AuditLogTable logs={mockLogs} />
      </Card>
    </div>
  )
}

export default AdminPage
