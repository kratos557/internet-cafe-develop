import { describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { getAuthHeader, setAccessToken } from '../api/client'
import { useSessionStore } from '../stores/session'

describe('session store', () => {
  it('guarda solo nombre y rol', () => {
    setActivePinia(createPinia())
    const session = useSessionStore()
    session.setUser('Ana Pérez', 'student')
    expect(session.isAuthenticated).toBe(true)
    expect(session.isAdmin).toBe(false)
    expect(Object.keys(session.$state).sort()).toEqual(['fullName', 'role'])
    session.clear()
    expect(session.isAuthenticated).toBe(false)
  })
})

describe('api client', () => {
  it('arma el header Authorization solo si hay token en memoria', () => {
    expect(getAuthHeader()).toEqual({})
    setAccessToken('abc')
    expect(getAuthHeader()).toEqual({ Authorization: 'Bearer abc' })
    setAccessToken(null)
    expect(getAuthHeader()).toEqual({})
  })
})
