/**
 * Cliente HTTP (placeholder). Más adelante se reemplaza por openapi-fetch.
 * El access token vive SOLO en esta variable de módulo: nunca en
 * localStorage, sessionStorage ni Pinia (SRS 12.2).
 */
let accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function getAuthHeader(): Record<string, string> {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {}
}
