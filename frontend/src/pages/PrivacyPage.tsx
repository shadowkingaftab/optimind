import React from 'react'
import Card from '../components/common/Card'

const PrivacyPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
      <Card className="prose prose-sm max-w-none">
        <p>Last updated: August 2026</p>
        <p>EyeDx is committed to protecting your privacy. This policy explains how we collect, use, and safeguard your information when you use our AI-powered eye disease detection service.</p>
        <h2>Information We Collect</h2>
        <p>We collect eye images and basic account information to provide our analysis services.</p>
        <h2>How We Use Your Information</h2>
        <p>Your data is used solely for generating predictions and improving our models. We do not share your personal health data with third parties.</p>
        <h2>Data Security</h2>
        <p>All data is encrypted in transit and at rest. We implement industry-standard security measures to protect your information.</p>
      </Card>
    </div>
  )
}

export default PrivacyPage
