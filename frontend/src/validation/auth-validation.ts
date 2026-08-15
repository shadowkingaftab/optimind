export const authValidation = {
  email: (value: string): string | undefined => {
    if (!value) return 'Email is required'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Invalid email address'
    return undefined
  },
  password: (value: string): string | undefined => {
    if (!value) return 'Password is required'
    if (value.length < 8) return 'Password must be at least 8 characters'
    return undefined
  },
  name: (value: string): string | undefined => {
    if (!value) return 'Name is required'
    if (value.length < 2) return 'Name must be at least 2 characters'
    return undefined
  },
  confirmPassword: (value: string, password: string): string | undefined => {
    if (!value) return 'Please confirm your password'
    if (value !== password) return 'Passwords do not match'
    return undefined
  }
}
