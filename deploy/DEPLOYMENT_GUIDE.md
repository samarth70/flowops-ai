# 🚀 FlowOps AI: Production Deployment Guide (Zero Cost, No Restarts)

This guide provides setup instructions for deploying **FlowOps AI** using **Cloudflare Pages** for the frontend and high-reliability, heavy-workload container hosting for the backend that **avoids Hugging Face's refresh cycles**.

---

## 1. Frontend: Deploying to Cloudflare Pages (100% Free Forever)

Since you already have a Cloudflare account, **Cloudflare Pages** is the optimal choice:
- **Unlimited bandwidth**, global Anycast edge network.
- Zero cold starts, instant response times.
- Native Git integration with GitHub.

### Step-by-Step Cloudflare Pages Deployment:
1. Push your repository to GitHub.
2. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/) and navigate to **Workers & Pages** $\rightarrow$ **Create Application** $\rightarrow$ **Pages** $\rightarrow$ **Connect to Git**.
3. Select your repository and configure the build settings:
   - **Project name**: `flowops-ai-crm`
   - **Framework preset**: `Vite`
   - **Root directory**: `frontend`
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
4. Under **Environment variables**, add:
   ```env
   VITE_API_URL=https://your-backend-service-url.com
   ```
5. Click **Save and Deploy**. Your frontend will be live on a global `*.pages.dev` domain in under 45 seconds!
   *(SPA routing fallback `/* /index.html 200` is already configured in `frontend/public/_redirects`).*

---

## 2. Backend: Better Hosting Options (Solving the Hugging Face Refresh Issue)

Hugging Face Spaces is notorious for pausing after inactivity and requiring periodic container refreshes that sever live SSE streams and agent sessions. Here are the top 3 superior alternatives for handling heavy Python/Docker agentic workloads:

---

### 🏆 Top Choice: Google Cloud Run (Free Tier)
Google Cloud Run is the industry gold standard for containerized AI backends:
* **2,000,000 requests per month 100% FREE**
* **360,000 vCPU-seconds and 180,000 GiB-seconds free every month**
* **Handles heavy container images up to 32GB RAM**
* **Near-instant wake-up (~200ms)** with full support for Server-Sent Events (SSE) streaming.
* **No random restarts**: Only scales down when completely idle, and wakes immediately upon request.

#### Deploying to Cloud Run:
Using Google Cloud SDK (already installed in your environment):
```bash
cd backend
gcloud run deploy flowops-backend \
  --source . \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars="DEFAULT_LLM_PROVIDER=groq,GROQ_MODEL=llama-3.3-70b-versatile"
```

---

### Option B: Koyeb Free Tier (1-Hour Idle Timeout)
If you prefer a simple PaaS with a longer idle window:
* **1-Hour Idle Timeout**: Only enters sleep mode after 60 minutes of zero traffic (compared to 15 mins on Render).
* **2GB SSD + 512MB RAM free instance**.
* Connects directly to GitHub and builds your `Dockerfile` automatically.

#### Deploying on Koyeb:
1. Create a free account at [koyeb.com](https://www.koyeb.com/).
2. Click **Create App** $\rightarrow$ **GitHub**.
3. Select your repo, set the root directory to `backend`, and select **Dockerfile**.
4. Add your environment variables (`GROQ_API_KEY`, etc.) and deploy.

---

### Option C: Oracle Cloud Always Free (24/7 Always-On, NEVER Sleeps)
If you require a completely uninterrupted, 24/7 live server:
* **4 Arm Ampere Cores + 24 GB RAM + 200 GB NVMe Storage** 100% Free Forever.
* True Linux VM with Docker daemon.
* Zero sleep, zero cold start, unlimited run time.

---

## 3. Local Development Quick Reference

```powershell
# Backend (FastAPI + Reflexion Critic Loop)
conda activate agenticAi
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Frontend (React + Vite)
cd frontend
npm run dev
```
