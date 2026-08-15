export const profileValidation = {
  name: (value: string): string | undefined => {
    if (!value) return 'Name is required'
    if (value.length < 2) return 'Name must be at least 2 characters'
    if (value.length > 50) return 'Name must be less than 50 characters'
    return undefined
  },
  email: (value: string): string | undefined => {
    if (!value) return 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Invalid email address'
    return undefined
  }
}
