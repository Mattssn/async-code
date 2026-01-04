'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/auth-context'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Code2 } from 'lucide-react'
import { toast } from 'sonner'

export default function SignIn() {
    const { user, loading, login, register } = useAuth()
    const router = useRouter()
    const [isRegister, setIsRegister] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [fullName, setFullName] = useState('')

    useEffect(() => {
        if (user && !loading) {
            router.push('/')
        }
    }, [user, loading, router])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)

        try {
            if (isRegister) {
                await register(email, password, fullName)
                toast.success('Account created successfully!')
            } else {
                await login(email, password)
                toast.success('Logged in successfully!')
            }
            router.push('/')
        } catch (error: any) {
            toast.error(error.message || (isRegister ? 'Registration failed' : 'Login failed'))
        } finally {
            setIsSubmitting(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
            </div>
        )
    }

    if (user) {
        return null // Will redirect
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center mx-auto mb-4">
                        <Code2 className="w-6 h-6 text-white" />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-2">
                        Welcome to AI Code Automation
                    </h1>
                    <p className="text-slate-600">
                        {isRegister ? 'Create an account to get started' : 'Sign in to continue'}
                    </p>
                </div>

                {/* Auth Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>{isRegister ? 'Create Account' : 'Sign In'}</CardTitle>
                        <CardDescription>
                            {isRegister
                                ? 'Enter your details to create your account'
                                : 'Enter your email and password to sign in'
                            }
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {isRegister && (
                                <div className="space-y-2">
                                    <Label htmlFor="fullName">Full Name (Optional)</Label>
                                    <Input
                                        id="fullName"
                                        type="text"
                                        placeholder="John Doe"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                    />
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={6}
                                />
                                {isRegister && (
                                    <p className="text-xs text-slate-500">
                                        Password must be at least 6 characters
                                    </p>
                                )}
                            </div>

                            <Button
                                type="submit"
                                className="w-full"
                                disabled={isSubmitting}
                            >
                                {isSubmitting
                                    ? (isRegister ? 'Creating account...' : 'Signing in...')
                                    : (isRegister ? 'Create Account' : 'Sign In')
                                }
                            </Button>
                        </form>

                        <div className="mt-4 text-center text-sm">
                            <button
                                type="button"
                                onClick={() => setIsRegister(!isRegister)}
                                className="text-slate-600 hover:text-slate-900 underline"
                            >
                                {isRegister
                                    ? 'Already have an account? Sign in'
                                    : "Don't have an account? Sign up"
                                }
                            </button>
                        </div>
                    </CardContent>
                </Card>

                {/* Footer */}
                <div className="text-center mt-6 text-sm text-slate-600">
                    <p>
                        By signing in, you agree to our terms of service and privacy policy.
                    </p>
                </div>
            </div>
        </div>
    )
}
