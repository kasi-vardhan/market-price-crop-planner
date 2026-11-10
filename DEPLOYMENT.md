# 🚀 Production Deployment Guide

This guide walks you through deploying the **Market Price & Crop Planning Helper** to live production.

---

## 📋 Required Environment Variables

Before deploying, ensure you have your API keys ready:

| Environment Variable | Required? | Description | Example / Default |
| :--- | :---: | :--- | :--- |
| `GROQ_API_KEY` | **Yes** | Groq API Key for LLM advisory | `gsk_...` |
| `DATA_GOV_API_KEY` | Optional | data.gov.in AGMARKNET live prices | Falls back to cached official mandi data |
| `DATA_GOV_RESOURCE_URL` | Optional | Mandi Price resource endpoint | `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070` |
| `ALLOWED_ORIGINS` | Optional | Permitted CORS origins | `*` (or your frontend URL) |

---

## 🎯 Recommended Deployment Options

Choose the deployment method that best suits your needs:

| Platform | Best For | Cost | RAM | Setup Difficulty |
| :--- | :--- | :---: | :---: | :---: |
| **[Render (All-in-One Docker)](#option-1-render-all-in-one-docker--recommended)** | Simplest unified deploy (Frontend + Backend on 1 URL) | **Free** | 512 MB | ⭐ Easy (1-click blueprint) |
| **[Hugging Face Spaces](#option-2-hugging-face-spaces-16-gb-ram-free)** | Heavy ML/SentenceTransformers performance | **Free** | 16 GB | ⭐ Easy |
| **[Vercel + Render / Railway](#option-3-split-deploy-vercel-frontend--renderrailway-backend)** | Maximum frontend speed & CDN caching | **Free** | N/A + 512MB/8GB | ⭐⭐ Moderate |
| **[Any VPS / Cloud (Docker)](#option-4-self-hosted--vps-docker)** | Full ownership (DigitalOcean, AWS, GCP, etc.) | Pay as you go | Custom | ⭐⭐ Moderate |

---

### Option 1: Render (All-in-One Docker — Recommended)

The repository includes a ready-to-go `Dockerfile` and `render.yaml` blueprint. The FastAPI backend automatically serves the built React frontend from the same service.

#### Step 1: Push your latest changes to GitHub
```powershell
git add .
git commit -m "Configure live deployment for Render, Docker, and Vercel"
git push origin main
```

#### Step 2: Deploy on Render
1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** → **Blueprint** (or **Web Service**).
3. Select your repository: `market-price-crop-planner`.
4. If using Blueprint:
   - Render automatically detects `render.yaml`.
   - Enter your `GROQ_API_KEY` and click **Apply**.
5. If creating a manual **Web Service**:
   - **Environment:** Docker
   - **Docker Command:** leave default (uses Dockerfile CMD)
   - Under **Environment Variables**, add:
     - `GROQ_API_KEY` = your Groq API key
     - `ALLOWED_ORIGINS` = `*`
6. Click **Deploy Web Service**.
7. Once the build finishes, open your live URL (e.g. `https://market-price-crop-planner.onrender.com`).

---

### Option 2: Hugging Face Spaces (16 GB RAM Free)

Because this app utilizes `sentence-transformers`, `faiss-cpu`, and agricultural knowledge vector retrieval, Hugging Face Spaces provides **16 GB RAM for free**, preventing out-of-memory errors on large loads.

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Set:
   - **Space SDK:** `Docker` → `Blank`
   - **Space hardware:** `Free CPU · 16 GB RAM`
   - **Visibility:** `Public`
3. In your Space **Settings** → **Variables and secrets**, add:
   - Secret `GROQ_API_KEY`: your Groq API key
   - Variable `PORT`: `7860`
4. Push your repository to the Hugging Face Git remote:
   ```bash
   git remote add space https://huggingface.co/spaces/<YOUR_USERNAME>/<YOUR_SPACE_NAME>
   git push space main
   ```
5. Your app will automatically build and launch at `https://huggingface.co/spaces/<YOUR_USERNAME>/<YOUR_SPACE_NAME>`.

---

### Option 3: Split Deploy (Vercel Frontend + Render/Railway Backend)

If you prefer hosting the React frontend on Vercel's global CDN and the FastAPI backend on Render or Railway:

#### Part A: Deploy the Backend on Render or Railway
1. Create a new Web Service pointing to `market-price-crop-planner`.
2. Set Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GROQ_API_KEY` = your key
   - `ALLOWED_ORIGINS` = `*` (or your upcoming Vercel URL)
6. Note the backend URL (e.g. `https://crop-planner-api.onrender.com`).

#### Part B: Deploy the Frontend on Vercel
1. Go to [vercel.com](https://vercel.com/) and click **Add New...** → **Project**.
2. Select `market-price-crop-planner`.
3. Set **Root Directory** to `frontend`.
4. Framework Preset: `Vite`.
5. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL` = `https://crop-planner-api.onrender.com` (your backend URL from Part A, no trailing slash).
6. Click **Deploy**. Vercel will build and deploy your React app with instant edge routing.

---

### Option 4: Self-Hosted / VPS (Docker)

To run the container on any Linux/Windows VPS or cloud machine:

```bash
# 1. Build the Docker image
docker build -t crop-planner .

# 2. Run the container
docker run -d \
  -p 8000:8000 \
  -e GROQ_API_KEY="gsk_..." \
  -e ALLOWED_ORIGINS="*" \
  --name crop-planner-app \
  crop-planner

# 3. Check logs
docker logs -f crop-planner-app
```

Visit `http://<your-server-ip>:8000` to interact with the application.

---

## 🔍 Verification & Post-Deployment Checklist

1. **Backend Health Check:**
   - Open `https://<YOUR_APP_URL>/health` in your browser.
   - It should return `{"status": "healthy"}`.
2. **Interactive API Documentation:**
   - Open `https://<YOUR_APP_URL>/docs` to view the Swagger UI.
3. **Frontend Application:**
   - Open `https://<YOUR_APP_URL>/`.
   - Submit a test recommendation:
     - Location: `Markapur`
     - Soil: `Red`
     - Water: `High`
     - Season: `Kharif`
     - Land: `2`
     - Budget: `50000`
   - Verify that the Best Crop Card, Top 3 Comparison Table, and Financial Scenarios load correctly.
