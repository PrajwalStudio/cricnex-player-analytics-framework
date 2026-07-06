# CricNex Project Deployment Context

## Overview
CricNex is a full-stack machine learning application for IPL player performance prediction. 
It consists of a Python/Flask backend providing a REST API, and a React frontend dashboard.

## Tech Stack
- **Backend:** Python 3.10, Flask, Gunicorn (Production server)
- **Frontend:** React 18, React Router, Axios, Recharts
- **Database:** MongoDB (using PyMongo)
- **Deployment Targets:** Render (Backend) and Vercel (Frontend)

## File Structure (Deployment Focus)
```text
CRICNEX/
├── src/
│   ├── backend.py          # Flask REST API endpoints
│   ├── wsgi.py             # Gunicorn entry point for production
│   └── ...                 # ML models and helper scripts
├── frontend/
│   ├── package.json        # Frontend dependencies and build scripts
│   └── ...                 # React components and pages
├── requirements.txt        # Backend dependencies (Pandas, Flask, XGBoost, etc.)
├── render.yaml             # Render infrastructure-as-code configuration
└── vercel.json             # Vercel routing configuration
```

## Current Configuration Status
The project is **already 100% configured for deployment**. No new code, scripts, or configuration files need to be generated.
1. **`render.yaml`**: Pre-configured as a Blueprint. It will install `requirements.txt` and automatically run `gunicorn --chdir src wsgi:app --bind 0.0.0.0:$PORT`.
2. **`vercel.json`**: Pre-configured to build the React frontend and handle SPA routing (rewriting all paths to `index.html`).
3. **Database**: A MongoDB Atlas connection string is required for the backend. The user already possesses this string.

## Instructions for AI Assistant (Deployment Execution)
When assisting the user with deployment, guide them through these specific steps. Do not instruct them to generate new deployment files, as everything is already present in the repository.

1. **Step 1 (Source Control):** Ensure the user has pushed this entire repository to their personal GitHub account. Both Render and Vercel will deploy directly from this GitHub repo.
2. **Step 2 (Backend to Render):** 
   - Guide the user to log into Render.com.
   - Instruct them to create a new **Blueprint** and connect their GitHub repository.
   - Render will automatically read `render.yaml`.
   - Instruct the user to provide their MongoDB URI (`mongodb+srv://prajwalpoojary1712_db_user:LOqphSWFGvbetfTR@cluster0.je1solq.mongodb.net/?appName=Cluster0`) for the `MONGODB_URI` environment variable when prompted.
   - Wait for the deployment to finish and copy the live Render backend URL.
3. **Step 3 (Frontend to Vercel):** 
   - Guide the user to log into Vercel.com.
   - Instruct them to import the GitHub repository.
   - Crucially, remind them to add a new Environment Variable named `REACT_APP_API_URL` and set its value to the backend URL they just got from Render (appending `/api` to it).
   - Click Deploy.
