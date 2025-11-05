'use client'

import { useState, useEffect } from 'react'
import { getSubscription, cancelSubscription } from '@/lib/api-client'
import type { Subscription } from '@/lib/types'

export default function SubscriptionCard() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [canceling, setCanceling] = useState(false)

  useEffect(() => {
    loadSubscription()
  }, [])

  const loadSubscription = async () => {
    try {
      const data = await getSubscription()
      if (data.status !== 'no_subscription') {
        setSubscription(data)
      }
    } catch (error) {
      console.error('Error loading subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription?')) return

    setCanceling(true)
    try {
      await cancelSubscription(false)
      await loadSubscription()
      alert('Subscription will be canceled at the end of the billing period')
    } catch (error) {
      alert('Failed to cancel subscription')
    } finally {
      setCanceling(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-48 rounded-lg"></div>
  }

  if (!subscription) {
    return (
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          No Active Subscription
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Subscribe to access premium features and downloads.
        </p>
        <a
          href="/pricing"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          View Plans
        </a>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Subscription Status
      </h3>
      
      <dl className="grid grid-cols-1 gap-4">
        <div>
          <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-white capitalize">
            {subscription.status}
          </dd>
        </div>
        
        <div>
          <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Current Period End</dt>
          <dd className="mt-1 text-sm text-gray-900 dark:text-white">
            {new Date(subscription.current_period_end).toLocaleDateString()}
          </dd>
        </div>
        
        {subscription.cancel_at_period_end && (
          <div className="text-yellow-600 text-sm">
            Your subscription will be canceled at the end of the current period.
          </div>
        )}
      </dl>

      <div className="mt-6 space-x-3">
        <button
          onClick={handleCancel}
          disabled={canceling || subscription.cancel_at_period_end}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600"
        >
          {canceling ? 'Canceling...' : 'Cancel Subscription'}
        </button>
      </div>
    </div>
  )
}

