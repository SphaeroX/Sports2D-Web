# Sports2D Web

> A modern web interface for **Sports2D** — markerless 2D human pose estimation and biomechanical analysis from video.

[![Vue.js](https://img.shields.io/badge/Vue.js-3-42b883?logo=vue.js)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Local Deployment](#local-deployment)
  - [Option A: With Docker (Recommended)](#option-a-with-docker-recommended)
  - [Option B: Without Docker](#option-b-without-docker)
- [Cloud Deployment](#cloud-deployment)
  - [Deploy to Render](#deploy-to-render)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [License](#license)
- [Citations](#citations)

---

## Overview

**Sports2D Web** is a full-stack SaaS application that provides a user-friendly web interface for the [Sports2D](https://github.com/davidpagnon/Sports2D) biomechanical analysis pipeline. Users can upload videos, trim and segment them, configure analysis parameters, and run markerless 2D pose estimation with optional OpenSim inverse kinematics — all through their browser.

The application tracks anonymous users via `localStorage` so that job history, queue status, and download links persist across sessions.

---

## Features

- **Drag & Drop Video Upload** — Upload videos up to 500 MB / 300 s.
- **Visual Trimming & Segmentation** — Define start/end times and create multiple segments for separate analysis.
- **Standard & Expert Modes** — Simple defaults or full parameter control.
- **Background Job Processing** — Celery workers handle long-running analyses asynchronously.
- **Live Job Status & Queue** — Real-time progress bars, status badges, and a persistent job history.
- **Result Download** — Download processed results as ZIP files.
- **Multi-language UI** — English and German support.
- **Anonymous User Tracking** — Jobs are associated with a browser via `localStorage` UUID.

---

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Vue 3 SPA     │──────▶   FastAPI App    │──────▶   SQLite DB     │
│  (Pinia + i18n) │◀─────│   (Python 3.11)  │◀─────│  (Job Storage)  │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Celery Worker│
                         │  (Redis)     │
                         └──────────────┘
```

| Component | Technology |
|-----------|------------|
| **Frontend** | Vue 3, Vite, Pinia, Vue Router, Vue I18n, Axios |
| **Backend API** | FastAPI, SQLAlchemy, Pydantic |
| **Worker Queue** | Celery + Redis |
| **Database** | SQLite (auto-initialized) |
| **Video Processing** | OpenCV, FFmpeg, RTMLib, OpenSim (via Pose2Sim) |

---

## Local Deployment

### Prerequisites

- [Git](https://git-scm.com/)
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) *(for Option A)*
- [Python 3.11+](https://www.python.org/) and [Node.js 20+](https://nodejs.org/) *(for Option B)*

Clone the repository:

```bash
git clone https://github.com/davidpagnon/Sports2D.git
```

---

### Option A: With Docker (Recommended)

This is the fastest and most reliable way to run the full stack locally.

#### 1. Build and start all services

Make sure you are in the `web` directory before running the commands:

```bash
docker-compose up --build
```

#### 2. Access the application

| Service | URL |
|---------|-----|
| Web Interface | http://localhost:5173 |
| Backend API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/api/health |

#### 3. Stopping the services

```bash
# Stop gracefully
docker-compose down

# Stop and remove all volumes (clears database & uploads)
docker-compose down -v
```

#### 4. Running in detached mode

```bash
docker-compose up -d --build
```

> **Note:** The first build downloads large ML models and may take **10–20 minutes** depending on your connection. Subsequent starts are near-instant.

---

### Option B: Without Docker

Use this if you prefer native development or want to modify code without rebuilding containers.

#### 1. Backend Setup

```bash
# Create a Python virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Initialize the database
python -c "from app.services.storage import init_db; init_db()"

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a **second terminal**, start the Celery worker (make sure the same virtual environment is activated):

```bash
cd backend
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

> The `--pool=solo` flag is recommended for local development to avoid multiprocessing issues with some ML libraries. For production, use `--pool=prefork` or `--pool=gevent`.

#### 2. Frontend Setup

In a **third terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

#### 3. Access the application

| Service | URL |
|---------|-----|
| Web Interface | http://localhost:5173 |
| Backend API Docs | http://localhost:8000/docs |

#### 4. Development tips

- The frontend dev server proxies `/api` and `/previews` requests to the backend automatically (see `vite.config.js`).
- Hot Module Replacement (HMR) is active for both frontend and backend when using `--reload`.

---

## Cloud Deployment

### Deploy to Render

[Render](https://render.com) is a popular platform for hosting Docker-based web services with free and paid tiers.

#### 1. Prerequisites

- A [Render](https://render.com) account
- Your code pushed to a GitHub/GitLab repository

#### 2. Create a Blueprint (Infrastructure as Code)

Render supports `render.yaml` for Blueprint deployments. Create a `render.yaml` in the **repository root**:

```yaml
services:
  - type: web
    name: sports2d-web-frontend
    runtime: static
    buildCommand: cd web/frontend && npm install && npm run build
    staticPublishPath: ./web/frontend/dist
    envVars:
      - key: VITE_API_BASE_URL
        value: https://sports2d-api.onrender.com
    routes:
      - type: rewrite
        source: /.*
        destination: /index.html

  - type: web
    name: sports2d-web-backend
    runtime: docker
    repo: https://github.com/YOUR_USERNAME/YOUR_REPO
    dockerfilePath: ./web/backend/Dockerfile
    dockerContext: ./web/backend
    envVars:
      - key: APP_NAME
        value: Sports2D Web
      - key: MAX_UPLOAD_SIZE_MB
        value: "500"
      - key: MAX_VIDEO_DURATION_SEC
        value: "300"
      - key: AUTO_DELETE_HOURS
        value: "24"
      - key: CELERY_BROKER_URL
        fromService:
          type: redis
          name: sports2d-redis
          property: connectionString
      - key: CELERY_RESULT_BACKEND
        fromService:
          type: redis
          name: sports2d-redis
          property: connectionString

  - type: worker
    name: sports2d-web-worker
    runtime: docker
    repo: https://github.com/YOUR_USERNAME/YOUR_REPO
    dockerfilePath: ./web/backend/Dockerfile
    dockerContext: ./web/backend
    envVars:
      - key: APP_NAME
        value: Sports2D Web
      - key: CELERY_BROKER_URL
        fromService:
          type: redis
          name: sports2d-redis
          property: connectionString
      - key: CELERY_RESULT_BACKEND
        fromService:
          type: redis
          name: sports2d-redis
          property: connectionString
    startCommand: celery -A app.worker.celery_app worker --loglevel=info --pool=prefork --concurrency=2

  - type: redis
    name: sports2d-redis
    plan: starter
    ipAllowList: []
```

> **Important:** Replace `YOUR_USERNAME/YOUR_REPO` with your actual GitHub username and repository name.

#### 3. Adjust CORS for production

Edit `web/backend/app/main.py` and restrict the CORS `allow_origins` to your Render frontend URL before deploying:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sports2d-web-frontend.onrender.com"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Deploy via Dashboard (Alternative)

If you prefer the UI over `render.yaml`:

1. **Redis:** Create a new **Redis** instance on Render.
2. **Web Service (Backend):**
   - Select your repository.
   - Choose **Runtime: Docker**.
   - Set the root directory to `web/backend`.
   - Add the environment variables listed above.
3. **Worker:**
   - Create another service from the same repository.
   - Choose **Runtime: Docker**.
   - Set the start command to: `celery -A app.worker.celery_app worker --loglevel=info --pool=prefork --concurrency=2`.
   - Use the same Redis connection string.
4. **Static Site (Frontend):**
   - Create a **Static Site**.
   - Set the build command to: `cd web/frontend && npm install && npm run build`.
   - Set the publish directory to `web/frontend/dist`.
   - Add an environment variable `VITE_API_BASE_URL` pointing to your backend service URL.

#### 5. Free Tier Limitations

- Render's free web services spin down after **15 minutes of inactivity**. The first request after spin-down may take **30–60 seconds** to wake up.
- Free Redis instances have limited memory (100 MB). For heavy usage, upgrade to a paid plan.
- Video processing is CPU-intensive. For production workloads, use Render's **Standard** or **Pro** instance types.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Sports2D Web` | Application name shown in logs |
| `MAX_UPLOAD_SIZE_MB` | `500` | Maximum uploaded video size in MB |
| `MAX_VIDEO_DURATION_SEC` | `300` | Maximum video duration in seconds |
| `AUTO_DELETE_HOURS` | `24` | Automatically delete job files after N hours |
| `CELERY_BROKER_URL` | — | Redis URL for Celery (e.g., `redis://localhost:6379/0`) |
| `CELERY_RESULT_BACKEND` | — | Redis URL for Celery results |
| `VITE_API_BASE_URL` | `''` | Base URL for frontend API calls (empty = same origin) |

---

## API Endpoints

The backend exposes a REST API documented automatically at `/docs` (Swagger UI) or `/redoc` (ReDoc).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload/` | Upload a video file |
| `POST` | `/api/jobs/process` | Start analysis with segments & parameters |
| `GET` | `/api/jobs/{job_id}/status` | Poll job status and progress |
| `GET` | `/api/jobs/list?user_id=...` | List all jobs for a given user |
| `GET` | `/api/download/{job_id}` | Download results as ZIP |
| `GET` | `/api/health` | Health check |

---

## Development

### Project Structure

```
web/
├── frontend/              # Vue 3 SPA
│   ├── src/
│   │   ├── components/    # Reusable Vue components
│   │   ├── stores/        # Pinia state management
│   │   ├── views/         # Page-level components
│   │   ├── i18n/          # Translation files (en, de)
│   │   └── ...
│   └── Dockerfile
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Business logic & DB models
│   │   ├── worker/        # Celery tasks
│   │   └── main.py
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Running Tests

```bash
# Backend (if tests exist)
cd web/backend
pytest

# Frontend
cd web/frontend
npm run test
```

### Adding a New Language

1. Create a new JSON file in `web/frontend/src/i18n/locales/` (e.g., `fr.json`).
2. Copy the structure from `en.json` and translate the values.
3. Register the locale in `web/frontend/src/i18n/index.js`.

---

## License

This project is licensed under the **BSD-3-Clause** License. See the original [Sports2D repository](https://github.com/davidpagnon/Sports2D) for details.

---

## Citations

If you use Sports2D in your research, please cite:

```bibtex
@article{Pagnon_Sports2D_Compute_2D_2024,
  author = {Pagnon, David and Kim, HunMin},
  doi = {10.21105/joss.06849},
  journal = {Journal of Open Source Software},
  month = sep,
  number = {101},
  pages = {6849},
  title = {{Sports2D: Compute 2D human pose and angles from a video or a webcam}},
  url = {https://joss.theoj.org/papers/10.21105/joss.06849},
  volume = {9},
  year = {2024}
}
```

---

## Acknowledgments

- Built on top of the amazing open-source work by **David Pagnon** and the **[Pose2Sim](https://github.com/perfanalytics/pose2sim)** project.
- Pose estimation powered by **[RTMLib](https://github.com/Tau-J/rtmlib)** and **[MMPose](https://github.com/open-mmlab/mmpose)**.
- Inverse kinematics via **[OpenSim](https://opensim.stanford.edu/)**.
