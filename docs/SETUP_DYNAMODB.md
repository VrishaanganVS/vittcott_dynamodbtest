# Setup DynamoDB (local) for development

This project uses DynamoDB to store user accounts. For the simplest, lowest-friction development setup you can run DynamoDB Local (Docker) and create the users table with the provided script.

1) Start DynamoDB Local using Docker (recommended):

```powershell
# run DynamoDB Local on port 8000
docker run -p 8000:8000 amazon/dynamodb-local
```

Or download the DynamoDB Local jar and run it directly (see AWS docs).

2) In the backend folder, install dependencies (if not installed) and create the table:

```powershell
Set-Location -Path "e:\\Vrishaangan\\GitHub\\vittcott_dynamodbtest\\backend"
npm install
# Point DYNAMODB_ENDPOINT at the local instance and create the table
node create_table.js
# or via npm script
npm run create-table
```

3) Set environment variables for the backend. Create a `.env` at the project root or backend root with at least:

```
# .env (example)
DYNAMODB_ENDPOINT=http://localhost:8000
AWS_REGION=ap-south-1
USERS_TABLE=Vittcott_Users
FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173
JWT_SECRET=dev-secret
```

4) Start the backend:

```powershell
npm start
```

5) Open the frontend (serve it or open the pages) and test signup/login. If you serve the frontend from the backend's static directory, use relative paths and CORS isn't needed.

Notes:
- The `create_table.js` script creates a table named `Vittcott_Users` with a primary `pk` attribute and a global secondary index `GSI_Email` on the `email` attribute so login-by-email works.
- For production, use an actual AWS account and remove any dev-only fallbacks in the server code.

Sync frontend into backend and dev convenience scripts
----------------------------------------------------

To avoid CORS and run the entire app from a single origin (recommended), copy the frontend `public` folder into `backend/src/frontend_build` so the backend serves the static files.

You can do this with the included script:

```powershell
Set-Location -Path "e:\\Vrishaangan\\GitHub\\vittcott_dynamodbtest\\backend"
npm run sync-frontend
```

There is also a `dev` script that will sync the frontend and start the backend in one step:

```powershell
npm run dev
```

Auto-create table on server startup
----------------------------------

If you prefer the backend to attempt creating the DynamoDB table when it starts (useful for local development), set the environment variable `AUTO_CREATE_TABLE=true` and ensure `DYNAMODB_ENDPOINT` points to your local DynamoDB (or the runtime can detect `localhost`). Example `.env`:

```
DYNAMODB_ENDPOINT=http://localhost:8000
AWS_REGION=ap-south-1
USERS_TABLE=Vittcott_Users
FRONTEND_ORIGINS=http://localhost:3000
JWT_SECRET=dev-secret
AUTO_CREATE_TABLE=true
```

When the backend starts it will attempt to create the table once and log results. This is guarded — if table creation fails, the server continues to run so you won't be blocked by transient errors.

