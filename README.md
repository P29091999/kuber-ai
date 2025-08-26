## Kuber AI – Digital Gold Assistant

### Overview
A consolidated AI-powered digital gold investment assistant with integrated chat interface and gold purchase functionality.

### Features
- AI-powered chatbot supporting English and Hindi
- User authentication (signup/login)
- Digital gold purchase system
- Real-time gold price tracking
- User portfolio management

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

2) Start the application:
```bash
.\.venv\Scripts\python main.py
```

3) Open `index.html` in your browser.

### Environment Variables
- `MONGO_URI`: MongoDB connection string (required for database functionality)
- `OPENAI_API_KEY`: OpenAI API key (optional) for richer AI responses

### MongoDB Atlas
1) Create free cluster at `https://www.mongodb.com/atlas`.
2) Create DB user and network access (0.0.0.0/0 or your IP).
3) Get connection string, e.g. `mongodb+srv://USER+PASS@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`.
4) Set `MONGO_URI` to this string in your `.env` file.

### Deployment (Render)
- Repo must contain `requirements.txt`, `render.yaml`.
- Connect repo to Render and click Deploy.
- Set environment variables in Render dashboard:
  - `MONGO_URI`: Your MongoDB connection string
  - `OPENAI_API_KEY`: Your OpenAI API key (optional)

### Notes
- Hindi is supported for queries and responses.
- The application serves both the API endpoints and the web interface from a single Flask app.
- **Security**: Never commit API keys or database credentials to version control.
