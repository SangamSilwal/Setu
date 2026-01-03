"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

export interface User {
  id: string
  email: string
  name: string
  role: "user" | "admin"
  isFirstTime: boolean
  details?: {
    nid?: string
    age?: number
    education?: string
    salary?: string
    disability?: { hasDisability: boolean; type?: string }
    address?: { province: string; district: string; municipality: string; ward: string }
  }
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (token: string) => void
  logout: () => void
  updateUserDetails: (details: User["details"]) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Helper function to decode JWT
function decodeToken(token: string): { sub: string; exp: number } | null {
  try {
    const payload = token.split(".")[1]
    return JSON.parse(atob(payload))
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    
    if (token) {
      const decoded = decodeToken(token)
      
      if (decoded && decoded.exp * 1000 > Date.now()) {
        // Token is valid, check if we have cached user details
        const cachedDetails = localStorage.getItem("know_rights_user_details")
        const details = cachedDetails ? JSON.parse(cachedDetails) : undefined
        
        setUser({
          id: decoded.sub,
          email: decoded.sub,
          name: decoded.sub.split("@")[0],
          role: "user",
          isFirstTime: !details,
          details,
        })
      } else {
        // Token expired or invalid
        localStorage.removeItem("access_token")
        localStorage.removeItem("know_rights_user_details")
      }
    }
    
    setIsLoading(false)
  }, [])

  const login = (token: string) => {
    localStorage.setItem("access_token", token)
    
    const decoded = decodeToken(token)
    if (decoded) {
      setUser({
        id: decoded.sub,
        email: decoded.sub,
        name: decoded.sub.split("@")[0],
        role: "user",
        isFirstTime: true,
      })
    }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem("access_token")
    localStorage.removeItem("know_rights_user_details")
  }

  const updateUserDetails = async (details: User["details"]) => {
    if (!user) return
    const updatedUser = { ...user, details, isFirstTime: false }
    setUser(updatedUser)
    localStorage.setItem("know_rights_user_details", JSON.stringify(details))
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, updateUserDetails }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider")
  return context
}