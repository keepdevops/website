export interface User {
  id: string
  email: string
  full_name: string
  is_admin: boolean
  created_at: string
}

export interface Subscription {
  id: string
  user_id: string
  stripe_customer_id: string
  stripe_subscription_id: string
  status: string
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
}

export interface PriceInfo {
  id: string
  product_id: string
  unit_amount: number
  currency: string
  recurring_interval?: string
  product_name: string
  product_description?: string
}

export interface DockerImage {
  id: string
  name: string
  tag: string
  registry_url: string
  size_mb?: number
  created_at: string
}

export interface Customer {
  id: string
  email: string
  full_name: string
  subscription_status?: string
  created_at: string
  is_admin: boolean
}

export interface Campaign {
  id: string
  name: string
  subject: string
  content: string
  segment: string
  status: string
  total_recipients: number
  opened_count: number
  clicked_count: number
  created_at: string
}

export interface AnalyticsData {
  total_users: number
  active_subscriptions: number
  monthly_revenue: number
  churn_rate: number
  conversion_rate: number
}



