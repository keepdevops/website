/**
 * Product Plugin Factory
 * Switch products via environment variable
 * LOC: ~50 lines
 */

import { ProductPlugin } from './interface'
import { createRedlineProduct } from './redline'

// Import other products as they're created
// import { createBluelineProduct } from './blueline'
// import { createGreenlineProduct } from './greenline'

/**
 * Get the active product plugin based on configuration
 */
export function getProduct(productId?: string): ProductPlugin {
  const product = productId || process.env.NEXT_PUBLIC_PRODUCT || 'redline'

  switch (product.toLowerCase()) {
    case 'redline':
      return createRedlineProduct()
    
    // Add more products here as they're created
    // case 'blueline':
    //   return createBluelineProduct()
    
    // case 'greenline':
    //   return createGreenlineProduct()

    default:
      console.warn(`Unknown product: ${product}, defaulting to Redline`)
      return createRedlineProduct()
  }
}

/**
 * Get product by name (useful for multi-product support)
 */
export function getProductByName(name: string): ProductPlugin {
  return getProduct(name)
}

/**
 * List all available products
 */
export function listAvailableProducts(): string[] {
  return [
    'redline',
    // Add more as they're created
    // 'blueline',
    // 'greenline',
  ]
}

/**
 * Check if a product exists
 */
export function productExists(productId: string): boolean {
  return listAvailableProducts().includes(productId.toLowerCase())
}

