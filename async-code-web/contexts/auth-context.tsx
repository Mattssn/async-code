'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { authService, User } from '@/lib/auth-service'

interface AuthContextType {
    user: User | null
    loading: boolean
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string, fullName?: string) => Promise<void>
    signOut: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

interface AuthProviderProps {
    children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Check if user is already logged in
        authService.getCurrentUser().then((user) => {
            setUser(user)
            setLoading(false)
        })
    }, [])

    const login = async (email: string, password: string) => {
        const { user } = await authService.login(email, password)
        setUser(user)
    }

    const register = async (email: string, password: string, fullName?: string) => {
        const { user } = await authService.register(email, password, fullName)
        setUser(user)
    }

    const signOut = () => {
        authService.logout()
        setUser(null)
    }

    const value = {
        user,
        loading,
        login,
        register,
        signOut,
    }

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
