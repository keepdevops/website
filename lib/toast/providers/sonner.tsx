/**
 * Sonner toast provider implementation.
 * Modern, beautiful toast notifications with great defaults.
 */

'use client'

import { toast as sonnerToast } from 'sonner'
import { ToastProviderInterface, ToastOptions, ToastId, ToastPromiseMessages } from '../interface'

export class SonnerToastProvider implements ToastProviderInterface {
  private _mapPosition(position?: string): any {
    const positionMap: Record<string, any> = {
      'top-left': 'top-left',
      'top-right': 'top-right',
      'top-center': 'top-center',
      'bottom-left': 'bottom-left',
      'bottom-right': 'bottom-right',
      'bottom-center': 'bottom-center'
    }
    return positionMap[position || 'bottom-right'] || 'bottom-right'
  }

  success(message: string, options?: ToastOptions): ToastId {
    return sonnerToast.success(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      action: options?.action,
      className: options?.className
    })
  }

  error(message: string, options?: ToastOptions): ToastId {
    return sonnerToast.error(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      action: options?.action,
      className: options?.className
    })
  }

  info(message: string, options?: ToastOptions): ToastId {
    return sonnerToast.info(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      action: options?.action,
      className: options?.className
    })
  }

  warning(message: string, options?: ToastOptions): ToastId {
    return sonnerToast.warning(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      action: options?.action,
      className: options?.className
    })
  }

  loading(message: string, options?: ToastOptions): ToastId {
    return sonnerToast.loading(message, {
      duration: options?.duration || Infinity,
      position: this._mapPosition(options?.position)
    })
  }

  dismiss(toastId?: ToastId): void {
    if (toastId) {
      sonnerToast.dismiss(toastId)
    } else {
      sonnerToast.dismiss()
    }
  }

  async promise<T>(
    promise: Promise<T>,
    messages: ToastPromiseMessages,
    options?: ToastOptions
  ): Promise<T> {
    return sonnerToast.promise(promise, {
      loading: messages.loading,
      success: messages.success,
      error: messages.error,
      duration: options?.duration,
      position: this._mapPosition(options?.position)
    })
  }
}

