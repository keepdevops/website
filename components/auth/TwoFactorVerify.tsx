'use client'

import { useState } from 'react'
import { api } from '@/lib/api-client'

interface TwoFactorVerifyProps {
  onVerified: () => void
  onCancel?: () => void
}

export default function TwoFactorVerify({ onVerified, onCancel }: TwoFactorVerifyProps) {
  const [code, setCode] = useState('')
  const [useBackupCode, setUseBackupCode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (useBackupCode) {
        // For backup codes, use the regular verify endpoint
        await api.post('/api/2fa/verify-backup', { backup_code: code })
      } else {
        // For TOTP codes during login, use the dedicated login endpoint
        await api.post('/api/2fa/verify', { code })
      }
      onVerified()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Two-Factor Authentication
      </h3>
      
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        {useBackupCode 
          ? 'Enter one of your backup codes:'
          : 'Enter the 6-digit code from your authenticator app:'
        }
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          placeholder={useBackupCode ? 'XXXX-XXXX-XXXX' : '000000'}
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-md text-center text-xl tracking-widest dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        />

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading || code.length === 0}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Verifying...' : 'Verify'}
        </button>

        <button
          type="button"
          onClick={() => {
            setUseBackupCode(!useBackupCode)
            setCode('')
            setError('')
          }}
          className="w-full text-sm text-blue-600 hover:text-blue-700"
        >
          {useBackupCode ? 'Use authenticator code' : 'Use backup code'}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="w-full text-sm text-gray-600 hover:text-gray-700"
          >
            Cancel
          </button>
        )}
      </form>
    </div>
  )
}


