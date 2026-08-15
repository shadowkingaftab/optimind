export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message)
  }
  return 'An unexpected error occurred'
}

export function isApiError(error: unknown): boolean {
  return typeof error === 'object' && error !== null && 'message' in error
}

export function handleApiError(error: unknown): string {
  if (isApiError(error)) {
    const apiError = error as { message: string; code?: string }
    return apiError.message
  }
  return getErrorMessage(error)
}
