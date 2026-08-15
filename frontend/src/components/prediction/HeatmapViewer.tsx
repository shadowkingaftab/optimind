import React from 'react'

interface HeatmapViewerProps {
  imageUrl: string
  heatmapUrl?: string
  opacity?: number
}

const HeatmapViewer: React.FC<HeatmapViewerProps> = ({
  imageUrl,
  heatmapUrl,
  opacity = 0.5
}) => {
  return (
    <div className="relative inline-block">
      <img src={imageUrl} alt="Eye scan" className="max-w-full h-auto rounded-lg" />
      {heatmapUrl && (
        <img
          src={heatmapUrl}
          alt="Heatmap overlay"
          className="absolute top-0 left-0 max-w-full h-auto rounded-lg mix-blend-multiply"
          style={{ opacity }}
        />
      )}
      <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
        Heatmap overlay
      </div>
    </div>
  )
}

export default HeatmapViewer
