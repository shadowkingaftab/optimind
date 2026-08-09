import React, { useRef } from 'react';

interface ScanViewerProps {
  imageUrl: string;
  overlays?: Array<{ x: number; y: number; radius: number; label: string; confidence: number }>;
  zoomLevel?: number;
}

const ScanViewer: React.FC<ScanViewerProps> = ({ imageUrl, overlays = [], zoomLevel = 1 }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <div 
      ref={containerRef}
      className="relative w-full aspect-square bg-slate-900 rounded-xl overflow-hidden border border-slate-800 group cursor-crosshair"
    >
      {/* Medical Imaging Grid Background */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ backgroundImage: 'radial-gradient(circle, #ffffff 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
      </div>

      <img 
        src={imageUrl} 
        alt="Retinal Scan" 
        className="w-full h-full object-contain transition-transform duration-300 ease-out"
        style={{ transform: `scale(${zoomLevel})` }}
      />

      {/* AI Detection Overlays */}
      {overlays.map((overlay, idx) => (
        <div 
          key={idx}
          className="absolute border-2 border-amber-400 rounded-full bg-amber-400/10 backdrop-blur-[1px] transition-all hover:bg-amber-400/20 cursor-pointer group/marker"
          style={{
            left: `${overlay.x}%`,
            top: `${overlay.y}%`,
            width: `${overlay.radius}%`,
            height: `${overlay.radius}%`,
            transform: 'translate(-50%, -50%)',
          }}
        >
          {/* Tooltip */}
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-slate-900 text-white text-[10px] rounded opacity-0 group-hover/marker:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
            {overlay.label} ({(overlay.confidence * 100).toFixed(1)}%)
          </div>
        </div>
      ))}

      {/* DICOM-style Overlay Info */}
      <div className="absolute top-4 left-4 text-[10px] font-mono text-teal-400/80 pointer-events-none select-none">
        <p>PATIENT: ANONYMIZED</p>
        <p>MODALITY: OCT-FUNDUS</p>
        <p>ZOOM: {(zoomLevel * 100).toFixed(0)}%</p>
      </div>
    </div>
  );
};

export default ScanViewer;
