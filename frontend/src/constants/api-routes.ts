export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout'
  },
  UPLOAD: {
    UPLOAD: '/upload',
    STATUS: '/upload/:id/status'
  },
  PREDICTION: {
    LIST: '/predictions',
    DETAIL: '/predictions/:id',
    HISTORY: '/predictions/history'
  },
  REPORT: {
    GENERATE: '/reports/generate',
    DOWNLOAD: '/reports/:id/download',
    DETAIL: '/reports/:id'
  },
  USER: {
    PROFILE: '/user/profile',
    SETTINGS: '/user/settings'
  },
  ADMIN: {
    USERS: '/admin/users',
    MODELS: '/admin/models',
    AUDIT_LOGS: '/admin/audit-logs',
    HEALTH: '/admin/health',
    PERFORMANCE: '/admin/performance'
  }
} as const
