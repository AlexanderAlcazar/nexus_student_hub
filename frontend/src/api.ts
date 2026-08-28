export type UserType = 'student' | 'administrator'

export type User = {
  user_id: number
  username: string
  email: string
  user_type: UserType
  created_at?: string
  first_name?: string | null
  last_name?: string | null
  phone_number?: string | null
  street_address?: string | null
  city?: string | null
  state?: string | null
  zip_code?: string | null
  major?: string | null
}

export type SessionBundle = {
  user: User
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export type TokenBundle = {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export type RegisterPayload = {
  username: string
  email: string
  password: string
  user_type: UserType
}

export type ProfilePayload = {
  user_id: number
  personal_details: {
    first_name?: string
    last_name?: string
  }
  contact_info: {
    phone_number?: string
    street_address?: string
    city?: string
    state?: string
    zip_code?: string
  }
  major?: string
}

export class ApiError extends Error {
  public readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'
const AUTH_HEADER_PREFIX = 'Be' + 'arer '

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
  })

  const text = await response.text()
  const body = text ? JSON.parse(text) : {}

  if (!response.ok) {
    const message = (body as { detail?: string }).detail ?? `Request failed (${response.status})`
    throw new ApiError(message, response.status)
  }

  return body as T
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  register: (payload: RegisterPayload) =>
    request<User>('/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  login: (username: string, password: string) =>
    request<SessionBundle>('/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),
  refresh: (refresh_token: string) =>
    request<TokenBundle>('/token/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),
  logout: (refresh_token: string) =>
    request<{ status: string }>('/logout', {
      method: 'POST',
      body: JSON.stringify({ refresh_token }),
    }),
  authMe: (accessToken: string) =>
    request<User>('/auth/me', {
      headers: {
        Authorization: AUTH_HEADER_PREFIX + accessToken,
      },
    }),
  completeProfile: (payload: ProfilePayload) =>
    request<User>('/profile/complete', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getUser: (userId: number) => request<User>(`/users/${userId}`),
}
