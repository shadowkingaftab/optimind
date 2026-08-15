import { IMAGE_LIMITS } from '../constants/image-limits'

export const imageValidation = {
  isImage: (file: File): boolean => {
    return file.type.startsWith('image/')
  },
  isAcceptedType: (file: File): boolean => {
    return IMAGE_LIMITS.ACCEPTED_TYPES.includes(file.type)
  },
  isSizeValid: (file: File): boolean => {
    return file.size <= IMAGE_LIMITS.MAX_FILE_SIZE
  },
  validate: (file: File): string | undefined => {
    if (!imageValidation.isImage(file)) {
      return 'File must be an image'
    }
    if (!imageValidation.isAcceptedType(file)) {
      return 'Invalid image format'
    }
    if (!imageValidation.isSizeValid(file)) {
      return `File size exceeds ${IMAGE_LIMITS.MAX_FILE_SIZE / 1024 / 1024}MB`
    }
    return undefined
  }
}
