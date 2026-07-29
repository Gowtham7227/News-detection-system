# Render Deployment Fix — Task List

- [x] Analyze project structure and root causes
- [x] Create `render.yaml` (root level)
- [x] Fix `backend/requirements.txt` (remove broken deps)
- [x] Fix `backend/runtime.txt` (verified Render-supported Python version)
- [x] Update `backend/app/core/config.py` (DATABASE_URL env var support)
- [x] Create `frontend/nginx.conf` (SPA routing + API proxy for production)
- [x] Update `frontend/Dockerfile` (add nginx.conf)
- [x] Update `frontend/vite.config.js` (production build config)
- [x] Create `.env.example` at root level with all required vars
- [x] Build verification — run `npm run build` in frontend/ manually to confirm
