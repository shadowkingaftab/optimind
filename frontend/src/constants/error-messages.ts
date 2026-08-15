export const ERROR_MESSAGES = {
  AUTH: {
    INVALID_CREDENTIALS: 'Invalid email or password',
    EMAIL_REQUIRED: 'Email is required',
    PASSWORD_REQUIRED: 'Password is required',
    WEAK_PASSWORD: 'Password must be at least 8 characters',
    PASSWORDS_DO_NOT_MATCH: 'Passwords do not match',
    USER_NOT_FOUND: 'User not found',
    EMAIL_ALREADY_EXISTS: 'Email already exists'
  },
  UPLOAD: {
    FILE_TOO_LARGE: 'File size exceeds maximum limit',
    INVALID_TYPE: 'Invalid file type',
    UPLOAD_FAILED: 'Upload failed. Please try again',
    PROCESSING_FAILED: 'Processing failed. Please try again'
  },
  PREDICTION: {
    NOT_FOUND: 'Prediction not found',
    PROCESSING_FAILED: 'Prediction processing failed'
  },
  REPORT: {
    NOT_FOUND: 'Report not found',
    GENERATION_FAILED: 'Report generation failed'
  },
  NETWORK: {
    TIMEOUT: 'Request timeout. Please try again',
    OFFLINE: 'You are offline. Please check your connection',
    SERVER_ERROR: 'Server error. Please try again later'
  },
  VALIDATION: {
    REQUIRED_FIELD: 'This field is required',
    INVALID_EMAIL: 'Invalid email address',
    INVALID_PHONE: 'Invalid phone number'
  }
} as const
