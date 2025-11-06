'use client'

import { useState, useEffect } from 'react'
import { get2FAStatus } from '@/lib/api-client'
import TwoFactorSetup from '@/components/auth/TwoFactorSetup'
import TwoFactorDisable from '@/components/auth/TwoFactorDisable'

interface TwoFactorStatus {
  enabled: boolean
  method: string | null
  backup_codes_remaining: number
}

export default function SettingsPage() {
  const [twoFactorStatus, setTwoFactorStatus] = useState<TwoFactorStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTwoFactorStatus()
  }, [])

  const loadTwoFactorStatus = async () => {
    try {
      const status = await get2FAStatus()
      setTwoFactorStatus(status)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleSetupComplete = () => {
    loadTwoFactorStatus()
  }

  const handleDisableComplete = () => {
    loadTwoFactorStatus()
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        Security Settings
      </h1>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Two-Factor Authentication Section */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Two-Factor Authentication
          </h2>

          {twoFactorStatus?.enabled ? (
            <div className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div className="ml-3 flex-1">
                    <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
                      Two-Factor Authentication is enabled
                    </h3>
                    <div className="mt-2 text-sm text-green-700 dark:text-green-300">
                      <p>Method: {twoFactorStatus.method?.toUpperCase() || 'TOTP'}</p>
                      <p>Backup codes remaining: {twoFactorStatus.backup_codes_remaining}</p>
                      {twoFactorStatus.backup_codes_remaining < 3 && (
                        <p className="text-yellow-600 dark:text-yellow-400 mt-2">
                          ⚠️ You're running low on backup codes. Consider regenerating them.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <TwoFactorDisable onComplete={handleDisableComplete} />
            </div>
          ) : (
            <TwoFactorSetup onComplete={handleSetupComplete} />
          )}
        </div>

        {/* Additional Security Settings */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Session Management
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Manage your active sessions and devices.
          </p>
          <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600">
            View Active Sessions
          </button>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Password
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Update your password regularly to keep your account secure.
          </p>
          <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600">
            Change Password
          </button>
        </div>
      </div>
    </div>
  )
}


