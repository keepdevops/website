'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createCheckoutSession, getSubscription } from '@/lib/api-client'
import { Check, X, Zap, Shield, Crown } from 'lucide-react'

// Define your pricing tiers for Redline
const PRICING_TIERS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    interval: 'forever',
    description: 'Perfect for trying out Redline',
    features: [
      'Up to 5 projects',
      'Basic analytics',
      '1 GB storage',
      'Community support',
      '7-day data retention',
    ],
    limitations: [
      'No advanced features',
      'Limited API calls',
      'Email support only',
    ],
    icon: Zap,
    color: 'gray',
    priceId: null, // No payment needed
    cta: 'Get Started',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Professional',
    price: 29,
    interval: 'month',
    description: 'For serious developers and small teams',
    features: [
      'Unlimited projects',
      'Advanced analytics & insights',
      '100 GB storage',
      'Priority email support',
      '30-day data retention',
      'Custom integrations',
      'API access',
      'Team collaboration (up to 5)',
    ],
    limitations: [],
    icon: Shield,
    color: 'blue',
    priceId: 'price_pro_monthly', // Replace with actual Stripe price ID
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 99,
    interval: 'month',
    description: 'For large teams and organizations',
    features: [
      'Everything in Professional',
      'Unlimited storage',
      '24/7 phone & chat support',
      'Unlimited data retention',
      'Advanced security & SSO',
      'Custom SLA',
      'Dedicated account manager',
      'Unlimited team members',
      'On-premise deployment option',
      'Custom development',
    ],
    limitations: [],
    icon: Crown,
    color: 'purple',
    priceId: 'price_enterprise_monthly', // Replace with actual Stripe price ID
    cta: 'Contact Sales',
    popular: false,
  },
]

export default function PricingPage() {
  const router = useRouter()
  const [loading, setLoading] = useState<string | null>(null)
  const [currentPlan, setCurrentPlan] = useState<string | null>(null)
  const [billingInterval, setBillingInterval] = useState<'month' | 'year'>('month')

  useEffect(() => {
    loadCurrentSubscription()
  }, [])

  const loadCurrentSubscription = async () => {
    try {
      const subscription = await getSubscription()
      if (subscription && subscription.status === 'active') {
        // Map subscription to tier
        setCurrentPlan('pro') // Determine from subscription data
      }
    } catch (error) {
      console.error('Error loading subscription:', error)
    }
  }

  const handleSelectPlan = async (tier: typeof PRICING_TIERS[0]) => {
    if (tier.id === 'free') {
      router.push('/register')
      return
    }

    if (tier.id === 'enterprise') {
      // Redirect to contact/sales page
      window.location.href = 'mailto:sales@redline.com?subject=Enterprise Plan Inquiry'
      return
    }

    if (!tier.priceId) {
      alert('This plan is not available yet. Please contact support.')
      return
    }

    setLoading(tier.id)
    try {
      const { url } = await createCheckoutSession(tier.priceId)
      window.location.href = url
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Not logged in - redirect to register with plan selection
        localStorage.setItem('selected_plan', tier.id)
        router.push('/register')
      } else {
        alert('Failed to start checkout. Please try again.')
      }
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white sm:text-5xl sm:tracking-tight lg:text-6xl">
            Choose Your <span className="text-blue-600">Redline</span> Plan
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400">
            Scale your development workflow with powerful tools and integrations
          </p>

          {/* Billing Toggle */}
          <div className="mt-8 flex justify-center items-center space-x-4">
            <span className={`text-sm font-medium ${billingInterval === 'month' ? 'text-gray-900 dark:text-white' : 'text-gray-500'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingInterval(billingInterval === 'month' ? 'year' : 'month')}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 dark:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <span
                className={`${
                  billingInterval === 'year' ? 'translate-x-6' : 'translate-x-1'
                } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
              />
            </button>
            <span className={`text-sm font-medium ${billingInterval === 'year' ? 'text-gray-900 dark:text-white' : 'text-gray-500'}`}>
              Yearly
              <span className="ml-1.5 inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                Save 20%
              </span>
            </span>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {PRICING_TIERS.map((tier) => {
            const Icon = tier.icon
            const isCurrentPlan = currentPlan === tier.id
            const displayPrice = billingInterval === 'year' ? Math.floor(tier.price * 0.8) : tier.price

            return (
              <div
                key={tier.id}
                className={`relative rounded-2xl border-2 ${
                  tier.popular
                    ? 'border-blue-500 shadow-xl scale-105'
                    : 'border-gray-200 dark:border-gray-700'
                } bg-white dark:bg-gray-800 p-8 transition-all hover:shadow-2xl`}
              >
                {tier.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="inline-flex items-center rounded-full bg-blue-500 px-4 py-1 text-xs font-semibold text-white">
                      MOST POPULAR
                    </span>
                  </div>
                )}

                {isCurrentPlan && (
                  <div className="absolute -top-4 right-4">
                    <span className="inline-flex items-center rounded-full bg-green-500 px-3 py-1 text-xs font-semibold text-white">
                      CURRENT PLAN
                    </span>
                  </div>
                )}

                {/* Icon */}
                <div className={`inline-flex rounded-lg p-3 bg-${tier.color}-100 dark:bg-${tier.color}-900 mb-4`}>
                  <Icon className={`h-6 w-6 text-${tier.color}-600 dark:text-${tier.color}-400`} />
                </div>

                {/* Plan Name */}
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {tier.name}
                </h3>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {tier.description}
                </p>

                {/* Price */}
                <div className="mt-6">
                  <div className="flex items-baseline">
                    <span className="text-5xl font-extrabold text-gray-900 dark:text-white">
                      ${displayPrice}
                    </span>
                    {tier.price > 0 && (
                      <span className="ml-2 text-lg font-medium text-gray-500 dark:text-gray-400">
                        /{tier.interval}
                      </span>
                    )}
                  </div>
                  {billingInterval === 'year' && tier.price > 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      ${tier.price * 12}/year billed monthly
                    </p>
                  )}
                </div>

                {/* CTA Button */}
                <button
                  onClick={() => handleSelectPlan(tier)}
                  disabled={loading === tier.id || isCurrentPlan}
                  className={`mt-8 w-full rounded-lg px-4 py-3 text-sm font-semibold transition-all ${
                    tier.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {loading === tier.id ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                  ) : isCurrentPlan ? (
                    'Current Plan'
                  ) : (
                    tier.cta
                  )}
                </button>

                {/* Features */}
                <ul className="mt-8 space-y-3">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                      <span className="ml-3 text-sm text-gray-700 dark:text-gray-300">
                        {feature}
                      </span>
                    </li>
                  ))}
                  {tier.limitations.map((limitation, index) => (
                    <li key={index} className="flex items-start">
                      <X className="h-5 w-5 text-gray-400 shrink-0 mt-0.5" />
                      <span className="ml-3 text-sm text-gray-400 line-through">
                        {limitation}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Need help choosing?
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            All plans include a 14-day free trial. No credit card required.
          </p>
          <div className="flex justify-center space-x-4">
            <a
              href="/docs"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              View Documentation
            </a>
            <span className="text-gray-300">|</span>
            <a
              href="mailto:support@redline.com"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Contact Sales
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

