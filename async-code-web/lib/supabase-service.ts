import { getSupabase } from './supabase'
import { Project, Task, ProjectWithStats, ChatMessage } from '@/types'

// Stub service for local development - returns empty data
export class SupabaseService {
    private static get supabase() {
        const client = getSupabase()
        if (!client) {
            console.warn('Supabase not configured - using local development mode')
            return null
        }
        return client
    }

    // Project operations
    static async getProjects(): Promise<ProjectWithStats[]> {
        if (!this.supabase) return []

        try {
            const { data, error } = await this.supabase
                .from('projects')
                .select(`
                    *,
                    tasks (
                        id,
                        status
                    )
                `)
                .order('created_at', { ascending: false })

            if (error) throw error

            // Add task statistics
            return data?.map((project: any) => ({
                ...project,
                task_count: project.tasks?.length || 0,
                completed_tasks: project.tasks?.filter((t: any) => t.status === 'completed').length || 0,
                active_tasks: project.tasks?.filter((t: any) => t.status === 'running').length || 0
            })) || []
        } catch (error) {
            console.warn('Error loading projects:', error)
            return []
        }
    }

    static async createProject(projectData: {
        name: string
        description?: string
        repo_url: string
        repo_name: string
        repo_owner: string
        settings?: any
    }): Promise<Project> {
        if (!this.supabase) {
            throw new Error('Database not available in local development mode')
        }

        const { data: { user } } = await this.supabase.auth.getUser()
        if (!user) throw new Error('No authenticated user')

        const { data, error } = await this.supabase
            .from('projects')
            .insert([{ ...projectData, user_id: user.id }])
            .select()
            .single()

        if (error) throw error
        return data
    }

    static async updateProject(id: number, updates: Partial<Project>): Promise<Project> {
        if (!this.supabase) {
            throw new Error('Database not available in local development mode')
        }

        const { data, error } = await this.supabase
            .from('projects')
            .update(updates)
            .eq('id', id)
            .select()
            .single()

        if (error) throw error
        return data
    }

    static async deleteProject(id: number): Promise<void> {
        if (!this.supabase) {
            throw new Error('Database not available in local development mode')
        }

        const { error } = await this.supabase
            .from('projects')
            .delete()
            .eq('id', id)

        if (error) throw error
    }

    static async getProject(id: number): Promise<Project | null> {
        if (!this.supabase) return null

        const { data, error } = await this.supabase
            .from('projects')
            .select('*')
            .eq('id', id)
            .single()

        if (error) {
            if (error.code === 'PGRST116') return null // Not found
            throw error
        }
        return data
    }

    // Task operations
    static async getTasks(projectId?: number, options?: {
        limit?: number
        offset?: number
    }): Promise<Task[]> {
        if (!this.supabase) return []

        try {
            let query = this.supabase
                .from('tasks')
                .select(`
                    *,
                    project:projects (
                        id,
                        name,
                        repo_name,
                        repo_owner
                    )
                `)

            if (projectId) {
                query = query.eq('project_id', projectId)
            }

            // Add pagination if options provided
            if (options?.limit) {
                const start = options.offset || 0
                const end = start + options.limit - 1
                query = query.range(start, end)
            }

            const { data, error } = await query.order('created_at', { ascending: false })

            if (error) throw error
            return data || []
        } catch (error) {
            console.warn('Error loading tasks:', error)
            return []
        }
    }

    static async getTask(id: number): Promise<Task | null> {
        if (!this.supabase) return null

        try {
            const { data, error } = await this.supabase
                .from('tasks')
                .select(`
                    *,
                    project:projects (
                        id,
                        name,
                        repo_name,
                        repo_owner
                    )
                `)
                .eq('id', id)
                .single()

            if (error) {
                if (error.code === 'PGRST116') return null // Not found
                throw error
            }
            return data
        } catch (error) {
            console.warn('Error loading task:', error)
            return null
        }
    }

    static async getUserProfile() {
        if (!this.supabase) return null

        try {
            const { data: { user } } = await this.supabase.auth.getUser()
            if (!user) return null

            const { data, error } = await this.supabase
                .from('users')
                .select('*')
                .eq('id', user.id)
                .single()

            if (error) {
                if (error.code === 'PGRST116') return null // Not found
                throw error
            }
            return data
        } catch (error) {
            console.warn('Error loading user profile:', error)
            return null
        }
    }

    static async updateUserProfile(updates: {
        full_name?: string
        github_username?: string
        github_token?: string
        preferences?: any
    }) {
        if (!this.supabase) {
            // In local dev mode, just store in localStorage
            if (typeof window !== 'undefined' && updates.preferences) {
                localStorage.setItem('user_preferences', JSON.stringify(updates.preferences))
            }
            return { preferences: updates.preferences }
        }

        const { data: { user } } = await this.supabase.auth.getUser()
        if (!user) throw new Error('No authenticated user')

        const { data, error } = await this.supabase
            .from('users')
            .update(updates)
            .eq('id', user.id)
            .select()
            .single()

        if (error) throw error
        return data
    }
}
