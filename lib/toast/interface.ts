/**
 * Abstract interface for toast notification providers.
 * Defines common operations for displaying user feedback messages.
 */

export type ToastPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center'

export type ToastId = string | number

export interface ToastOptions {
  duration?: number
  position?: ToastPosition
  icon?: React.ReactNode
  action?: {
    label: string
    onClick: () => void
  }
  className?: string
  style?: React.CSSProperties
}

export interface ToastPromiseMessages {
  loading: string
  success: string
  error: string
}

export interface ToastProviderInterface {
  /**
   * Show success toast
   */
  success(message: string, options?: ToastOptions): ToastId
  
  /**
   * Show error toast
   */
  error(message: string, options?: ToastOptions): ToastId
  
  /**
   * Show info toast
   */
  info(message: string, options?: ToastOptions): ToastId
  
  /**
   * Show warning toast
   */
  warning(message: string, options?: ToastOptions): ToastId
  
  /**
   * Show loading toast
   */
  loading(message: string, options?: ToastOptions): ToastId
  
  /**
   * Dismiss toast by ID or all toasts
   */
  dismiss(toastId?: ToastId): void
  
  /**
   * Show promise-based toast with loading, success, and error states
   */
  promise<T>(
    promise: Promise<T>,
    messages: ToastPromiseMessages,
    options?: ToastOptions
  ): Promise<T>
}

