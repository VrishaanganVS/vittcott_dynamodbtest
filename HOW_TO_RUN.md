# VittCott - Quick Start Guide

## Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- AWS credentials configured (for DynamoDB)

## Setup Instructions

### 1. Install Dependencies

**Backend (Node.js):**
```powershell
cd backend
npm install
```

**Python Backend & Streamlit:**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `backend/.env` file with:
```
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
USERS_TABLE=Vittcott_Users
JWT_SECRET=your-secret-key-here
FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Create DynamoDB Table (First Time Only)
```powershell
cd backend
npm run create-table
```

## Running the Project

### Option 1: Run Everything at Once (Recommended)
```powershell
# From project root
.\scripts\demo_start.ps1
```
This will:
- Start Node backend on port 3000 (authentication)
- Start Python backend on port 8000 (main app)
- Start Streamlit on port 8501 (AI assistant)
- Open Streamlit in your browser

### Option 2: Run Services Individually

**Terminal 1 - Node Backend (Port 3000):**
```powershell
cd backend
npm start
```

**Terminal 2 - Python Backend (Port 8000):**
```powershell
cd backend
.\.venv\Scripts\activate
cd src
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 - Streamlit (Port 8501):**
```powershell
.\.venv\Scripts\activate
$env:VITTCOTT_BACKEND_URL='http://localhost:8000'
python -m streamlit run streamlit_app.py --server.port 8501
```

## Access the Application

After starting all services:

- **Main Website:** http://localhost:8000 (Python backend serving index.html)
- **Authentication Pages:** http://localhost:3000/pages/login.html or create-account.html
- **AI Assistant (Streamlit):** http://localhost:8501
- **Backend API:** http://localhost:8000/api

## Quick Commands Reference

### Node Backend Commands
```powershell
cd backend

# Start server
npm start

# Sync frontend files
npm run sync-frontend

# Create DynamoDB table
npm run create-table

# Get user by email
npm run get-user
```

### Testing the Flow

1. **Create Account:**
   - Go to http://localhost:3000/pages/create-account.html
   - Fill in details and submit
   - User saved to DynamoDB

2. **Login:**
   - Go to http://localhost:3000/pages/login.html
   - Enter credentials
   - Redirects to index.html with JWT token

3. **Use AI Assistant:**
   - Click "Assistant" button on index.html
   - Or directly visit http://localhost:8501
   - Ask investment questions

## Troubleshooting

### Streamlit Not Starting
```powershell
# Check if streamlit is installed
.\.venv\Scripts\python.exe -m pip list | Select-String streamlit

# Install if missing
.\.venv\Scripts\python.exe -m pip install streamlit
```

### Static Files Not Loading
```powershell
# Sync frontend to backend
cd backend
npm run sync-frontend
```

### DynamoDB Connection Issues
- Verify AWS credentials in `.env`
- Check AWS region is `ap-south-1`
- Ensure table exists: `npm run create-table`

### Port Already in Use
```powershell
# Find process using port (example: 8000)
netstat -ano | Select-String "8000"

# Kill process by PID
Stop-Process -Id <PID> -Force
```

## Project Structure

```
vittcott_dynamodbtest/
├── backend/
│   ├── server.js              # Node.js auth backend (port 3000)
│   ├── src/
│   │   └── main.py           # Python FastAPI backend (port 8000)
│   └── .venv/                # Python virtual environment
├── frontend/
│   └── public/               # Frontend source files
├── streamlit_app.py          # Streamlit AI assistant
└── scripts/
    └── demo_start.ps1        # Automated startup script
```

## URLs Summary

| Service | URL | Purpose |
|---------|-----|---------|
| Python Backend | http://localhost:8000 | Main API & serves index.html |
| Node Backend | http://localhost:3000 | Authentication (login/signup) |
| Streamlit | http://localhost:8501 | AI Investment Assistant |
| Index Page | http://localhost:8000 | Landing page |
| Login | http://localhost:3000/pages/login.html | User login |
| Signup | http://localhost:3000/pages/create-account.html | Create account |
| Stocks | http://localhost:8000/pages/stocks.html | Stocks listing |
| Mutual Funds | http://localhost:8000/pages/mutual-funds.html | Mutual funds listing |

## Notes

- **Frontend Files:** Synced to both backends via `npm run sync-frontend`
- **Authentication:** JWT tokens stored in localStorage
- **Auth Pages:** Served from Node backend (port 3000)
- **Other Pages:** Served from Python backend (port 8000)
- **Database:** AWS DynamoDB table "Vittcott_Users"


# Make sure .env exists (copy from .env.example if needed)
Copy-Item .env.example .env

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access your app:
# - Node Backend: http://localhost:3000
# - Python Backend: http://localhost:8000
# - Streamlit: http://localhost:8501