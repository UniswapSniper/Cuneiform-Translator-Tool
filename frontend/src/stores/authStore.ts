import { create } from 'zustand'

interface AuthStore {
  isAuthenticated: boolean
  token: string | null
  setAuthenticated: (auth: boolean, token?: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  isAuthenticated: false,
  token: localStorage.getItem('auth_token') || null,
  setAuthenticated: (auth, token) =>
    set({
      isAuthenticated: auth,
      token: token || null,
    }),
  logout: () => {
    localStorage.removeItem('auth_token')
    set({ isAuthenticated: false, token: null })
  },
}))
