import { loadStripe, Stripe } from '@stripe/stripe-js'

let stripePromise: Promise<Stripe | null> | null = null

/**
 * Get Stripe.js instance
 */
export function getStripe(): Promise<Stripe | null> {
  if (!stripePromise) {
    const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
    
    if (!publishableKey) {
      console.error('Stripe publishable key not configured')
      return Promise.resolve(null)
    }
    
    stripePromise = loadStripe(publishableKey)
  }
  
  return stripePromise
}

/**
 * Redirect to Stripe Checkout
 * 
 * @param sessionId - Checkout session ID from backend
 */
export async function redirectToCheckout(sessionId: string): Promise<void> {
  const stripe = await getStripe()
  
  if (!stripe) {
    throw new Error('Stripe not initialized')
  }
  
  const { error } = await stripe.redirectToCheckout({ sessionId })
  
  if (error) {
    throw new Error(error.message)
  }
}

/**
 * Create checkout session and redirect to Stripe
 * 
 * @param priceId - Stripe price ID
 * @param createSessionFn - Function that creates checkout session on backend
 */
export async function createAndRedirectToCheckout(
  priceId: string,
  createSessionFn: (priceId: string, successUrl: string, cancelUrl: string) => Promise<{ session_id: string; url: string }>
): Promise<void> {
  const successUrl = `${window.location.origin}/dashboard?checkout=success`
  const cancelUrl = `${window.location.origin}/dashboard?checkout=cancel`
  
  // Create session on backend
  const session = await createSessionFn(priceId, successUrl, cancelUrl)
  
  // Redirect to Stripe Checkout
  if (session.url) {
    window.location.href = session.url
  } else {
    await redirectToCheckout(session.session_id)
  }
}


