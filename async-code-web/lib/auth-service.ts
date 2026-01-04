// Authentication service that talks to our backend API

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface User {
    id: number;
    email: string;
    full_name?: string;
    github_username?: string;
}

export interface AuthResponse {
    user: User;
    token: string;
}

class AuthService {
    private token: string | null = null;

    constructor() {
        // Load token from localStorage on initialization
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('auth_token');
        }
    }

    async register(email: string, password: string, full_name?: string): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, full_name }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Registration failed');
        }

        const data: AuthResponse = await response.json();
        this.setToken(data.token);
        return data;
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Login failed');
        }

        const data: AuthResponse = await response.json();
        this.setToken(data.token);
        return data;
    }

    async getCurrentUser(): Promise<User | null> {
        if (!this.token) {
            return null;
        }

        try {
            const response = await fetch(`${API_URL}/api/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
            });

            if (!response.ok) {
                // Token is invalid or expired
                this.clearToken();
                return null;
            }

            const data = await response.json();
            return data.user;
        } catch (error) {
            console.error('Error getting current user:', error);
            this.clearToken();
            return null;
        }
    }

    logout() {
        this.clearToken();
    }

    getToken(): string | null {
        return this.token;
    }

    private setToken(token: string) {
        this.token = token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', token);
        }
    }

    private clearToken() {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
        }
    }

    // Helper method to make authenticated API calls
    async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
        const headers = new Headers(options.headers);

        if (this.token) {
            headers.set('Authorization', `Bearer ${this.token}`);
        }

        return fetch(url, {
            ...options,
            headers,
        });
    }
}

export const authService = new AuthService();
