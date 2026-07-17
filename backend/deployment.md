# Deployment Guide

## Frontend (Vercel)

1. Build the React app with `npm run build`.
2. Deploy the generated `dist` directory to Vercel.
3. Set the environment variable `VITE_API_URL` to the backend URL.

## Backend (Render / Railway / AWS EC2)

1. Build the Docker image:
   ```bash
   docker build -t symbioai-backend .
   ```
2. Start the stack:
   ```bash
   docker compose up --build -d
   ```
3. Health checks are available at `/health`, `/ready`, and `/metrics`.
4. Enable gzip or brotli compression at the ingress layer and configure CDN caching for static assets.

## Database and storage

- MongoDB Atlas is the target production database.
- AWS S3 compatible storage should be configured through environment variables for uploads.
- Redis should be used for cache invalidation and background task coordination.

## Recovery and availability

- Use automated database backups and periodic restore drills.
- Keep the app stateless and use JWTs so multiple instances can scale safely.
- Add Redis and queue workers for background processing in production.
- Aim for 99.9% uptime readiness by pairing health checks, retries, and load-balancer-style multi-instance deployment.
