'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import SubscriptionCard from '@/components/dashboard/SubscriptionCard'
import Link from 'next/link'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <nav className="bg-white dark:bg-gray-800 shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
              <div className="space-x-4">
                <Link href="/dashboard/billing" className="text-blue-600 hover:text-blue-700">Billing</Link>
                <Link href="/dashboard/downloads" className="text-blue-600 hover:text-blue-700">Downloads</Link>
                <button
                  onClick={() => {
                    localStorage.removeItem('access_token')
                    window.location.href = '/login'
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 gap-6">
            <SubscriptionCard />
            
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Quick Actions
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link
                  href="/dashboard/downloads"
                  className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 transition"
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">Download Software</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Access your Docker images and download tokens
                  </p>
                </Link>
                
                <Link
                  href="/dashboard/billing"
                  className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:border-blue-500 transition"
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">Manage Billing</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Update payment methods and view invoices
                  </p>
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}



