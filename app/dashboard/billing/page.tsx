'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getSubscription, cancelSubscription, api } from '@/lib/api-client'
import { CreditCard, Calendar, AlertCircle, CheckCircle, XCircle, TrendingUp } from 'lucide-react'

interface SubscriptionData {
  status: string
  plan_id?: string
  current_period_start?: string
  current_period_end?: string
  cancel_at_period_end?: boolean
  amount?: number
  currency?: string
  interval?: string
  payment_provider?: string
}

export default function BillingPage() {
  const router = useRouter()
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null)
  const [loading, setLoading] = useState(true)
  const [canceling, setCanceling] = useState(false)
  const [loadingPortal, setLoadingPortal] = useState(false)

  useEffect(() => {
    loadSubscription()
  }, [])

  const loadSubscription = async () => {
    try {
      const data = await getSubscription()
      setSubscription(data)
    } catch (error) {
      console.error('Error loading subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancelSubscription = async () => {
    if (
      !confirm(
        'Are you sure you want to cancel your subscription? You will still have access until the end of your billing period.'
      )
    ) {
      return
    }

    setCanceling(true)
    try {
      await cancelSubscription(false)
      await loadSubscription()
      alert('Subscription will be canceled at the end of the billing period.')
    } catch (error) {
      alert('Failed to cancel subscription. Please try again.')
    } finally {
      setCanceling(false)
    }
  }

  const handleImmediateCancellation = async () => {
    if (
      !confirm(
        'Are you sure you want to cancel immediately? You will lose access right away and no refund will be provided.'
      )
    ) {
      return
    }

    setCanceling(true)
    try {
      await cancelSubscription(true)
      await loadSubscription()
      alert('Subscription has been canceled immediately.')
    } catch (error) {
      alert('Failed to cancel subscription. Please try again.')
    } finally {
      setCanceling(false)
    }
  }

  const handleManageBilling = async () => {
    setLoadingPortal(true)
    try {
      const { data } = await api.post('/subscriptions/billing-portal', {
        return_url: window.location.href,
      })
      window.location.href = data.url
    } catch (error) {
      alert('Failed to open billing portal. Please try again.')
    } finally {
      setLoadingPortal(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { color: 'green', icon: CheckCircle, text: 'Active' },
      canceled: { color: 'red', icon: XCircle, text: 'Canceled' },
      past_due: { color: 'yellow', icon: AlertCircle, text: 'Past Due' },
      trialing: { color: 'blue', icon: TrendingUp, text: 'Trial' },
      no_subscription: { color: 'gray', icon: AlertCircle, text: 'No Subscription' },
    }

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.no_subscription
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-${config.color}-100 text-${config.color}-800 dark:bg-${config.color}-900 dark:text-${config.color}-200`}>
        <Icon className="w-4 h-4 mr-1.5" />
        {config.text}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
              <div className="h-48 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const hasActiveSubscription = subscription && subscription.status !== 'no_subscription'

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Billing & Subscription
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage your subscription and billing information
          </p>
        </div>

        {/* No Subscription State */}
        {!hasActiveSubscription && (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-8 text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-gray-100 dark:bg-gray-700 mb-4">
              <CreditCard className="h-8 w-8 text-gray-600 dark:text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No Active Subscription
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Subscribe to Redline to unlock powerful features and grow your workflow
            </p>
            <button
              onClick={() => router.push('/pricing')}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              View Pricing Plans
            </button>
          </div>
        )}

        {/* Active Subscription */}
        {hasActiveSubscription && (
          <div className="space-y-6">
            {/* Subscription Overview */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Current Subscription
                </h2>
              </div>
              <div className="px-6 py-5 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Status
                  </span>
                  {getStatusBadge(subscription.status)}
                </div>

                {subscription.plan_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Plan
                    </span>
                    <span className="text-sm text-gray-900 dark:text-white font-medium">
                      Professional
                    </span>
                  </div>
                )}

                {subscription.amount && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Amount
                    </span>
                    <span className="text-sm text-gray-900 dark:text-white font-semibold">
                      ${subscription.amount / 100} {subscription.currency?.toUpperCase()} / {subscription.interval}
                    </span>
                  </div>
                )}

                {subscription.current_period_end && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400 flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      {subscription.cancel_at_period_end ? 'Cancels On' : 'Renews On'}
                    </span>
                    <span className="text-sm text-gray-900 dark:text-white">
                      {new Date(subscription.current_period_end).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                )}

                {subscription.payment_provider && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Payment Provider
                    </span>
                    <span className="text-sm text-gray-900 dark:text-white capitalize">
                      {subscription.payment_provider}
                    </span>
                  </div>
                )}

                {subscription.cancel_at_period_end && (
                  <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                    <div className="flex">
                      <AlertCircle className="h-5 w-5 text-yellow-400" />
                      <div className="ml-3">
                        <p className="text-sm text-yellow-800 dark:text-yellow-200">
                          Your subscription will be canceled at the end of the current billing period.
                          You will retain access until then.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Payment Method */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Payment Method
                </h2>
              </div>
              <div className="px-6 py-5">
                <button
                  onClick={handleManageBilling}
                  disabled={loadingPortal}
                  className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors"
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  {loadingPortal ? 'Loading...' : 'Manage Payment Method'}
                </button>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  Update your credit card, view invoices, and download receipts
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Subscription Actions
                </h2>
              </div>
              <div className="px-6 py-5 space-y-4">
                <div>
                  <button
                    onClick={() => router.push('/pricing')}
                    className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Upgrade Plan
                  </button>
                  <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Unlock more features with a higher-tier plan
                  </p>
                </div>

                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  {!subscription.cancel_at_period_end ? (
                    <>
                      <button
                        onClick={handleCancelSubscription}
                        disabled={canceling}
                        className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-red-300 dark:border-red-600 shadow-sm text-sm font-medium rounded-md text-red-700 dark:text-red-200 bg-white dark:bg-gray-700 hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50 transition-colors"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        {canceling ? 'Canceling...' : 'Cancel Subscription'}
                      </button>
                      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                        Cancel at the end of the current billing period
                      </p>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={handleImmediateCancellation}
                        disabled={canceling}
                        className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-red-500 dark:border-red-600 shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 transition-colors"
                      >
                        {canceling ? 'Processing...' : 'Cancel Immediately'}
                      </button>
                      <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                        End subscription right now (no refund)
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

