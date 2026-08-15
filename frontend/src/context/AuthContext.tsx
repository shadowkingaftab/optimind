import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useAuthStore } from '../store/auth-slice'

interface AuthContextValue {
  user: ReturnType<typeof useAuthStore>['user']
  token: ReturnType<typeof useAuthStore>['token']
  isAuthenticated: boolean
  loading: boolean
  login: ReturnType<typeof useAuthStore>['login']
  register: ReturnType<typeof useAuthStore>['register']
  logout: ReturnType<typeof useAuthStore>['logout']
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const authStore = useAuthStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      authStore.setToken(token)
    }
    setLoading(false)
  }, [authStore])

  return (
    <AuthContext.Provider
      value={{
        user: authStore.user,
        token: authStore.token,
        isAuthenticated: authStore.isAuthenticated,
        loading,
        login: authStore.login,
        register: authStore.register,
        logout: authStore.logout
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
