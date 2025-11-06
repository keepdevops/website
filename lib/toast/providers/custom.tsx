/**
 * Custom toast provider implementation.
 * Simple internal implementation with no external dependencies.
 */

'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'
import { ToastProviderInterface, ToastOptions, ToastId, ToastPromiseMessages, ToastPosition } from '../interface'

interface Toast {
  id: ToastId
  type: 'success' | 'error' | 'info' | 'warning' | 'loading'
  message: string
  options?: ToastOptions
}

export class CustomToastProvider implements ToastProviderInterface {
  private toasts: Toast[] = []
  private listeners: Set<(toasts: Toast[]) => void> = new Set()
  private nextId = 1

  private _addToast(type: Toast['type'], message: string, options?: ToastOptions): ToastId {
    const id = this.nextId++
    const toast: Toast = { id, type, message, options }
    
    this.toasts.push(toast)
    this._notify()
    
    const duration = options?.duration || 4000
    if (duration !== Infinity) {
      setTimeout(() => this.dismiss(id), duration)
    }
    
    return id
  }

  private _notify() {
    this.listeners.forEach(listener => listener([...this.toasts]))
  }

  subscribe(listener: (toasts: Toast[]) => void): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }

  success(message: string, options?: ToastOptions): ToastId {
    return this._addToast('success', message, options)
  }

  error(message: string, options?: ToastOptions): ToastId {
    return this._addToast('error', message, options)
  }

  info(message: string, options?: ToastOptions): ToastId {
    return this._addToast('info', message, options)
  }

  warning(message: string, options?: ToastOptions): ToastId {
    return this._addToast('warning', message, options)
  }

  loading(message: string, options?: ToastOptions): ToastId {
    return this._addToast('loading', message, { ...options, duration: Infinity })
  }

  dismiss(toastId?: ToastId): void {
    if (toastId) {
      this.toasts = this.toasts.filter(t => t.id !== toastId)
    } else {
      this.toasts = []
    }
    this._notify()
  }

  async promise<T>(
    promise: Promise<T>,
    messages: ToastPromiseMessages,
    options?: ToastOptions
  ): Promise<T> {
    const loadingId = this.loading(messages.loading, options)
    
    try {
      const result = await promise
      this.dismiss(loadingId)
      this.success(messages.success, options)
      return result
    } catch (error) {
      this.dismiss(loadingId)
      this.error(messages.error, options)
      throw error
    }
  }

  getToasts(): Toast[] {
    return [...this.toasts]
  }
}

// Singleton instance
export const customToastProvider = new CustomToastProvider()

