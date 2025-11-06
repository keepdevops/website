export interface CheckoutSession {
  session_id: string
  url: string
}

export interface BillingPortalSession {
  url: string
}

export interface Price {
  id: string
  product_id: string
  unit_amount: number
  currency: string
  recurring_interval?: string | null
  product_name: string
  product_description?: string | null
}

export interface Subscription {
  id: string
  user_id: string
  stripe_customer_id: string
  stripe_subscription_id: string
  status: string
  current_period_end?: string
  cancel_at_period_end?: boolean
}

export interface PaymentContextType {
  createCheckout: (priceId: string, successUrl: string, cancelUrl: string) => Promise<CheckoutSession>
  getSubscription: () => Promise<Subscription | null>
  cancelSubscription: (immediately?: boolean) => Promise<void>
  openBillingPortal: (returnUrl: string) => Promise<void>
  getPrices: () => Promise<Price[]>
  isLoading: boolean
  error: string | null
}


