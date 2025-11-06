import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export async function loginUser(email: string, password: string) {
  const { data } = await api.post('/api/auth/login', { email, password })
  localStorage.setItem('access_token', data.access_token)
  return data
}

export async function registerUser(email: string, password: string, full_name: string) {
  const { data } = await api.post('/api/auth/register', { email, password, full_name })
  localStorage.setItem('access_token', data.access_token)
  return data
}

export async function logoutUser() {
  await api.post('/api/auth/logout')
  localStorage.removeItem('access_token')
}

export async function getCurrentUser() {
  const { data } = await api.get('/api/auth/me')
  return data
}

export async function getSubscription() {
  const { data } = await api.get('/api/subscriptions/me')
  return data
}

export async function createCheckoutSession(priceId: string) {
  const { data } = await api.post('/api/subscriptions/checkout', {
    price_id: priceId,
    success_url: `${window.location.origin}/dashboard?success=true`,
    cancel_url: `${window.location.origin}/dashboard?canceled=true`,
  })
  return data
}

export async function cancelSubscription(immediately: boolean = false) {
  const { data } = await api.post('/api/subscriptions/cancel', { immediately })
  return data
}

export async function getAvailablePrices() {
  const { data } = await api.get('/api/subscriptions/prices')
  return data
}

export async function getDockerImages() {
  const { data } = await api.get('/api/docker/images')
  return data
}

export async function createDownloadToken(imageName: string, tag: string = 'latest') {
  const { data } = await api.post('/api/docker/download-token', { image_name: imageName, tag })
  return data
}

// Two-Factor Authentication Functions
export async function setup2FA() {
  const { data } = await api.post('/api/2fa/setup')
  return data
}

export async function enable2FA(code: string) {
  const { data } = await api.post('/api/2fa/enable', { code })
  return data
}

export async function verify2FA(code: string) {
  const { data } = await api.post('/api/2fa/verify', { code })
  return data
}

export async function verifyBackupCode(backupCode: string) {
  const { data } = await api.post('/api/2fa/verify-backup', { backup_code: backupCode })
  return data
}

export async function disable2FA(password: string, code?: string) {
  const { data } = await api.post('/api/2fa/disable', { password, code })
  return data
}

export async function get2FAStatus() {
  const { data } = await api.get('/api/2fa/status')
  return data
}

export async function complete2FALogin(userId: string, code: string) {
  const { data } = await api.post('/api/auth/login/2fa', { user_id: userId, code })
  localStorage.setItem('access_token', data.access_token)
  return data
}


