export const RISK_LEVELS = {
  LOW: {
    label: 'Low',
    color: 'green',
    variant: 'success'
  },
  MEDIUM: {
    label: 'Medium',
    color: 'yellow',
    variant: 'warning'
  },
  HIGH: {
    label: 'High',
    color: 'red',
    variant: 'danger'
  },
  UNKNOWN: {
    label: 'Unknown',
    color: 'gray',
    variant: 'default'
  }
} as const

export type RiskLevel = keyof typeof RISK_LEVELS
