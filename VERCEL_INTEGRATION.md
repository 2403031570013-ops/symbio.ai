# Vercel Frontend + Render Backend Integration Guide

## Current Setup
- **Backend URL**: https://symbio-backend.onrender.com
- **Frontend**: To be deployed on Vercel

## Required Configuration

### 1. Render Backend Environment Variables

Update these in your Render dashboard for the `symbio-backend` service:

**Critical Variables:**
- `DATABASE_URL`: `mongodb+srv://ANIKJAIN4470_DB_USER:Anikjain4470@cluster0.ullffax.mongodb.net/symbioai?retryWrites=true&w=majority&appName=Cluster0`
- `CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-project.vercel.app`)
- `FRONTEND_URL`: Your Vercel frontend URL (e.g., `https://your-project.vercel.app`)

**Optional Variables:**
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth secret
- `RESEND_API_KEY`: For email functionality
- `FACTORY_VERIFICATION_CODE`: Default is "SYMBIO2024" (you can change this)
- SMTP settings for email
- S3 settings for file storage
- `OPENAI_API_KEY`: For AI features

### 2. Vercel Frontend Environment Variables

Set these in your Vercel project settings:

**Required Variables:**
- `VITE_API_URL`: `https://symbio-backend.onrender.com/api`
- `VITE_GOOGLE_CLIENT_ID`: Your Google OAuth client ID (same as backend)
- `VITE_BASE_PATH`: `/` (unless deploying to GitHub Pages subpath)

**Example Vercel Environment Variables:**
```
VITE_API_URL=https://symbio-backend.onrender.com/api
VITE_GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
VITE_BASE_PATH=/
```

**Optional Variables:**
- `VITE_API_PROXY_TARGET`: Not needed for production (only for local development)

## Google OAuth Configuration

Since your frontend and backend are on different domains (Vercel and Render), you need to configure Google OAuth properly:

### Required Steps:

1. **Go to Google Cloud Console** (console.cloud.google.com)
2. **Create a new OAuth 2.0 client ID** (if you don't have one):
   - Go to APIs & Services → Credentials
   - Create credentials → OAuth client ID
   - Application type: Web application
   - Name: SymbioAI Frontend

3. **Add these authorized JavaScript origins:**
   - Your Vercel frontend URL (e.g., `https://your-project.vercel.app`)
   - `http://localhost:5173` (for local development)

4. **Add these authorized redirect URIs:**
   - Your Vercel frontend URL (e.g., `https://your-project.vercel.app`)
   - `http://localhost:5173` (for local development)

5. **Copy the Client ID** and set it in both:
   - Vercel: `VITE_GOOGLE_CLIENT_ID`
   - Render: `GOOGLE_CLIENT_ID`

6. **Copy the Client Secret** and set it in:
   - Render: `GOOGLE_CLIENT_SECRET`

### Important Notes:
- The same Google OAuth client ID must be used on both frontend and backend
- Google login requires both `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to be set in Render
- The backend validates Google tokens using the client ID for security

## Deployment Steps

### Step 1: Update Render Environment Variables
1. Go to Render dashboard
2. Open `symbio-backend` service
3. Go to Environment section
4. Set `CORS_ORIGINS` to your Vercel frontend URL
5. Set `FRONTEND_URL` to your Vercel frontend URL
6. Fix the `DATABASE_URL` if not already corrected
7. Render will automatically redeploy

### Step 2: Deploy Frontend to Vercel
1. Import your repository to Vercel
2. Set root directory to project root
3. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set environment variables:
   - `VITE_API_URL`: `https://symbio-backend.onrender.com/api`
   - `VITE_GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `VITE_BASE_PATH`: `/`
5. Deploy

### Step 3: Verify Integration
After both deployments are complete:

1. **Test backend health**: `https://symbio-backend.onrender.com/health`
2. **Test frontend**: Open your Vercel URL
3. **Test authentication**: Try logging in/registering
4. **Test Google OAuth**: Try Google Sign-In
5. **Test API calls**: Check browser console for CORS errors

**Note for Factory Verification:**
- During registration, you'll need to verify your factory
- The default factory verification code is: `SYMBIO2024`
- You can change this in Render by setting `FACTORY_VERIFICATION_CODE` environment variable

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
- Verify `CORS_ORIGINS` in Render matches your Vercel URL exactly
- Check that the URL includes `https://` and no trailing slashes
- Wait for Render to redeploy after changing environment variables

### Authentication Issues
If Google login shows "not fully configured":
1. **Check Google libraries are installed**: The backend requires `google-auth` package (already in requirements.txt)
2. **Verify environment variables**:
   - Render: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` must be set
   - Vercel: `VITE_GOOGLE_CLIENT_ID` must be set
3. **Check Google Cloud Console**:
   - Your Vercel URL must be in authorized JavaScript origins
   - Your Vercel URL must be in authorized redirect URIs
4. **Wait for Render redeploy** after setting environment variables

If login/refresh doesn't work:
- Verify `FRONTEND_URL` in Render matches your Vercel URL exactly
- Check that `SECURE_COOKIES` is set to `true` in Render
- Ensure both frontend and backend are using HTTPS
- Verify Google OAuth authorized origins include your Vercel URL

### WebSocket Connection Issues
If real-time messaging doesn't work:
- Check that the WebSocket URL is constructed correctly
- Verify the backend `/api/messaging/ws` endpoint is accessible
- Check that CORS allows WebSocket connections

### API Connection Issues
If API calls fail:
- Verify `VITE_API_URL` in Vercel is set to `https://symbio-backend.onrender.com/api`
- Check that the backend is deployed and healthy
- Look at browser network tab for specific error messages
- Check Render logs for backend errors

## Local Development

For local development with the production backend:

1. Create `.env.local` file in frontend root:
   ```
   VITE_API_URL=https://symbio-backend.onrender.com/api
   VITE_GOOGLE_CLIENT_ID=your-google-client-id
   VITE_BASE_PATH=/
   ```

2. Run local development server:
   ```bash
   npm run dev
   ```

3. Your local frontend will connect to the production backend

## Security Notes

- Never commit sensitive environment variables to git
- Use different Google OAuth clients for development and production
- Keep your MongoDB credentials secure
- Enable HTTPS on both frontend and backend
- Use secure cookies in production (already configured in render.yaml)