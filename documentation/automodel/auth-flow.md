# Auth Flow

## Overview

Google OAuth2 for login. JWTs for session management. No passwords stored.

## Sequence

```
1. User clicks "Sign in with Google"
   -> GET /api/auth/google
   -> 302 redirect to accounts.google.com

2. User consents on Google
   -> Google redirects to GET /api/auth/google/callback?code=...

3. Backend exchanges code for tokens
   -> Fetches user profile (email, name, picture, sub)
   -> Creates or updates User row in DB
   -> Issues JWT with {sub: user_id, email, name, exp}
   -> 302 redirect to /?token=<jwt>

4. Frontend receives token
   -> Stores in localStorage('churn_jwt')
   -> Removes from URL
   -> Calls GET /api/auth/me to validate
```

## JWT Structure

**Algorithm:** HS256
**Secret:** `JWT_SECRET` env var
**Expiry:** 7 days

**Payload:**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "name": "User Name",
  "exp": 1234567890
}
```

## Auth Middleware

**HTTP routes:**
- `get_current_user` dependency extracts `Authorization: Bearer <token>` header
- Decodes JWT, returns `{id, email, name}`
- Raises 401 on missing/invalid/expired token

**WebSocket:**
- Token passed as query param: `/api/sessions/{id}/chat?token=<jwt>`
- `get_ws_user(token)` decodes the JWT
- Session ownership verified before accepting connection

## Ownership Check

Every session route verifies that `session.user_id == user.id`. Mismatched ownership returns 404 (not 403) to avoid leaking session IDs.

## Libraries

- `authlib` — OAuth2 flow with Google
- `python-jose` — JWT encoding/decoding
- `starlette.middleware.sessions` — required by authlib for OAuth state

## Config

| Env Var | Usage |
|---------|-------|
| `GOOGLE_CLIENT_ID` | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `JWT_SECRET` | HMAC key for JWT signing |
| `APP_BASE_URL` | Override redirect URL (optional) |
