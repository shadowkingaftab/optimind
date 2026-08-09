import React from 'react';

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  label?: string;
  fullScreen?: boolean;
  variant?: 'primary' | 'white' | 'muted';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  label, 
  fullScreen = false,
  variant = 'primary'
}) => {
  const dimensions = {
    xs: 'w-3 h-3 border-[1.5px]',
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-[3px]',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-4',
  };

  const colors = {
    primary: 'border-teal-600 border-t-transparent',
    white: 'border-white border-t-transparent',
    muted: 'border-slate-300 border-t-transparent',
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div 
        className={`${dimensions[size]} ${colors[variant]} rounded-full animate-spin`} 
        role="status"
        aria-label={label || "Loading"}
      />
      {label && (
        <p className={`text-sm font-medium animate-pulse ${
          variant === 'white' ? 'text-white' : 'text-slate-500'
        }`}>
          {label}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-[400px] w-full flex items-center justify-center bg-slate-50/50 rounded-xl">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
