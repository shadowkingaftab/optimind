export const APP_ROUTES = {
  PUBLIC: {
    LANDING: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    FORGOT_PASSWORD: '/forgot-password',
    RESET_PASSWORD: '/reset-password/:token',
    PRIVACY: '/privacy',
    TERMS: '/terms'
  },
  PROTECTED: {
    DASHBOARD: '/dashboard',
    UPLOAD: '/upload',
    PREDICTION: '/predictions/:id',
    PREDICTION_HISTORY: '/predictions',
    REPORT: '/reports/:id',
    PROFILE: '/profile',
    SETTINGS: '/settings'
  },
  ADMIN: {
    ROOT: '/admin',
    USERS: '/admin/users',
    MODELS: '/admin/models',
    AUDIT_LOGS: '/admin/audit-logs',
    HEALTH: '/admin/health',
    PERFORMANCE: '/admin/performance'
  },
  ERROR: {
    NOT_FOUND: '*',
    SERVICE_UNAVAILABLE: '/service-unavailable'
  }
} as const
