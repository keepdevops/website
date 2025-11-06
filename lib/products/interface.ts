/**
 * Product Plugin Interface
 * All product plugins must implement this interface
 * Constraint: 200 LOC per product implementation
 */

export interface PricingTier {
  id: string
  name: string
  price: number
  interval: 'month' | 'year' | 'forever'
  description: string
  features: string[]
  limitations?: string[]
  priceId: string | null
  stripeProductId?: string
  popular?: boolean
  cta: string
  color?: string
  maxUsers?: number
  maxProjects?: number
  storage?: string
  apiCallsPerMonth?: number
}

export interface ProductFeature {
  id: string
  name: string
  description: string
  availableIn: string[] // tier IDs
  icon?: string
}

export interface ProductMetadata {
  id: string
  name: string
  description: string
  tagline: string
  logo?: string
  brandColor: string
  supportEmail: string
  salesEmail?: string
  docsUrl?: string
}

export interface ProductLimits {
  free: {
    projects: number
    storage: number // in GB
    apiCalls: number
    users: number
  }
  pro: {
    projects: number
    storage: number
    apiCalls: number
    users: number
  }
  enterprise: {
    projects: number | 'unlimited'
    storage: number | 'unlimited'
    apiCalls: number | 'unlimited'
    users: number | 'unlimited'
  }
}

/**
 * Main Product Plugin Interface
 * Each product (Redline, Blueline, etc.) implements this
 */
export interface ProductPlugin {
  // Product metadata
  metadata: ProductMetadata
  
  // Pricing tiers for this product
  tiers: PricingTier[]
  
  // Features breakdown
  features: ProductFeature[]
  
  // Usage limits per tier
  limits: ProductLimits
  
  // Get tier by ID
  getTier(tierId: string): PricingTier | undefined
  
  // Check if user's plan has feature
  hasFeature(tierId: string, featureId: string): boolean
  
  // Get limits for a tier
  getLimits(tierId: string): any
  
  // Validate usage against limits
  validateUsage(tierId: string, usage: {
    projects?: number
    storage?: number
    apiCalls?: number
    users?: number
  }): {
    valid: boolean
    exceeded?: string[]
  }
}

/**
 * Product Plugin Factory
 */
export type ProductPluginFactory = () => ProductPlugin

