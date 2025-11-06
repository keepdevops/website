/**
 * React Hot Toast provider implementation.
 * Lightweight and highly customizable toast library.
 */

'use client'

import toast from 'react-hot-toast'
import { ToastProviderInterface, ToastOptions, ToastId, ToastPromiseMessages } from '../interface'

export class ReactHotToastProvider implements ToastProviderInterface {
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
    return toast.success(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    })
  }

  error(message: string, options?: ToastOptions): ToastId {
    return toast.error(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon,
      className: options?.className,
      style: options?.style
    })
  }

  info(message: string, options?: ToastOptions): ToastId {
    return toast(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon || 'ℹ️',
      className: options?.className,
      style: options?.style
    })
  }

  warning(message: string, options?: ToastOptions): ToastId {
    return toast(message, {
      duration: options?.duration,
      position: this._mapPosition(options?.position),
      icon: options?.icon || '⚠️',
      className: options?.className,
      style: options?.style
    })
  }

  loading(message: string, options?: ToastOptions): ToastId {
    return toast.loading(message, {
      duration: options?.duration || Infinity,
      position: this._mapPosition(options?.position)
    })
  }

  dismiss(toastId?: ToastId): void {
    if (toastId) {
      toast.dismiss(toastId as string)
    } else {
      toast.dismiss()
    }
  }

  async promise<T>(
    promise: Promise<T>,
    messages: ToastPromiseMessages,
    options?: ToastOptions
  ): Promise<T> {
    return toast.promise(
      promise,
      {
        loading: messages.loading,
        success: messages.success,
        error: messages.error
      },
      {
        duration: options?.duration,
        position: this._mapPosition(options?.position)
      }
    )
  }
}

