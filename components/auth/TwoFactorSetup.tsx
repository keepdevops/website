'use client'

import { useState } from 'react'
import { api } from '@/lib/api-client'
import Image from 'next/image'

export default function TwoFactorSetup({ onComplete }: { onComplete?: () => void }) {
  const [step, setStep] = useState<'initial' | 'setup' | 'verify'>('initial')
  const [setupData, setSetupData] = useState<any>(null)
  const [verificationCode, setVerificationCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSetup = async () => {
    setLoading(true)
    setError('')
    
    try {
      const { data } = await api.post('/api/2fa/setup')
      setSetupData(data)
      setStep('setup')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Setup failed')
    } finally {
      setLoading(false)
    }
  }

  const handleEnable = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      await api.post('/api/2fa/enable', { code: verificationCode })
      alert('2FA enabled successfully!')
      onComplete?.()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid code')
    } finally {
      setLoading(false)
    }
  }

  if (step === 'initial') {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Two-Factor Authentication
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Add an extra layer of security to your account by requiring a verification code in addition to your password.
        </p>
        <button
          onClick={handleSetup}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Setting up...' : 'Setup 2FA'}
        </button>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </div>
    )
  }

  if (step === 'setup') {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Scan QR Code
        </h3>
        
        <div className="space-y-4">
          <div className="flex justify-center">
            <img src={setupData.qr_code_url} alt="QR Code" className="w-64 h-64" />
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Manual Entry Key:
            </p>
            <code className="text-sm bg-white dark:bg-gray-800 p-2 rounded block break-all">
              {setupData.secret}
            </code>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Backup Codes (Save these in a safe place):
            </p>
            <div className="grid grid-cols-2 gap-2 bg-gray-50 dark:bg-gray-700 p-4 rounded">
              {setupData.backup_codes.map((code: string, idx: number) => (
                <code key={idx} className="text-xs bg-white dark:bg-gray-800 p-2 rounded">
                  {code}
                </code>
              ))}
            </div>
          </div>

          <button
            onClick={() => setStep('verify')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Continue to Verification
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Verify Setup
      </h3>
      
      <form onSubmit={handleEnable} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Enter the 6-digit code from your authenticator app:
          </label>
          <input
            type="text"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="000000"
            required
            maxLength={6}
            className="w-full px-4 py-2 border border-gray-300 rounded-md text-center text-2xl tracking-widest dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading || verificationCode.length !== 6}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Verifying...' : 'Enable 2FA'}
        </button>
      </form>
    </div>
  )
}



