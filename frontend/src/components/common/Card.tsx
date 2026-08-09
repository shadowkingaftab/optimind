import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
  variant?: 'default' | 'elevated' | 'bordered';
}

const Card: React.FC<CardProps> = ({ 
  title, 
  subtitle, 
  action, 
  children, 
  className = '', 
  noPadding = false,
  variant = 'default'
}) => {
  const baseStyles = "bg-white rounded-xl overflow-hidden transition-all duration-200";
  
  const variants = {
    default: "border border-slate-200 shadow-sm",
    elevated: "border border-slate-100 shadow-md hover:shadow-lg",
    bordered: "border-2 border-slate-200 shadow-none"
  };

  return (
    <div className={`${baseStyles} ${variants[variant]} ${className}`}>
      {(title || action) && (
        <div className="px-6 py-4 border-b border-slate-100 flex items-start justify-between gap-4 bg-slate-50/30">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-800 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-1 font-medium">{subtitle}</p>}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-6'}>
        {children}
      </div>
    </div>
  );
};

export default Card;
