import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/supabase'

let supabaseInstance: ReturnType<typeof createClient<Database>> | null = null
let supabaseInitialized = false

export const getSupabase = () => {
    if (!supabaseInitialized) {
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
        const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

        if (supabaseUrl && supabaseAnonKey) {
            supabaseInstance = createClient<Database>(supabaseUrl, supabaseAnonKey, {
                auth: {
                    autoRefreshToken: true,
                    persistSession: true,
                    detectSessionInUrl: true
                }
            })
            console.log('Supabase client initialized successfully')
        } else {
            console.warn('Supabase credentials not configured - running without database')
            supabaseInstance = null
        }
        supabaseInitialized = true
    }

    return supabaseInstance
}
