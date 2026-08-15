import React from 'react'

const ServiceUnavailablePage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900">503</h1>
        <p className="mt-4 text-xl text-gray-600">Service Unavailable</p>
        <p className="mt-2 text-gray-500">We are experiencing technical difficulties. Please try again later.</p>
      </div>
    </div>
  )
}

export default ServiceUnavailablePage
