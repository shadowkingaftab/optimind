export interface UserProfile {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'viewer'
  createdAt: string
  updatedAt: string
}

export interface UpdateUserProfile {
  name?: string
  email?: string
}
