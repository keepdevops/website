'use client'

import { useState } from 'react'
import { disable2FA } from '@/lib/api-client'

interface TwoFactorDisableProps {
  onComplete: () => void
}

export default function TwoFactorDisable({ onComplete }: TwoFactorDisableProps) {
  const [showConfirm, setShowConfirm] = useState(false)
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await disable2FA(password)
      setShowConfirm(false)
      setPassword('')
      onComplete()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disable 2FA')
    } finally {
      setLoading(false)
    }
  }

  if (!showConfirm) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Manage Two-Factor Authentication
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Disabling 2FA will make your account less secure.
        </p>
        <button
          onClick={() => setShowConfirm(true)}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Disable 2FA
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Confirm Disable Two-Factor Authentication
      </h3>
      
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-4">
        <p className="text-sm text-yellow-800 dark:text-yellow-200">
          ⚠️ Warning: Disabling two-factor authentication will make your account more vulnerable to unauthorized access.
        </p>
      </div>

      <form onSubmit={handleDisable} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Enter your password to confirm:
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex space-x-3">
          <button
            type="submit"
            disabled={loading || !password}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Disabling...' : 'Confirm Disable'}
          </button>
          <button
            type="button"
            onClick={() => {
              setShowConfirm(false)
              setPassword('')
              setError('')
            }}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}


