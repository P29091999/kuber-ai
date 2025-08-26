## Kuber AI – Digital Gold Assistant

### APIs
- API 1 (port 3000): POST `/api/query`
- API 2 (port 3001): POST `/api/purchase-gold`

### Local run
1) Create venv and install:
```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```
2) Start API 1:
```bash
.\.venv\Scripts\python api1.py
```
3) Start API 2:
```bash
.\.venv\Scripts\python API2\api2.py
```
4) Open `bot.html`.

### Environment
- `OPENAI_API_KEY` (optional) for richer responses in API 1.
- `MONGODB_URI` (recommended) for API 2. Without it, API 2 uses in-memory store.

### MongoDB Atlas
1) Create free cluster at `https://www.mongodb.com/atlas`.
2) Create DB user and network access (0.0.0.0/0 or your IP).
3) Get connection string, e.g. `mongodb+srv://USER:PASS@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`.
4) Set `MONGODB_URI` to this string.

### Deployment (Render)
- Repo must contain `requirements.txt`, `render.yaml`.
- Connect repo to Render and click Deploy.
- Set env vars per service:
  - `kuber-ai-api1`: `OPENAI_API_KEY`
  - `kuber-ai-api2`: `MONGODB_URI`
- `kuber-ai-bot` serves `bot.html`. Update bot.html to point to deployed API URLs if needed.

### Notes
- Hindi is supported for queries and responses.
- API 2’s in-memory fallback is for dev only; use MongoDB for production persistence.
