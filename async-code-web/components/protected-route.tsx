'use client'

import { useAuth } from '@/contexts/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { getSupabase } from '@/lib/supabase'

interface ProtectedRouteProps {
    children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { user, loading } = useAuth()
    const router = useRouter()
    const supabase = getSupabase()

    useEffect(() => {
        // Only enforce authentication if Supabase is configured
        if (supabase && !loading && !user) {
            router.push('/signin')
        }
    }, [user, loading, router, supabase])

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
            </div>
        )
    }

    // If Supabase is not configured, allow access without authentication
    if (!supabase) {
        return <>{children}</>
    }

    if (!user) {
        return null // Will redirect
    }

    return <>{children}</>
} 