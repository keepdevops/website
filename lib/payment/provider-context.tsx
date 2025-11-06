'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { api } from '@/lib/api-client'
import type { CheckoutSession, BillingPortalSession, Price, Subscription, PaymentContextType } from './types'

const PaymentContext = createContext<PaymentContextType | undefined>(undefined)

interface PaymentProviderProps {
  children: ReactNode
  provider?: string
}

export function PaymentProvider({ children, provider = 'stripe' }: PaymentProviderProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createCheckout = useCallback(async (
    priceId: string,
    successUrl: string,
    cancelUrl: string
  ): Promise<CheckoutSession> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data } = await api.post('/api/subscriptions/checkout', {
        price_id: priceId,
        success_url: successUrl,
        cancel_url: cancelUrl,
        mode: 'subscription'
      })
      
      return data
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to create checkout session'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getSubscription = useCallback(async (): Promise<Subscription | null> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data } = await api.get('/api/subscriptions/me')
      
      if (data.status === 'no_subscription') {
        return null
      }
      
      return data
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to get subscription'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const cancelSubscription = useCallback(async (immediately: boolean = false): Promise<void> => {
    setIsLoading(true)
    setError(null)
    
    try {
      await api.post('/api/subscriptions/cancel', { immediately })
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to cancel subscription'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const openBillingPortal = useCallback(async (returnUrl: string): Promise<void> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data } = await api.post('/api/subscriptions/billing-portal', {
        return_url: returnUrl
      })
      
      // Redirect to billing portal
      window.location.href = data.url
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to open billing portal'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const getPrices = useCallback(async (): Promise<Price[]> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data } = await api.get('/api/subscriptions/prices')
      return data
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to get prices'
      setError(errorMsg)
      throw new Error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const value: PaymentContextType = {
    createCheckout,
    getSubscription,
    cancelSubscription,
    openBillingPortal,
    getPrices,
    isLoading,
    error
  }

  return (
    <PaymentContext.Provider value={value}>
      {children}
    </PaymentContext.Provider>
  )
}

export function usePayment() {
  const context = useContext(PaymentContext)
  
  if (context === undefined) {
    throw new Error('usePayment must be used within a PaymentProvider')
  }
  
  return context
}


