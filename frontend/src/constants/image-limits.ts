export const IMAGE_LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024,
  ACCEPTED_TYPES: ['image/jpeg', 'image/png', 'image/dicom'],
  MAX_DIMENSION: 4096,
  MIN_DIMENSION: 224,
  MAX_FILES: 1
} as const

export const IMAGE_REQUIREMENTS = {
  FORMATS: ['JPG', 'PNG', 'DICOM'],
  MAX_SIZE: '10MB',
  DIMENSIONS: 'Minimum 224x224, Maximum 4096x4096',
  GUIDELINES: [
    'Image should be centered and in focus',
    'Both eyes should be visible in frame',
    'Avoid blurry or low-light images',
    'Ensure good contrast between iris and background'
  ]
} as const
