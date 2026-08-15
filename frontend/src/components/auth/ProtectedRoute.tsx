import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'

interface ProtectedRouteProps {
  children: React.ReactNode
  isAuthenticated?: boolean
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, isAuthenticated = false }) => {
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
