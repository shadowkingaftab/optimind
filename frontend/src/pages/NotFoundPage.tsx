import React from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/common/Button'

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900">404</h1>
        <p className="mt-4 text-xl text-gray-600">Page not found</p>
        <Link to="/">
          <Button className="mt-8">Go Home</Button>
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage
