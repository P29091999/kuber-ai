## Kuber AI – Digital Gold Assistant

### APIs
- API 1 (port 3000): POST `/api/query`
- API 2 (port 3001): POST `/api/purchase-gold`

### Setup
1) Copy `env.example` to `.env` and configure your environment variables:
```bash
cp env.example .env
```

2) Edit `.env` with your actual values:
- `MONGO_URI`: Your MongoDB connection string
- `OPENAI_API_KEY`: Your OpenAI API key (optional)

### Local run
1) Create venv and install:
```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

2) Start API 1:
```bash
.\.venv\Scripts\python yashi\main.py
```

3) Start API 2:
```bash
.\.venv\Scripts\python API2\api2.py
```

4) Open `yashi\index.html` or `bot.html`.

### Environment Variables
- `MONGO_URI`: MongoDB connection string (required for database functionality)
- `OPENAI_API_KEY`: OpenAI API key (optional) for richer AI responses in API 1

### MongoDB Atlas
1) Create free cluster at `https://www.mongodb.com/atlas`.
2) Create DB user and network access (0.0.0.0/0 or your IP).
3) Get connection string, e.g. `mongodb+srv://USER:PASS@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`.
4) Set `MONGO_URI` to this string in your `.env` file.

### Deployment (Render)
- Repo must contain `requirements.txt`, `render.yaml`.
- Connect repo to Render and click Deploy.
- Set env vars per service:
  - `kuber-ai-api1`: `MONGO_URI`, `OPENAI_API_KEY`
  - `kuber-ai-api2`: `MONGO_URI`
- `kuber-ai-bot` serves `bot.html`. Update bot.html to point to deployed API URLs if needed.

### Notes
- Hindi is supported for queries and responses.
- API 2's in-memory fallback is for dev only; use MongoDB for production persistence.
- **Security**: Never commit API keys or database credentials to version control.
