# Backend deployment for GitHub Pages frontend

GitHub Pages is static hosting. It can’t run Python/FastAPI. Host the backend elsewhere and point the frontend to it using the VITE_PUBLIC_API_URL build-time variable.

## 1) Quick deploy with Render (Docker)

Prereqs: GitHub account, Render account.

1. In Render, create a new Web Service from this repo, selecting Docker.
2. Expose port 8000.
3. If Render asks for a start command, use:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. Optional env vars:

   - ALLOW_ORIGINS=<https://YOUR-USERNAME.github.io>
   - DATABASE_URL=postgresql://... (or keep SQLite)

5. Deploy and note the public URL (for example, <https://sifu-backend.onrender.com>).

Then set the frontend to use it:

- In GitHub → Settings → Secrets and variables → Actions → New repository secret
   - Name: VITE_PUBLIC_API_URL
   - Value: <https://sifu-backend.onrender.com/api>
- Push any commit (or re-run the Pages workflow).

## 2) Self-host with Docker Compose on a VPS

1. Provision a small VM with Docker/Docker Compose.
2. Copy this repo and run:
   docker-compose up -d
3. Put Nginx/Caddy in front with TLS and proxy /api to the backend (port 8000).
4. Ensure CORS allows <https://YOUR-USERNAME.github.io>.

Set VITE_PUBLIC_API_URL to your public backend base with /api (for example, <https://api.example.com/api>), then redeploy Pages.

## 3) Temporary testing via tunnel (ngrok/Cloudflare)

1. Run backend locally on 8000.
2. Start a tunnel (ngrok http 8000).
3. Set VITE_PUBLIC_API_URL to the tunnel URL with /api and redeploy.

---

Notes

- The frontend reads VITE_PUBLIC_API_URL at build time. Without it, it calls /sifu/api (works only if you have a gateway serving that path).
- constants.py CORS defaults are permissive; adjust ALLOW_ORIGINS for production.
