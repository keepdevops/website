'use client'

import ProtectedRoute from '@/components/auth/ProtectedRoute'
import CustomerTable from '@/components/admin/CustomerTable'
import Link from 'next/link'

export default function AdminCustomersPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Customer Management
            </h1>
            <Link
              href="/admin"
              className="text-blue-600 hover:text-blue-700"
            >
              Back to Admin
            </Link>
          </div>

          <CustomerTable />
        </div>
      </div>
    </ProtectedRoute>
  )
}

