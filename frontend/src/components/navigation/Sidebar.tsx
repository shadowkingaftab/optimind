import React from 'react'
import { Link, useLocation } from 'react-router-dom'

interface SidebarItem {
  label: string
  href: string
  icon?: React.ReactNode
}

interface SidebarProps {
  items: SidebarItem[]
  footer?: React.ReactNode
}

const Sidebar: React.FC<SidebarProps> = ({ items, footer }) => {
  const location = useLocation()

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto">
        <nav className="space-y-1 px-2 py-4">
          {items.map((item) => {
            const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`${
                  isActive
                    ? 'bg-indigo-50 border-r-4 border-indigo-500 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                } group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors`}
              >
                {item.icon && (
                  <span className={`${isActive ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'} mr-3 flex-shrink-0`}>
                    {item.icon}
                  </span>
                )}
                {item.label}
              </Link>
            )
          })}
        </nav>
      </div>
      {footer && <div className="flex-shrink-0 border-t border-gray-200 p-4">{footer}</div>}
    </div>
  )
}

export default Sidebar
