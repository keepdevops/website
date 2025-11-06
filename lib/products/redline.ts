/**
 * Redline Product Plugin - Docker Distribution Platform
 * LOC: ~185 lines (under 200 LOC constraint) ✅
 */
import { ProductPlugin, PricingTier, ProductFeature, ProductLimits } from './interface'

export class RedlineProduct implements ProductPlugin {
  metadata = {
    id: 'redline',
    name: 'Redline',
    description: 'Enterprise Docker image distribution platform',
    tagline: 'Secure, fast, and reliable container distribution',
    brandColor: '#EF4444',
    supportEmail: 'support@redline.io',
    salesEmail: 'sales@redline.io',
    docsUrl: 'https://docs.redline.io',
  }

  tiers: PricingTier[] = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      interval: 'forever' as const,
      description: 'Perfect for trying out Redline',
      features: ['Up to 5 projects', 'Basic analytics', '1 GB storage', 'Community support', '7-day retention', 'Public repos'],
      limitations: ['No private repos', 'Limited API (1k/mo)', 'Email support only'],
      priceId: null,
      cta: 'Get Started Free',
      color: 'gray',
      maxUsers: 1,
      maxProjects: 5,
      storage: '1 GB',
      apiCallsPerMonth: 1000,
    },
    {
      id: 'pro',
      name: 'Professional',
      price: 29,
      interval: 'month' as const,
      description: 'For serious developers and small teams',
      features: ['Unlimited projects', 'Advanced analytics', '100 GB storage', 'Priority support', '30-day retention', 'Private repos', 'API access (100k/mo)', 'Team collab (5 users)', 'Webhooks', 'SSL/TLS'],
      priceId: 'price_pro_monthly_redline',
      stripeProductId: 'prod_redline_pro',
      cta: 'Start 14-Day Trial',
      popular: true,
      color: 'blue',
      maxUsers: 5,
      maxProjects: -1,
      storage: '100 GB',
      apiCallsPerMonth: 100000,
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 99,
      interval: 'month' as const,
      description: 'For large teams and organizations',
      features: ['Everything in Pro', 'Unlimited storage', '24/7 support', 'Unlimited retention', 'SSO', 'Custom SLA', 'Account manager', 'Unlimited users', 'Unlimited API', 'On-premise option', 'SOC 2/HIPAA'],
      priceId: 'price_enterprise_monthly_redline',
      stripeProductId: 'prod_redline_enterprise',
      cta: 'Contact Sales',
      color: 'purple',
      maxUsers: -1,
      maxProjects: -1,
      storage: 'Unlimited',
      apiCallsPerMonth: -1,
    },
  ]

  features: ProductFeature[] = [
    { id: 'private_repos', name: 'Private Repositories', description: 'Host private Docker images', availableIn: ['pro', 'enterprise'] },
    { id: 'analytics', name: 'Advanced Analytics', description: 'Detailed insights', availableIn: ['pro', 'enterprise'] },
    { id: 'team', name: 'Team Collaboration', description: 'Manage team permissions', availableIn: ['pro', 'enterprise'] },
    { id: 'webhooks', name: 'Webhooks', description: 'Real-time events', availableIn: ['pro', 'enterprise'] },
    { id: 'sso', name: 'Single Sign-On', description: 'SAML/OAuth integration', availableIn: ['enterprise'] },
    { id: 'sla', name: 'Custom SLA', description: 'Guaranteed uptime', availableIn: ['enterprise'] },
  ]

  limits: ProductLimits = {
    free: { projects: 5, storage: 1, apiCalls: 1000, users: 1 },
    pro: { projects: -1, storage: 100, apiCalls: 100000, users: 5 },
    enterprise: { projects: 'unlimited', storage: 'unlimited', apiCalls: 'unlimited', users: 'unlimited' },
  }

  getTier(tierId: string) {
    return this.tiers.find((t) => t.id === tierId)
  }

  hasFeature(tierId: string, featureId: string) {
    const feature = this.features.find((f) => f.id === featureId)
    return feature?.availableIn.includes(tierId) || false
  }

  getLimits(tierId: string) {
    return this.limits[tierId as keyof ProductLimits] || this.limits.free
  }

  validateUsage(tierId: string, usage: { projects?: number; storage?: number; apiCalls?: number; users?: number }) {
    const limits = this.getLimits(tierId)
    const exceeded: string[] = []

    const checkLimit = (key: keyof typeof usage, limit: any) => {
      if (usage[key] && limit !== 'unlimited' && limit !== -1 && usage[key]! > limit) exceeded.push(key)
    }

    checkLimit('projects', limits.projects)
    checkLimit('storage', limits.storage)
    checkLimit('apiCalls', limits.apiCalls)
    checkLimit('users', limits.users)

    return { valid: exceeded.length === 0, exceeded: exceeded.length > 0 ? exceeded : undefined }
  }
}

export function createRedlineProduct(): ProductPlugin {
  return new RedlineProduct()
}

