# Market Price & Crop Planning Helper 🌱

An intelligent agricultural decision-support system that recommends crops by balancing three core goals:
1. **Agronomic suitability:** Evaluates farm soil, season, water availability, temperature, and seasonal rainfall against research benchmarks (ICAR / ANGRAU).
2. **Low investment / budget compatibility:** Constrains and evaluates recommendations based on the farmer's stated investment budget.
3. **Good expected profit & ROI:** Calculates deterministic net profit, ROI, break-even prices, and 3-tier profit scenarios (conservative, expected, optimistic) grounded in official AGMARKNET mandi prices without inventing values.

---

## 🏛 System Architecture & Technology Stack

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    React Frontend (Vite)                    │
   │  Farm inputs: Location, Soil, Water, Season, Area, Budget   │
   │  Dashboard: Best Crop Card + Top 3 Comparison Table + Scenarios│
   └──────────────────────────────┬──────────────────────────────┘
                                  │ HTTP POST /api/plan
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                   FastAPI Backend Service                   │
   │   • Input validation (land area > 0, budget bounds, types)  │
   │   • LangGraph Multi-Agent Agriculture Graph Orchestration   │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
┌──────────────┐         ┌─────────────────┐        ┌──────────────────┐
│  Open-Meteo  │         │    AGMARKNET    │        │  FAISS / RAG     │
│  Live & 3-Yr │         │ data.gov.in API │        │ Sentence-Transf. │
│ Historical   │         │ + Local Cache   │        │ ICAR & ANGRAU    │
│ Weather API  │         │ Real Mandi Data │        │ Pulses/Crop Docs │
└──────────────┘         └─────────────────┘        └──────────────────┘
      │                           │                           │
      └───────────────────────────┼───────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Candidate Crop Agronomic Evaluation             │
   │  • 5-Factor Weighted Suitability Engine:                   │
   │    - Soil (25%, Essential hard constraint)                 │
   │    - Season (15%, Essential hard constraint)               │
   │    - Water (20%, Essential/penalty matching)               │
   │    - Temperature (20%, Gaussian/continuous range scoring)  │
   │    - Rainfall (20%, 3-yr climate history range scoring)    │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │         Deterministic Financial & Affordability Engine      │
   │  • Total Cost = cost_per_acre × land_area                   │
   │  • Expected Yield = yield_per_acre × land_area              │
   │  • Revenue = expected_yield × expected_price                │
   │  • Net Profit = Revenue − Total Cost                        │
   │  • ROI (%) = (Net Profit / Total Cost) × 100                │
   │  • Break-even Price = Total Cost / Expected Yield           │
   │  • Scenarios: Conservative (min price), Expected, Optimistic│
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │           Recommendation Ranking Engine (7 Components)      │
   │  Strict Hierarchy:                                          │
   │    1. Eligible & Within-Budget crops always rank first      │
   │    2. Over-budget or marginal crops rank lower              │
   │    3. Ineligible crops (soil/season violated) excluded      │
   │  Composite Score Weights:                                   │
   │    Suitability (30%) + Affordability (25%) + Profit (15%)   │
   │    + ROI (10%) + Market Outlook (10%) + Stability (5%)      │
   │    + Risk Confidence (5%)                                   │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Groq LLM Explanation Generator                 │
   │  Synthesizes natural language advisory grounded in facts,   │
   │  citing agricultural sources and clarifying assumptions.    │
   └─────────────────────────────────────────────────────────────┘
```

---

## 🌾 Supported Crops & Agricultural Data Sources

All agronomic thresholds, yields, and cultivation costs are grounded in official Indian agricultural research publications (no fabricated values):

| Crop Key | Commodity Name | Compatible Soils | Seasons | Water Needs | Duration (Days) | Benchmark Yield | Cost/Acre | Primary Data Source |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **tomato** | Tomato | Red, Loamy, Alluvial | Kharif, Rabi, Zaid | High | 90–120 | 18,000 kg | ₹45,000 | ICAR-IIHR & AP Dept. of Horticulture |
| **chilli** | Chilli Red | Red, Loamy, Black, Alluvial | Kharif, Rabi, Zaid | Medium | 150–180 | 2,500 kg | ₹35,000 | ANGRAU & Spices Board of India |
| **groundnut** | Groundnut | Red, Sandy, Loamy, Alluvial | Kharif, Rabi, Zaid | Medium | 90–120 | 1,200 kg | ₹28,000 | ICAR-DGR & ANGRAU Rayalaseema |
| **paddy** | Paddy (Dhan) | Clay, Loamy, Alluvial | Kharif, Rabi | High | 110–145 | 2,200 kg | ₹30,000 | ICAR-NRRI & Directorate of Rice Development |
| **green_gram**| Moong | Red, Loamy, Sandy, Alluvial | Kharif, Rabi, Zaid | Low | 60–75 | 500 kg | ₹16,000 | ICAR-IIPR & ANGRAU Pulses Advisory |
| **bengal_gram**| Chickpea | Black, Clay, Loamy | Rabi | Low | 90–110 | 750 kg | ₹18,000 | ICAR-IIPR & PJTSAU Chickpea Manual |
| **black_gram**| Urad Dal | Red, Loamy, Black, Alluvial | Kharif, Rabi | Low | 65–80 | 450 kg | ₹15,000 | ICAR-IIPR & ANGRAU Black Gram Guide |
| **maize** | Maize | Red, Loamy, Black, Alluvial | Kharif, Rabi | Medium | 90–110 | 2,400 kg | ₹24,000 | ICAR-IIMR & ANGRAU Maize Advisory |
| **red_gram** | Pigeon Pea | Red, Loamy, Black, Alluvial | Kharif | Medium | 150–200 | 650 kg | ₹20,000 | ICAR-IIPR & ANGRAU Regional Research |
| **cotton** | Cotton | Black, Alluvial, Loamy, Red | Kharif | Medium | 150–180 | 900 kg | ₹36,000 | ICAR-CICR & ANGRAU Commercial Cotton Guide |

---

## ⚙️ Installation & Environment Configuration

### Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: v18 or higher (with npm)
- **Git**: Installed and configured

### 1. Environment Variables Setup
Copy the example environment file to `.env`:
```powershell
# In project root
Copy-Item .env.example .env

# Or inside backend directory
Copy-Item backend\.env.example backend\.env
```

Configure your API keys in `.env` (or `backend/.env`):
| Variable | Description | Required / Optional |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | Groq API Key for fast LLM inference (`openai/gpt-oss-20b` or `llama-3.3-70b-versatile`) | **Required** for AI advisory generation |
| `DATA_GOV_API_KEY` | Open Government Data (data.gov.in) API key for AGMARKNET real-time prices | **Optional** (falls back to cached official mandi data) |
| `DATA_GOV_RESOURCE_URL` | Mandi Price resource endpoint URL | **Default provided in .env.example** |
| `HF_TOKEN` | Hugging Face token to avoid download rate limits | **Optional** |
| `ALLOWED_ORIGINS` | Comma-separated CORS allowed origins | **Default:** `http://localhost:5173,...` |

### 2. Backend Dependency Installation
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

*(Optional) Rebuild FAISS Vector Index if adding new documents:*
```powershell
python app/rag/build_index.py
```

### 3. Frontend Dependency Installation
```powershell
cd frontend
npm install
```

---

## 🚀 Quick Start on Windows

### Option A: One-Click Execution
Double click **`run_all.bat`** in the repository root. This opens both the backend API and frontend dev server in separate consoles.

### Option B: Manual Startup

**1. Backend (PowerShell)**:
```powershell
cd backend
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
.\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

**2. Frontend (PowerShell)**:
```powershell
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Automated Test Suite & Validation

The project includes unit, integrity, regression, and end-to-end integration test suites.

### 1. Run Comprehensive Test Suite (18 Tests)
Covers agronomic suitability, hard constraint violations, temperature penalties, financial arithmetic, ROI, over-budget filtering, no-eligible-crops edge cases, and input validation:
```powershell
cd backend
.\venv\Scripts\python.exe test_suite_comprehensive.py
```
*Result: 18 passed in 0.001s (OK)*

### 2. Run Financial Integrity & Edge Cases (17 Tests)
```powershell
cd backend
.\venv\Scripts\python.exe -m unittest discover -s app/evaluation -v
```
*Result: 17 passed in 0.002s (OK)*

### 3. Run FastAPI Integration Tests (3 Tests)
Verifies `/health`, 400/422 validation handling, and full LangGraph workflow execution with live Open-Meteo weather and Groq LLM:
```powershell
cd backend
.\venv\Scripts\python.exe test_api_endpoints.py
```
*Result: 3 passed in 22.4s (OK)*

### 4. Run Deterministic Recommendation Test
```powershell
cd backend
.\venv\Scripts\python.exe test_recommendation.py
```
*Result: chilli (77.25%), tomato (75.5%), groundnut (65.62%) ranked deterministically.*

---

## 🔍 Verification Guide via Swagger & Frontend

### Verifying via Swagger (`/docs`)
1. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.
2. Expand `POST /api/plan`.
3. Click **Try it out** and enter the following JSON payload:
```json
{
  "location": "Markapur",
  "soil": "red",
  "water": "high",
  "season": "kharif",
  "land_area": 2.0,
  "budget": 50000.0,
  "farmer_question": "What crop gives good returns with low initial cost?"
}
```
4. Click **Execute**.
5. Observe the response:
   - Notice that high-cost crops (e.g. Tomato costing ₹90,000 for 2 acres) are flagged with `budget_exceeded: true` and are placed below eligible crops that fit within the ₹50,000 budget (e.g. Groundnut or Black Gram).
   - Verify `profit_analysis` includes `scenarios` (conservative, expected, optimistic), `break_even_price`, and `roi_percent`.
   - Verify `crop_suitability` lists essential violations (e.g., paddy marked ineligible on red soil).

### Verifying via the React Frontend
1. Open [http://localhost:5173](http://localhost:5173).
2. Enter your farm details:
   - Location: `Markapur`
   - Soil: `Red Soil`
   - Water: `High (canal/borewell)`
   - Season: `Kharif (Monsoon)`
   - Land Area: `2.0` acres
   - Investment Budget: `50000`
3. Click **Generate Crop Plan**.
4. View the dashboard:
   - **Recommended Crop Card:** Displays recommendation score, suitability badge, total investment, net profit, ROI, and break-even price.
   - **Top 3 Crop Comparison Table:** Compares the best crop against the top 2 alternative crops side-by-side with suitability, investment, profit, and ROI.
   - **Profit Scenarios Card:** Visualizes conservative, expected, and optimistic profits with price assumptions.
   - **Advisories & Knowledge Citations:** Displays ICAR / ANGRAU research sources and risk advisories.

---

## ⚠️ Known Limitations & Missing Data

1. **Regional Scope:** Crop benchmarks (costs, yields, seasons) are optimized for Andhra Pradesh agro-climatic zones (Rayalaseema, Coastal Andhra).
2. **AGMARKNET Real-Time Coverage:** Certain mandis or niche commodities occasionally have missing daily market arrivals. In such cases, the system uses official cached benchmarks and explicitly marks the data freshness as `"cached"` or `"unavailable"` instead of inventing prices.
3. **Weather Forecast Range:** Weather data from Open-Meteo covers current conditions and short-term forecasts (7–14 days), complemented by 3-year historical seasonal rainfall averages for long-term water evaluation.
