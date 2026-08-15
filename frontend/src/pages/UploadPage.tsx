import React from 'react'
import EyeImageUploader from '../components/upload/EyeImageUploader'
import Card from '../components/common/Card'

const UploadPage: React.FC = () => {
  const handleUpload = async (files: File[]) => {
    console.log('Uploading files:', files)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Eye Image</h1>
      <Card>
        <EyeImageUploader onUpload={handleUpload} />
      </Card>
    </div>
  )
}

export default UploadPage
