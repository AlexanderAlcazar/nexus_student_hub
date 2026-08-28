import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError, api, type User, type UserType } from './api'
import './App.css'

type View = 'login' | 'register' | 'dashboard' | 'profile'

const REFRESH_TOKEN_KEY = 'nexus.refresh_token'

function App() {
  const [view, setView] = useState<View>('login')
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')
  const [user, setUser] = useState<User | null>(null)
  const [profilePreview, setProfilePreview] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    user_type: 'student' as UserType,
  })

  const [loginForm, setLoginForm] = useState({ username: '', password: '' })

  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    street_address: '',
    city: '',
    state: '',
    zip_code: '',
    major: '',
  })

  const isLoggedIn = Boolean(user && accessToken)

  useEffect(() => {
    const stored = window.localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!stored) {
      return
    }

    setRefreshToken(stored)
    void bootstrapSession(stored)
  }, [])

  async function bootstrapSession(storedRefresh: string) {
    setLoading(true)
    setMessage('Restoring session...')

    try {
      const refreshed = await api.refresh(storedRefresh)
      const me = await api.authMe(refreshed.access_token)
      setAccessToken(refreshed.access_token)
      setRefreshToken(refreshed.refresh_token)
      window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshed.refresh_token)
      setUser(me)
      setView('dashboard')
      setMessage(`Welcome back, ${me.username}`)
    } catch {
      clearSession()
    } finally {
      setLoading(false)
    }
  }

  function clearSession() {
    setAccessToken('')
    setRefreshToken('')
    setUser(null)
    setProfilePreview(null)
    window.localStorage.removeItem(REFRESH_TOKEN_KEY)
    setView('login')
  }

  async function runWithRefresh<T>(fn: (token: string) => Promise<T>): Promise<T> {
    if (!accessToken) {
      throw new Error('Not authenticated.')
    }

    try {
      return await fn(accessToken)
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401 || !refreshToken) {
        throw error
      }

      const rotated = await api.refresh(refreshToken)
      setAccessToken(rotated.access_token)
      setRefreshToken(rotated.refresh_token)
      window.localStorage.setItem(REFRESH_TOKEN_KEY, rotated.refresh_token)
      return await fn(rotated.access_token)
    }
  }

  async function handleRegister(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const created = await api.register(registerForm)
      setMessage(`Account created for ${created.username}. Please log in.`)
      setView('login')
      setLoginForm({ username: created.username, password: '' })
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleLogin(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const session = await api.login(loginForm.username, loginForm.password)
      setAccessToken(session.access_token)
      setRefreshToken(session.refresh_token)
      setUser(session.user)
      window.localStorage.setItem(REFRESH_TOKEN_KEY, session.refresh_token)
      setView('dashboard')
      setMessage(`Logged in as ${session.user.username}`)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleLogout() {
    setLoading(true)
    setMessage('')
    try {
      if (refreshToken) {
        await api.logout(refreshToken)
      }
      clearSession()
      setMessage('Logged out.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Logout failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleLoadProfile() {
    if (!user) {
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const profile = await runWithRefresh(() => api.getUser(user.user_id))
      setProfilePreview(profile)
      setMessage('Loaded profile from API.')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Could not load profile.')
    } finally {
      setLoading(false)
    }
  }

  async function handleCompleteProfile(event: FormEvent) {
    event.preventDefault()

    if (!user) {
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const completed = await runWithRefresh(() =>
        api.completeProfile({
          user_id: user.user_id,
          personal_details: {
            first_name: profileForm.first_name || undefined,
            last_name: profileForm.last_name || undefined,
          },
          contact_info: {
            phone_number: profileForm.phone_number || undefined,
            street_address: profileForm.street_address || undefined,
            city: profileForm.city || undefined,
            state: profileForm.state || undefined,
            zip_code: profileForm.zip_code || undefined,
          },
          major: profileForm.major || undefined,
        }),
      )

      setProfilePreview(completed)
      setMessage('Profile completed.')
      setView('dashboard')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Profile update failed.')
    } finally {
      setLoading(false)
    }
  }

  const title = useMemo(() => {
    if (view === 'login') return 'Sign in'
    if (view === 'register') return 'Create account'
    if (view === 'profile') return 'Complete profile'
    return 'Dashboard'
  }, [view])

  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1>Nexus Student Hub</h1>
        <p>Frontend prototype for visualizing your app experience.</p>
      </header>

      <section className="card">
        <h2>{title}</h2>

        {message && <p className="status">{message}</p>}

        {view === 'register' && (
          <form onSubmit={handleRegister} className="form-grid">
            <label>
              Username
              <input
                required
                minLength={3}
                value={registerForm.username}
                onChange={(event) => setRegisterForm((current) => ({ ...current, username: event.target.value }))}
              />
            </label>
            <label>
              Email
              <input
                required
                type="email"
                value={registerForm.email}
                onChange={(event) => setRegisterForm((current) => ({ ...current, email: event.target.value }))}
              />
            </label>
            <label>
              Password
              <input
                required
                type="password"
                minLength={8}
                value={registerForm.password}
                onChange={(event) => setRegisterForm((current) => ({ ...current, password: event.target.value }))}
              />
            </label>
            <label>
              User type
              <select
                value={registerForm.user_type}
                onChange={(event) =>
                  setRegisterForm((current) => ({ ...current, user_type: event.target.value as UserType }))
                }
              >
                <option value="student">Student</option>
                <option value="administrator">Administrator</option>
              </select>
            </label>
            <button disabled={loading} type="submit">
              {loading ? 'Creating...' : 'Create account'}
            </button>
            <button disabled={loading} type="button" className="secondary" onClick={() => setView('login')}>
              Back to login
            </button>
          </form>
        )}

        {view === 'login' && (
          <form onSubmit={handleLogin} className="form-grid">
            <label>
              Username
              <input
                required
                value={loginForm.username}
                onChange={(event) => setLoginForm((current) => ({ ...current, username: event.target.value }))}
              />
            </label>
            <label>
              Password
              <input
                required
                type="password"
                value={loginForm.password}
                onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
              />
            </label>
            <button disabled={loading} type="submit">
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
            <button disabled={loading} type="button" className="secondary" onClick={() => setView('register')}>
              Need an account?
            </button>
          </form>
        )}

        {view === 'profile' && isLoggedIn && user && (
          <form onSubmit={handleCompleteProfile} className="form-grid">
            <label>
              First name
              <input
                value={profileForm.first_name}
                onChange={(event) => setProfileForm((current) => ({ ...current, first_name: event.target.value }))}
              />
            </label>
            <label>
              Last name
              <input
                value={profileForm.last_name}
                onChange={(event) => setProfileForm((current) => ({ ...current, last_name: event.target.value }))}
              />
            </label>
            <label>
              Phone number
              <input
                value={profileForm.phone_number}
                onChange={(event) => setProfileForm((current) => ({ ...current, phone_number: event.target.value }))}
              />
            </label>
            <label>
              Street address
              <input
                value={profileForm.street_address}
                onChange={(event) => setProfileForm((current) => ({ ...current, street_address: event.target.value }))}
              />
            </label>
            <label>
              City
              <input
                value={profileForm.city}
                onChange={(event) => setProfileForm((current) => ({ ...current, city: event.target.value }))}
              />
            </label>
            <label>
              State
              <input
                value={profileForm.state}
                onChange={(event) => setProfileForm((current) => ({ ...current, state: event.target.value }))}
              />
            </label>
            <label>
              Zip code
              <input
                value={profileForm.zip_code}
                onChange={(event) => setProfileForm((current) => ({ ...current, zip_code: event.target.value }))}
              />
            </label>
            {user.user_type === 'student' && (
              <label>
                Major
                <input
                  value={profileForm.major}
                  onChange={(event) => setProfileForm((current) => ({ ...current, major: event.target.value }))}
                />
              </label>
            )}
            <button disabled={loading} type="submit">
              {loading ? 'Saving...' : 'Save profile'}
            </button>
            <button disabled={loading} type="button" className="secondary" onClick={() => setView('dashboard')}>
              Cancel
            </button>
          </form>
        )}

        {view === 'dashboard' && isLoggedIn && user && (
          <div className="dashboard">
            <div className="actions">
              <button disabled={loading} type="button" onClick={() => setView('profile')}>
                Complete profile
              </button>
              <button disabled={loading} type="button" className="secondary" onClick={handleLoadProfile}>
                Load profile
              </button>
              <button disabled={loading} type="button" className="secondary" onClick={handleLogout}>
                Logout
              </button>
            </div>

            <div className="panel">
              <h3>Current user</h3>
              <pre>{JSON.stringify(user, null, 2)}</pre>
            </div>

            {profilePreview && (
              <div className="panel">
                <h3>Profile preview</h3>
                <pre>{JSON.stringify(profilePreview, null, 2)}</pre>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  )
}

export default App
