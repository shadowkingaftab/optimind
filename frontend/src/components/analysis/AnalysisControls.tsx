import React from 'react';
import Button from '../common/Button';
import { Download, Share, Refresh, Printer } from '../../assets/icons';

interface AnalysisControlsProps {
  onRerun: () => void;
  onExport: () => void;
  isProcessing: boolean;
  canEdit?: boolean;
}

const AnalysisControls: React.FC<AnalysisControlsProps> = ({ onRerun, onExport, isProcessing, canEdit = true }) => {
  return (
    <div className="flex flex-wrap items-center gap-3 p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
      <div className="flex items-center gap-2 flex-1 min-w-[200px]">
        <Button 
          variant="primary" 
          onClick={onRerun} 
          isLoading={isProcessing}
          icon={<Refresh className="w-4 h-4" />}
          disabled={!canEdit}
        >
          {isProcessing ? 'Analyzing...' : 'Re-analyze Scan'}
        </Button>
        
        <Button variant="secondary" icon={<Printer className="w-4 h-4" />}>
          Print Report
        </Button>
      </div>
      
      <div className="h-8 w-px bg-slate-200 hidden sm:block"></div>
      
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm" icon={<Share className="w-3 h-3" />}>
          Share
        </Button>
        <Button variant="secondary" size="sm" onClick={onExport} icon={<Download className="w-3 h-3" />}>
          Export DICOM
        </Button>
      </div>
    </div>
  );
};

export default AnalysisControls;
