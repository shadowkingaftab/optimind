import React from 'react'
import { Link } from 'react-router-dom'
import Card from '../components/common/Card'
import Button from '../components/common/Button'

const DashboardPage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <h3 className="text-lg font-medium text-gray-900">Recent Predictions</h3>
          <p className="mt-2 text-3xl font-bold text-indigo-600">12</p>
          <p className="mt-1 text-sm text-gray-500">Total predictions this month</p>
          <Link to="/predictions">
            <Button variant="outline" className="mt-4 w-full">View History</Button>
          </Link>
        </Card>
        <Card>
          <h3 className="text-lg font-medium text-gray-900">Account Status</h3>
          <p className="mt-2 text-sm text-gray-600">Active</p>
          <Link to="/settings">
            <Button variant="outline" className="mt-4 w-full">Manage Settings</Button>
          </Link>
        </Card>
        <Card>
          <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          <div className="mt-4 space-y-2">
            <Link to="/upload">
              <Button className="w-full">New Analysis</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage
