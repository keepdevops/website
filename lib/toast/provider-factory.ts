/**
 * Factory for creating toast provider instances.
 * Supports React Hot Toast, Sonner, React Toastify, and Custom providers.
 */

import { ToastProviderInterface } from './interface'

export function getToastProvider(providerName?: string): ToastProviderInterface {
  const provider = providerName || process.env.NEXT_PUBLIC_TOAST_PROVIDER || 'sonner'
  
  switch (provider) {
    case 'react-hot-toast':
      const { ReactHotToastProvider } = require('./providers/react-hot-toast')
      return new ReactHotToastProvider()
    
    case 'sonner':
      const { SonnerToastProvider } = require('./providers/sonner')
      return new SonnerToastProvider()
    
    case 'react-toastify':
      const { ReactToastifyProvider } = require('./providers/react-toastify')
      return new ReactToastifyProvider()
    
    case 'custom':
      const { CustomToastProvider } = require('./providers/custom')
      return new CustomToastProvider()
    
    default:
      throw new Error(
        `Unsupported toast provider: ${provider}. ` +
        `Supported: react-hot-toast, sonner, react-toastify, custom`
      )
  }
}

