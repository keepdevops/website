'use client'

import { useState } from 'react'
import { createDownloadToken } from '@/lib/api-client'

interface DownloadButtonProps {
  imageName: string
  imageTag?: string
}

export default function DownloadButton({ imageName, imageTag = 'latest' }: DownloadButtonProps) {
  const [loading, setLoading] = useState(false)

  const handleDownload = async () => {
    setLoading(true)
    try {
      const tokenData = await createDownloadToken(imageName, imageTag)
      
      const instructions = `
Docker Pull Instructions:
------------------------
1. Use this token as your password (valid for 24 hours):
   ${tokenData.token}

2. Pull the image:
   docker pull ${tokenData.download_url}

3. Or use the token in your docker login:
   echo "${tokenData.token}" | docker login --username download --password-stdin ${tokenData.download_url.split('/')[0]}
      `.trim()
      
      navigator.clipboard.writeText(tokenData.token)
      alert(instructions + '\n\nToken copied to clipboard!')
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate download token')
    } finally {
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleDownload}
      disabled={loading}
      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
    >
      {loading ? 'Generating...' : 'Get Download Token'}
    </button>
  )
}



