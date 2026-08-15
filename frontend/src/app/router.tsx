import { createBrowserRouter, Navigate } from 'react-router-dom';
import React from 'react';

// Placeholder pages - Replace with actual implementations
const DashboardPage = () => <div className="p-8 text-clinical-text">EyeDx Clinical Dashboard</div>;
const PatientAnalysisPage = () => <div className="p-8 text-clinical-text">Retinal Scan Analysis</div>;
const NotFoundPage = () => <div className="p-8 text-red-600">404 - Resource Not Found</div>;

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/dashboard',
    element: <DashboardPage />,
  },
  {
    path: '/analysis/:patientId',
    element: <PatientAnalysisPage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
