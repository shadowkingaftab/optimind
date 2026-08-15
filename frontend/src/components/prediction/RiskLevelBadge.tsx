import React from 'react'
import Badge from '../common/Badge'

interface RiskLevelBadgeProps {
  level: 'low' | 'medium' | 'high' | 'unknown'
  size?: 'sm' | 'md'
}

const RiskLevelBadge: React.FC<RiskLevelBadgeProps> = ({ level, size = 'md' }) => {
  const variants = {
    low: 'success' as const,
    medium: 'warning' as const,
    high: 'danger' as const,
    unknown: 'default' as const
  }

  return (
    <Badge variant={variants[level]} size={size}>
      {level.charAt(0).toUpperCase() + level.slice(1)} Risk
    </Badge>
  )
}

export default RiskLevelBadge
