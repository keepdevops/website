'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { loginUser } from '@/lib/api-client'
import TwoFactorVerify from './TwoFactorVerify'

export default function LoginForm() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [requires2FA, setRequires2FA] = useState(false)
  const [userId, setUserId] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await loginUser(email, password)
      router.push('/dashboard')
    } catch (err: any) {
      // Check if 2FA is required
      if (err.response?.status === 403 && err.response?.data?.detail === '2FA verification required') {
        const userIdFromHeader = err.response?.headers?.['x-user-id']
        if (userIdFromHeader) {
          setUserId(userIdFromHeader)
          setRequires2FA(true)
        } else {
          setError('2FA required but user ID not found')
        }
      } else {
        setError(err.response?.data?.detail || 'Login failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const handle2FAVerified = () => {
    router.push('/dashboard')
  }

  if (requires2FA && userId) {
    return (
      <TwoFactorVerify 
        onVerified={handle2FAVerified}
        onCancel={() => {
          setRequires2FA(false)
          setUserId('')
        }}
      />
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 w-full max-w-md">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        />
      </div>

      {error && (
        <div className="text-red-600 text-sm">{error}</div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {loading ? 'Logging in...' : 'Log in'}
      </button>
    </form>
  )
}


