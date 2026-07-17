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
4. Set `MONGODB_URI` in your `.env` file.
5. Run the API:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend integration

The frontend can call the backend with axios:

```js
axios.post('http://localhost:8000/api/auth/login', data)
axios.get('http://localhost:8000/api/materials')
axios.post('http://localhost:8000/api/materials', materialData)
```

## Docker

```bash
docker compose up --build
```
