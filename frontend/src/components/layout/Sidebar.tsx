import React from 'react';
import { Activity, Users, FileText, Settings, Eye } from '../../assets/icons';

interface NavItem {
  label: string;
  icon: React.FC<{ className?: string }>;
  active?: boolean;
  badge?: number;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: Activity, active: true },
  { label: 'Scan Analysis', icon: Eye },
  { label: 'Patients', icon: Users, badge: 12 },
  { label: 'Reports', icon: FileText },
  { label: 'Settings', icon: Settings },
];

const Sidebar: React.FC<{ isOpen: boolean }> = ({ isOpen }) => {
  return (
    <aside 
      className={`fixed inset-y-0 left-0 z-20 w-64 bg-slate-50 border-r border-slate-200 transform transition-transform duration-300 ease-in-out pt-16 lg:translate-x-0 lg:static lg:pt-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <nav className="p-4 space-y-1 mt-4">
        <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Clinical Workspace</p>
        {navItems.map((item) => (
          <a
            key={item.label}
            href="#"
            className={`flex items-center justify-between px-4 py-3 rounded-lg text-sm font-medium transition-all ${
              item.active 
                ? 'bg-teal-600 text-white shadow-md shadow-teal-600/20' 
                : 'text-slate-600 hover:bg-white hover:text-teal-700 hover:shadow-sm'
            }`}
          >
            <div className="flex items-center gap-3">
              <item.icon className={`w-5 h-5 ${item.active ? 'text-white' : 'text-slate-400'}`} />
              {item.label}
            </div>
            {item.badge && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                item.active ? 'bg-teal-500 text-white' : 'bg-slate-200 text-slate-600'
              }`}>
                {item.badge}
              </span>
            )}
          </a>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 bg-slate-50">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            <span className="text-xs font-semibold text-slate-700">System Status</span>
          </div>
          <p className="text-xs text-slate-500">AI Model v2.4.1 • Operational</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
