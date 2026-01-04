import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/supabase'

let supabaseInstance: ReturnType<typeof createClient<Database>> | null = null

export const getSupabase = () => {
    if (!supabaseInstance) {
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
        const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

        // Return null if Supabase credentials are not configured
        if (!supabaseUrl || !supabaseAnonKey) {
            console.warn('Supabase credentials not configured. Running without database persistence.')
            return null
        }

        supabaseInstance = createClient<Database>(supabaseUrl, supabaseAnonKey, {
            auth: {
                autoRefreshToken: true,
                persistSession: true,
                detectSessionInUrl: true
            }
        })
    }

    return supabaseInstance
}
