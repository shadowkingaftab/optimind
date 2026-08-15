import React from 'react';
import { AlertTriangle, CheckCircle, Info } from '../../assets/icons';

interface ResultCardProps {
  diagnosis: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'normal';
  findings: string[];
  recommendation?: string;
}

const severityStyles = {
  normal: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: CheckCircle },
  low: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', icon: Info },
  medium: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: AlertTriangle },
  high: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: AlertTriangle },
};

const ResultCard: React.FC<ResultCardProps> = ({ diagnosis, confidence, severity, findings, recommendation }) => {
  const style = severityStyles[severity];
  const Icon = style.icon;

  return (
    <div className={`rounded-xl border ${style.border} ${style.bg} p-5 transition-all`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-white/60 ${style.text}`}>
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <h3 className={`font-bold text-lg ${style.text}`}>{diagnosis}</h3>
            <p className="text-xs opacity-80 font-medium uppercase tracking-wide">Primary Detection</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-slate-800">{(confidence * 100).toFixed(1)}%</p>
          <p className="text-[10px] text-slate-500 font-semibold uppercase">Confidence</p>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase mb-1.5">Key Findings</p>
          <ul className="space-y-1.5">
            {findings.map((finding, i) => (
              <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                <span className={`mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${style.text.replace('text-', 'bg-')}`} />
                {finding}
              </li>
            ))}
          </ul>
        </div>

        {recommendation && (
          <div className="mt-4 pt-4 border-t border-black/5">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Clinical Recommendation</p>
            <p className="text-sm text-slate-800 font-medium leading-relaxed">{recommendation}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
