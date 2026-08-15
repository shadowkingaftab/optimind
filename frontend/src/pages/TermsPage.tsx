import React from 'react'
import Card from '../components/common/Card'

const TermsPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
      <Card className="prose prose-sm max-w-none">
        <p>Last updated: August 2026</p>
        <p>By using EyeDx, you agree to these terms. Our AI-powered analysis is provided for informational purposes only and does not constitute medical advice.</p>
        <h2>Use of Service</h2>
        <p>You may use our service for personal, non-commercial purposes. You are responsible for ensuring that any uploaded images are yours to share.</p>
        <h2>Disclaimer</h2>
        <p>EyeDx is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider.</p>
      </Card>
    </div>
  )
}

export default TermsPage
