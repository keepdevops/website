/**
 * Toast context provider for managing toast notifications globally.
 */

'use client'

import React, { createContext, useContext, ReactNode } from 'react'
import { Toaster as SonnerToaster } from 'sonner'
import { Toaster as HotToastToaster } from 'react-hot-toast'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { ToastProviderInterface } from './interface'
import { getToastProvider } from './provider-factory'

interface ToastContextType {
  toast: ToastProviderInterface
}

const ToastContext = createContext<ToastContextType | null>(null)

export function useToastContext() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToastContext must be used within ToastProvider')
  }
  return context
}

interface ToastProviderProps {
  children: ReactNode
  provider?: string
}

export function ToastProvider({ children, provider }: ToastProviderProps) {
  const providerName = provider || process.env.NEXT_PUBLIC_TOAST_PROVIDER || 'sonner'
  const toastInstance = getToastProvider(providerName)
  
  return (
    <ToastContext.Provider value={{ toast: toastInstance }}>
      {providerName === 'sonner' && <SonnerToaster position="bottom-right" />}
      {providerName === 'react-hot-toast' && <HotToastToaster position="bottom-right" />}
      {providerName === 'react-toastify' && (
        <ToastContainer
          position="bottom-right"
          autoClose={4000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      )}
      {children}
    </ToastContext.Provider>
  )
}

