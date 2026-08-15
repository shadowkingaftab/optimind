import { IMAGE_LIMITS, IMAGE_REQUIREMENTS } from '../constants/image-limits'

export const uploadValidation = {
  fileSize: (file: File): string | undefined => {
    if (file.size > IMAGE_LIMITS.MAX_FILE_SIZE) {
      return `File size exceeds ${IMAGE_REQUIREMENTS.MAX_SIZE}`
    }
    return undefined
  },
  fileType: (file: File): string | undefined => {
    if (!IMAGE_LIMITS.ACCEPTED_TYPES.includes(file.type)) {
      return `Invalid file type. Accepted: ${IMAGE_REQUIREMENTS.FORMATS.join(', ')}`
    }
    return undefined
  },
  maxFiles: (files: File[]): string | undefined => {
    if (files.length > IMAGE_LIMITS.MAX_FILES) {
      return `Maximum ${IMAGE_LIMITS.MAX_FILES} file(s) allowed`
    }
    return undefined
  },
  validate: (file: File): string | undefined => {
    return uploadValidation.fileSize(file) || uploadValidation.fileType(file)
  }
}
