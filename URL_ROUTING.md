# URL Routing Guide for Vittcott Deployment

## 🌐 Production URLs (Elastic Beanstalk)

**Base URL**: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com`

### Available Endpoints:

1. **Main Website** (Static Pages)
   - Home: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/`
   - Stocks: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/pages/stocks.html`
   - Portfolio: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/pages/portfolio.html`
   - Mutual Funds: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/pages/mutual-funds.html`

2. **FastAPI Backend** (API Endpoints)
   - Base: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/api/`
   - Stocks: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/api/stocks/live`
   - Portfolio: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/api/portfolio/*`
   - AI: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/api/ai/*`

3. **Streamlit AI Assistant**
   - URL: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/streamlit`
   - WebSocket: `http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com/streamlit/_stcore/stream`

---

## 💻 Local Development URLs

### Running locally (development mode):

1. **FastAPI Backend** (serves static pages too)
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --port 8000
   ```
   - URL: `http://localhost:8000`
   - API: `http://localhost:8000/api/*`

2. **Streamlit App**
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```
   - URL: `http://localhost:8501`

3. **Frontend Development Server** (Optional - for React/Vue development)
   ```bash
   cd frontend
   npm run dev
   ```
   - URL: `http://localhost:3000`
   - **Note**: This is ONLY for frontend development with hot reload

---

## 🔄 How Routing Works

### Production (Elastic Beanstalk):
```
Nginx (Port 8080) 
├── / → FastAPI (Port 8000) - Static pages & frontend
├── /api/* → FastAPI (Port 8000) - API endpoints  
└── /streamlit → Streamlit (Port 8501) - AI Assistant
```

### Configuration Files:
- **Procfile**: Starts both FastAPI and Streamlit processes
- **.ebextensions/02_nginx.config**: Nginx reverse proxy configuration
- **.streamlit/config.toml**: Streamlit base URL path = `/streamlit`

---

## ✅ Fixed Issues:

1. **Port 3000 not accessible**: Frontend dev server is for local development only. Production uses static files served by FastAPI (port 8000).

2. **Port 8501 not accessible directly**: Streamlit is proxied through Nginx at `/streamlit` path.

3. **All HTML links updated**: Changed from `http://localhost:8501` to `/streamlit` for deployment compatibility.

---

## 🚀 Deployment Flow:

1. Push to GitHub → Triggers GitHub Actions
2. GitHub Actions runs tests
3. Deploys to Elastic Beanstalk
4. EB starts both processes (FastAPI + Streamlit)
5. Nginx routes traffic to appropriate service

---

## 📝 Important Notes:

- **Port 3000**: Only exists in local development for frontend hot reload
- **Port 8000**: FastAPI serves both API and static pages in production
- **Port 8501**: Streamlit runs internally, accessed via `/streamlit` externally
- All URLs in production HTML/JS use **relative paths** (`/api/`, `/streamlit`)
