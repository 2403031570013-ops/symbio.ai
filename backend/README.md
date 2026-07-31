# SymbioAI Backend

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the sample environment file:
   ```bash
   copy .env.example .env
   ```
4. Set `DATABASE_URL` in your `.env` file.
5. Run the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend integration

The frontend can call the backend with axios. Set `VITE_API_URL` to your Render backend URL before deploying to Vercel.

```js
axios.post('http://localhost:8000/api/auth/login', data)
axios.get('http://localhost:8000/api/materials')
axios.post('http://localhost:8000/api/materials', materialData)
```

For local development, use a `.env` file with at least:

```bash
DATABASE_URL=mongodb+srv://...
FRONTEND_URL=http://localhost:5173
```

## Deployment

### Render backend

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required env vars: `DATABASE_URL`, `JWT_SECRET`, `JWT_REFRESH_SECRET`, `FRONTEND_URL`

### Vercel frontend

- Build command: `npm run build`
- Output directory: `dist`
- Required env vars: `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID` if Google login is enabled
- The included `vercel.json` handles React Router refreshes on deployed routes.

## Docker

```bash
docker compose up --build
```
