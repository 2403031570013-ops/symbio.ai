# Deployment Guide - SymbioAI

## Quick Start - Get Your App Live

### Frontend (GitHub Pages) - Ready to Deploy!

**Your frontend will be available at:** https://anikjain4470.github.io/symbio.ai/

**To enable GitHub Pages:**
1. Go to: https://github.com/ANIKJAIN4470/symbio.ai/settings/pages
2. Under "Build and deployment" → "Source", select: **GitHub Actions**
3. Click "Save"
4. The workflow will automatically deploy on next push

**Trigger deployment now:**
```bash
git commit --allow-empty -m "Trigger frontend deployment"
git push origin master
```

### Backend (Simple Option - Render)

**For a quick backend deployment:**

1. Go to [render.com](https://render.com) and sign up (free tier available)
2. Click "New +" → "Web Service"
3. Connect GitHub and select `ANIKJAIN4470/symbio.ai`
4. Configure:
   - **Name**: symbioai-backend
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `DATABASE_URL`: `sqlite:///./symbioai.db` (for development)
   - `SECRET_KEY`: Generate at https://generate-secret.vercel.app/32
   - `CORS_ORIGINS`: `https://anikjain4470.github.io/symbio.ai`
6. Click "Deploy Web Service"

**Your backend URL will be:** `https://symbioai-backend.onrender.com`

### Update Frontend to Use Backend URL

After backend deployment, update the frontend:

1. Go to: https://github.com/ANIKJAIN4470/symbio.ai/settings/pages
2. Add environment variable: `VITE_API_URL` = `https://symbioai-backend.onrender.com`
3. Or update `src/services/api.js`:
```javascript
const api = axios.create({
  baseURL: 'https://symbioai-backend.onrender.com/api',
  withCredentials: true,
});
```

## Alternative: Full GitHub Deployment

### Backend on GitHub Container Registry

The backend Docker image is automatically built and pushed to:
`ghcr.io/ANIKJAIN4470/symbio.ai/symbioai-backend:latest`

You can deploy this to any cloud provider that supports Docker containers.

### Manual Deployment Steps

**Option 1: Railway (Easiest)**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `ANIKJAIN4470/symbio.ai`
4. Railway will auto-detect the configuration
5. Add environment variables as needed

**Option 2: AWS/Azure/GCP**
1. Pull the Docker image: `docker pull ghcr.io/ANIKJAIN4470/symbio.ai/symbioai-backend:latest`
2. Deploy to your preferred cloud provider
3. Configure environment variables

## Final URLs

After completing the steps above:

- **Frontend**: https://anikjain4470.github.io/symbio.ai/
- **Backend**: Your chosen provider URL (e.g., https://symbioai-backend.onrender.com)

## Troubleshooting

**Frontend not loading:**
- Check GitHub Actions tab for deployment status
- Ensure GitHub Pages is enabled with GitHub Actions as source

**Backend connection issues:**
- Verify CORS_ORIGINS includes your frontend URL
- Check backend logs for errors
- Ensure environment variables are set correctly

**Database issues:**
- For development, SQLite works fine
- For production, use PostgreSQL (Render provides free PostgreSQL)
