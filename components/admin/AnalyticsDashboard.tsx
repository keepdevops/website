'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api-client'
import type { AnalyticsData } from '@/lib/types'

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const { data } = await api.get('/api/analytics/overview')
      setAnalytics(data)
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-48 rounded-lg"></div>
  }

  if (!analytics) return null

  const stats = [
    {
      name: 'Total Users',
      value: analytics.total_users,
      color: 'bg-blue-500'
    },
    {
      name: 'Active Subscriptions',
      value: analytics.active_subscriptions,
      color: 'bg-green-500'
    },
    {
      name: 'Monthly Revenue',
      value: `$${analytics.monthly_revenue.toFixed(2)}`,
      color: 'bg-purple-500'
    },
    {
      name: 'Conversion Rate',
      value: `${analytics.conversion_rate.toFixed(1)}%`,
      color: 'bg-yellow-500'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <div key={stat.name} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center mb-4`}>
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.name}</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">{stat.value}</p>
        </div>
      ))}
    </div>
  )
}

