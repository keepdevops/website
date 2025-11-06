'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import AnalyticsDashboard from '@/components/admin/AnalyticsDashboard'
import Link from 'next/link'

export default function AdminPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <nav className="bg-white dark:bg-gray-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
              <div className="space-x-4">
                <Link href="/admin/customers" className="text-blue-600 hover:text-blue-700">Customers</Link>
                <Link href="/admin/campaigns" className="text-blue-600 hover:text-blue-700">Campaigns</Link>
                <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">Dashboard</Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-8">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-6">Overview</h2>
            <AnalyticsDashboard />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Link
              href="/admin/customers"
              className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 hover:shadow-lg transition"
            >
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Manage Customers</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                View and manage all customer accounts and subscriptions
              </p>
            </Link>

            <Link
              href="/admin/campaigns"
              className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 hover:shadow-lg transition"
            >
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Email Campaigns</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Create and manage email marketing campaigns
              </p>
            </Link>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}



