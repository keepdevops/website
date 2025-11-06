/**
 * React Toastify provider implementation.
 * Feature-rich, established toast notification library.
 */

'use client'

import { toast as toastifyToast, Id } from 'react-toastify'
import { ToastProviderInterface, ToastOptions, ToastId, ToastPromiseMessages } from '../interface'

export class ReactToastifyProvider implements ToastProviderInterface {
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
    return toastifyToast.success(message, {
      autoClose: options?.duration || 4000,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    }) as ToastId
  }

  error(message: string, options?: ToastOptions): ToastId {
    return toastifyToast.error(message, {
      autoClose: options?.duration || 4000,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    }) as ToastId
  }

  info(message: string, options?: ToastOptions): ToastId {
    return toastifyToast.info(message, {
      autoClose: options?.duration || 4000,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    }) as ToastId
  }

  warning(message: string, options?: ToastOptions): ToastId {
    return toastifyToast.warning(message, {
      autoClose: options?.duration || 4000,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    }) as ToastId
  }

  loading(message: string, options?: ToastOptions): ToastId {
    return toastifyToast.info(message, {
      autoClose: false,
      position: this._mapPosition(options?.position),
      closeButton: false,
      isLoading: true
    }) as ToastId
  }

  dismiss(toastId?: ToastId): void {
    if (toastId) {
      toastifyToast.dismiss(toastId as Id)
    } else {
      toastifyToast.dismiss()
    }
  }

  async promise<T>(
    promise: Promise<T>,
    messages: ToastPromiseMessages,
    options?: ToastOptions
  ): Promise<T> {
    return toastifyToast.promise(
      promise,
      {
        pending: messages.loading,
        success: messages.success,
        error: messages.error
      },
      {
        autoClose: options?.duration || 4000,
        position: this._mapPosition(options?.position)
      }
    )
  }
}

