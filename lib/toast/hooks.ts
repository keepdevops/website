/**
 * Toast hooks for easy access to toast notifications.
 */

'use client'

import { useToastContext } from './context'
import { ToastProviderInterface } from './interface'

/**
 * Hook to access toast notifications
 */
export function useToast(): ToastProviderInterface {
  const { toast } = useToastContext()
  return toast
}

