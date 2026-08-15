import { create } from 'zustand'
import { AuthState, User, LoginCredentials, RegisterCredentials } from '../types/auth.types'
import { ERROR_MESSAGES } from '../constants/error-messages'

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  loading: false,

  login: async (credentials) => {
    set({ loading: true })
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      if (!response.ok) throw new Error(ERROR_MESSAGES.AUTH.INVALID_CREDENTIALS)
      const data = await response.json()
      set({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        loading: false
      })
    } catch (error) {
      set({ loading: false })
      throw error
    }
  },

  register: async (credentials) => {
    set({ loading: true })
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })
      if (!response.ok) throw new Error('Registration failed')
      const data = await response.json()
      set({
        user: data.user,
        token: data.token,
        isAuthenticated: true,
        loading: false
      })
    } catch (error) {
      set({ loading: false })
      throw error
    }
  },

  logout: () => {
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false
    })
  },

  setUser: (user) => set({ user }),
  setToken: (token) => set({ token, isAuthenticated: !!token }),
  setLoading: (loading) => set({ loading })
}))
