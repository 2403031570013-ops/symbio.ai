# Deployment

## Render Backend
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Vercel Frontend
- Root directory: repository root
- Build command: `npm run build`
- Output directory: `dist`
- Environment: set `VITE_API_URL` to the backend `/api` URL

## Required Environment Variables
- `DATABASE_URL` or `MONGODB_URI`
- `SECRET_KEY`
- `JWT_REFRESH_SECRET`
- `FRONTEND_URL`
- `CORS_ORIGINS`
- `RESEND_API_KEY`
- `ADMIN_DEV_SECRET`
- `DEV_EMAIL_OTP`
- `DEV_MOBILE_OTP`
- `DEV_FACTORY_CODE`

## MongoDB Atlas Setup
- Create an Atlas cluster
- Add a database user
- Allow network access for the deployment IPs
- Set `DATABASE_URL` to the MongoDB connection string

## Admin / Super Admin
- `ADMIN_DEV_SECRET` is for local development only
- Admin and Super Admin accounts are created or seeded in MongoDB
- Do not hardcode admin secrets in the frontend

## Dev OTP Variables
- `DEV_EMAIL_OTP=654321`
- `DEV_MOBILE_OTP=123456`
- `DEV_FACTORY_CODE=123456`

## Post-Deployment Verification
- `/health`
- `/ready`
- Register
- Factory verification
- Email OTP
- Mobile OTP
- Login
- Refresh token
- Admin dashboard
- Marketplace