# SymbioAI Deployment Guide

This guide reflects the current production-ready setup: React/Vite frontend, FastAPI backend, JWT access tokens, HTTP-only refresh cookies, Google OAuth, and PostgreSQL-compatible deployment.

## Required Production Environment

### Frontend

Set these variables wherever the frontend is built:

```bash
VITE_API_URL=https://YOUR_BACKEND_DOMAIN/api
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com
VITE_BASE_PATH=/
```

Use `VITE_BASE_PATH=/symbio.ai/` only if deploying to GitHub Pages under that repo subpath.

### Backend

Set these variables on Render, Railway, Docker, or your cloud host:

```bash
SECRET_KEY=strong-random-production-secret
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN
GOOGLE_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com
RESEND_API_KEY=YOUR_RESEND_API_KEY
ENVIRONMENT=production
SECURE_COOKIES=true
FRONTEND_URL=https://YOUR_FRONTEND_DOMAIN
RATE_LIMIT_PER_MINUTE=120

# SMTP provider
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=provider-user-or-api-key
SMTP_PASSWORD=provider-password-or-api-secret
SMTP_FROM_EMAIL=no-reply@symbioai.com
SMTP_USE_TLS=true

# S3-compatible object storage
S3_BUCKET=symbioai-uploads
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=provider-access-key
S3_SECRET_ACCESS_KEY=provider-secret-key
S3_ENDPOINT_URL=
S3_PUBLIC_BASE_URL=
```

Notes:
- `SECRET_KEY` must not be `change-me-in-production`; the app refuses to start in production with the default secret.
- `RESEND_API_KEY`, `CORS_ORIGINS`, and `FRONTEND_URL` are required in production. Use the exact HTTPS frontend URL for the last two values.
- `CORS_ORIGINS` accepts a comma-separated list, for example `https://app.example.com,https://www.example.com`.
- In production, refresh cookies are sent as `Secure; HttpOnly; SameSite=None`, which is required for separate frontend/backend domains.
- Realtime messaging uses WebSockets at `wss://YOUR_BACKEND_DOMAIN/api/messaging/ws`.
- Uploads require S3-compatible object storage. The API returns presigned upload URLs and stores only object URLs in the database.
- Email verification and password reset require SMTP credentials.

## Google OAuth Setup

In Google Cloud Console:

1. Create an OAuth 2.0 Web Client.
2. Add authorized JavaScript origins:
   - `https://YOUR_FRONTEND_DOMAIN`
   - `http://localhost:5173` for local development.
3. Add the same client ID to:
   - frontend `VITE_GOOGLE_CLIENT_ID`
   - backend `GOOGLE_CLIENT_ID`
4. Redeploy frontend and backend after setting the variables.

The backend verifies real Google ID tokens. Demo or fake Google auth is intentionally rejected.

## Recommended Deployment: Vercel Frontend + Render Backend

### Backend on Render

1. Create a Render PostgreSQL database.
2. Create a Render Web Service with:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set backend environment variables listed above.
4. Deploy and confirm:

```bash
curl https://YOUR_BACKEND_DOMAIN/health
curl https://YOUR_BACKEND_DOMAIN/ready
```

Expected response contains `"success": true`.

### Frontend on Vercel

1. Import the repository into Vercel.
2. Use the repo root as the project root.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Set frontend environment variables listed above.
6. Deploy.

## Alternative: Railway Backend

The backend includes `backend/railway.toml`.

1. Create a Railway project from the GitHub repository.
2. Use `backend` as the service root if Railway does not auto-detect it.
3. Add PostgreSQL.
4. Set all backend environment variables.
5. Deploy. Railway will run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Alternative: Docker Backend

From the repository root:

```bash
docker build -t symbioai-backend ./backend
docker run --rm -p 8000:8000 \
  -e SECRET_KEY=strong-random-production-secret \
  -e DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE \
  -e CORS_ORIGINS=https://YOUR_FRONTEND_DOMAIN \
  -e GOOGLE_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com \
  -e ENVIRONMENT=production \
  -e SECURE_COOKIES=true \
  symbioai-backend
```

## GitHub Pages Frontend

GitHub Pages works for static hosting, but Vercel is recommended because it handles environment variables and previews more cleanly.

If using GitHub Pages:

1. Enable Pages with GitHub Actions.
2. Set repository variables:
   - `VITE_API_URL=https://YOUR_BACKEND_DOMAIN/api`
   - `VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com`
   - `VITE_BASE_PATH=/symbio.ai/`
3. Ensure Google OAuth authorized JavaScript origins include:
   - `https://anikjain4470.github.io`
4. Ensure backend `CORS_ORIGINS` includes:
   - `https://anikjain4470.github.io`

## Pre-Deploy Verification

Run locally before deploying:

```bash
npm ci
npm run build
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

Optional dependency/security checks:

```bash
npm audit --audit-level=high
python -m pip check
```

## Post-Deploy Smoke Test

After deployment, verify:

1. `GET /health` returns success.
2. `GET /ready` returns success.
3. Frontend loads without console errors.
4. Register creates a new account.
5. Login returns a session and loads `/dashboard`.
6. Refreshing `/dashboard` keeps the user signed in.
7. Logout clears the session.
8. Google Sign-In opens Google consent and completes login.
9. Material listing can be created.
10. Material files upload through object storage and save URLs.
11. AI Match messaging opens a realtime WebSocket-backed thread.
12. Notifications load and unread counts update.
13. 2FA setup shows a QR code and enables with a TOTP code.
14. Marketplace, AI Insights, ESG, Supply Chain, Compliance, and Transactions pages render.

## Troubleshooting

### Google Sign-In does not appear

Check `VITE_GOOGLE_CLIENT_ID` on the frontend build environment, then rebuild the frontend.

### Google Sign-In returns 401

Check that backend `GOOGLE_CLIENT_ID` exactly matches the OAuth client used by the frontend.

### Login works but refresh does not persist

Check:
- backend is HTTPS
- `ENVIRONMENT=production`
- `SECURE_COOKIES=true`
- frontend `VITE_API_URL` points to the HTTPS backend `/api`
- backend `CORS_ORIGINS` exactly includes the frontend origin

### CORS errors

Do not use `*` with credentialed auth. Set exact origins in `CORS_ORIGINS`.

### Database errors on production PostgreSQL

Use the provider connection string in `DATABASE_URL`. The app normalizes `postgres://` and `postgresql://` URLs for the installed psycopg driver.
