'use client'

import { useEffect, useState } from 'react'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import DownloadButton from '@/components/dashboard/DownloadButton'
import { getDockerImages } from '@/lib/api-client'
import type { DockerImage } from '@/lib/types'

export default function DownloadsPage() {
  const [images, setImages] = useState<DockerImage[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadImages()
  }, [])

  const loadImages = async () => {
    try {
      const data = await getDockerImages()
      setImages(data)
    } catch (error) {
      console.error('Error loading images:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Available Downloads
          </h1>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : images.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <p className="text-gray-600 dark:text-gray-400">
                No images available. Please subscribe to access downloads.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {images.map((image) => (
                <div key={image.id} className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {image.name}:{image.tag}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Registry: {image.registry_url}
                      </p>
                      {image.size_mb && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Size: {image.size_mb} MB
                        </p>
                      )}
                    </div>
                    <DownloadButton imageName={image.name} imageTag={image.tag} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  )
}

