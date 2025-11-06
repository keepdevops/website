/**
 * Tests for toast provider implementations.
 */

import { describe, it, expect, vi } from '@jest/globals'
import { ToastProviderInterface } from '../lib/toast/interface'
import { ReactHotToastProvider } from '../lib/toast/providers/react-hot-toast'
import { SonnerToastProvider } from '../lib/toast/providers/sonner'
import { ReactToastifyProvider } from '../lib/toast/providers/react-toastify'
import { CustomToastProvider } from '../lib/toast/providers/custom'

describe('ToastProviderInterface', () => {
  it('should have all required methods', () => {
    const required = ['success', 'error', 'info', 'warning', 'loading', 'dismiss', 'promise']
    const provider = new CustomToastProvider()
    
    required.forEach(method => {
      expect(typeof (provider as any)[method]).toBe('function')
    })
  })
})

describe('CustomToastProvider', () => {
  it('should show success toast', () => {
    const provider = new CustomToastProvider()
    const id = provider.success('Success message')
    
    expect(id).toBeDefined()
    expect(provider.getToasts()).toHaveLength(1)
    expect(provider.getToasts()[0].type).toBe('success')
  })

  it('should show error toast', () => {
    const provider = new CustomToastProvider()
    const id = provider.error('Error message')
    
    expect(id).toBeDefined()
    const toasts = provider.getToasts()
    expect(toasts[0].type).toBe('error')
  })

  it('should dismiss toast by id', () => {
    const provider = new CustomToastProvider()
    const id = provider.info('Info message')
    
    expect(provider.getToasts()).toHaveLength(1)
    
    provider.dismiss(id)
    
    expect(provider.getToasts()).toHaveLength(0)
  })

  it('should dismiss all toasts', () => {
    const provider = new CustomToastProvider()
    
    provider.success('Toast 1')
    provider.error('Toast 2')
    provider.info('Toast 3')
    
    expect(provider.getToasts()).toHaveLength(3)
    
    provider.dismiss()
    
    expect(provider.getToasts()).toHaveLength(0)
  })

  it('should handle promise success', async () => {
    const provider = new CustomToastProvider()
    const promise = Promise.resolve('result')
    
    const result = await provider.promise(promise, {
      loading: 'Loading...',
      success: 'Success!',
      error: 'Error!'
    })
    
    expect(result).toBe('result')
  })

  it('should handle promise error', async () => {
    const provider = new CustomToastProvider()
    const promise = Promise.reject(new Error('Test error'))
    
    await expect(
      provider.promise(promise, {
        loading: 'Loading...',
        success: 'Success!',
        error: 'Error!'
      })
    ).rejects.toThrow('Test error')
  })
})

describe('SonnerToastProvider', () => {
  it('should create instance', () => {
    const provider = new SonnerToastProvider()
    expect(provider).toBeDefined()
    expect(typeof provider.success).toBe('function')
  })
})

describe('ReactHotToastProvider', () => {
  it('should create instance', () => {
    const provider = new ReactHotToastProvider()
    expect(provider).toBeDefined()
    expect(typeof provider.error).toBe('function')
  })
})

describe('ReactToastifyProvider', () => {
  it('should create instance', () => {
    const provider = new ReactToastifyProvider()
    expect(provider).toBeDefined()
    expect(typeof provider.warning).toBe('function')
  })
})

