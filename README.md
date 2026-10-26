# BioLoop Gujarat (Village-Level Decision Support)

**BioLoop Gujarat** is a deterministic, rules-based decision-support prototype for agricultural biomass utilization, logistics catchment, and transparent pathway evaluation across the state of Gujarat.

It evaluates agricultural residues and agro-industrial by-products against practical utilization pathways (briquetting, pelleting, biochar, activated carbon, and composting) using engineering compatibility rules, transparent multi-factor weighting, straight-line Haversine proximity calculations with rural transit time estimates, and explicit confidence scoring.

> **Honesty & UX Policy:**  
> - **Zero AI/LLM in the scoring pipeline:** Every recommendation is purely deterministic, transparent, and auditable.
> - **Not a Guaranteed Transaction:** A recommendation is never presented as an automated or guaranteed commercial agreement.
> - **Village-Level Granularity:** Coordinates represent approximate village/taluka centroids (`coord_precision: "approximate"`). Verify against Survey of India, Census, or ISRO Bhuvan before field deployment.
> - **Seeded Data Transparency:** All facilities and baseline technical parameters are strictly illustrative demo data (`record_status: "demo"`).

---

## Technology Stack

- **Backend:** Python 3.14+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (SQLite with portable schema), Pytest, Uvicorn
- **Frontend:** React 19, Vite, Leaflet + React-Leaflet, Recharts
- **Styling:** Plain CSS with CSS variables (`tokens.css`, `app.css`), full-bleed `100dvh` app shell, humanist typography (Fraunces & IBM Plex Sans), restrained palette (Forest Green, Cream, Warm Paper, Terracotta, Ochre, Ink, Sage), and smooth 60fps motion transitions with `prefers-reduced-motion` compliance. **Strictly no purple, no glassmorphism, no gradient cards, and no generic marketing boilerplate.**

---

## Directory Structure

```text
geo tech/
├── backend/
│   ├── config/
│   │   └── weights.json          # Default scoring weights (summing to 1.0)
│   ├── services/
│   │   ├── engine.py             # Rule-based eligibility filter, factor scoring, explanations
│   │   └── geo.py                # Haversine distance & rural transit speed calculations
│   ├── tests/
│   │   └── test_engine.py        # Pytest test suite with 5 scenario tests
│   ├── db.py                     # SQLAlchemy database configuration
│   ├── main.py                   # FastAPI REST endpoints
│   ├── models.py                 # SQLAlchemy declarative models (districts, villages, offtakers, hubs, farmer groups)
│   ├── schemas.py                # Pydantic v2 schemas
│   ├── seed.py                   # Idempotent DB seeder (28 villages, 14 offtakers, 7 hubs, 12 farmer groups)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.js         # API integration
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Editorial nav and demo disclosures
│   │   │   ├── BiomassInputForm.jsx # View 1: Input form with district > village selectors
│   │   │   ├── PathwayList.jsx   # View 2: Ranked pathways with staggered animation
│   │   │   ├── FactorBreakdown.jsx # View 3: 5-factor breakdown & missing info
│   │   │   ├── OfftakerMap.jsx   # View 4: Full-bleed Leaflet map with collapsible facility drawer
│   │   │   ├── CompareTable.jsx  # View 5: Practical constraints & Recharts
│   │   │   └── WeightsDrawer.jsx # Live weights adjustment drawer
│   │   ├── styles/
│   │   │   ├── tokens.css        # Strict color, typographic tokens & motion system
│   │   │   └── app.css           # Full-screen 100dvh document-like layout
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Quick Start & Setup

### 1. Backend Server Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment and activate
py -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Seed the SQLite database with curated demo records (28 villages, offtakers, hubs, farmer groups)
python seed.py

# Run the test suite
pytest -v tests/test_engine.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000 --host 127.0.0.1
```
The backend API documentation is available at `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Development Server Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start the Vite development server
npm run dev -- --host 127.0.0.1 --port 5173
```
Open your browser at `http://127.0.0.1:5173`.

---

## Tested Manual Scenarios

The test suite (`backend/tests/test_engine.py`) explicitly validates the following 5 field scenarios:

1. **Scenario 1 (Groundnut Shells / Talaja [Bhavnagar] / 120 t/month, 11% moisture):**
   - Ranks **Biomass Briquetting** as #1 (91.3/100) due to near-zero haulage (~1.2 km, ~5 mins transit) to `Demo Briquette Unit, near Talaja`.
   - Lists 4 offtakers, 2 hubs, and 5 farmer groups within the 100 km catchment radius.
2. **Scenario 2 (Cotton Stalks / Limbdi [Surendranagar] with High Moisture - 48%):**
   - Briquetting and pelleting are disqualified by the hard-rule eligibility filter due to moisture exceeding tolerance by >25%. Aerobic composting remains eligible (tolerance up to 55%).
3. **Scenario 3 (Small Scale Volume - 5 t/month):**
   - All commercial pathways are flagged as ineligible due to falling below minimum viable monthly operational scale (minimum 25–40 t/month).
4. **Scenario 4 (Omitted Moisture Field):**
   - Moisture content is omitted. The engine automatically flags moisture in `missing_info`, marks Processing Requirements as `"Requires verification"`, and calculates data confidence as `"Moderate"`.
5. **Scenario 5 (Tight Catchment Radius - Village with No Facilities in 10 km):**
   - Anjar with a tight 10 km radius: returns cleanly with a helpful empty state in the facilities drawer without throwing errors or crashing.

---

## Known Technical Limitations

1. **Approximate Village Centroids:**
   - Coordinates reflect indicative taluka/village headquarters centroids (3 decimals). Field survey or cadastral parcel verification (e.g. Gujarat Revenue Department / AnyRoR / Bhuvan) is required before planning physical collection points.
2. **Haversine Distance & Transit Speed Estimates:**
   - Proximities are straight-line great-circle distances. Transit times incorporate an indicative 25% road circuity factor at an assumed 32 km/h average speed for tractor-trolleys and rural trucks. Monsoon road conditions, railway crossings, and ghat sections will affect actual haulage times.
3. **Demo Facilities & Capacity Values:**
   - All off-takers, aggregation depots, and farmer groups are generic illustrative demo records (`record_status: "demo"`). Technical capacity thresholds and moisture tolerances must be verified against specific plant technical datasheets.
4. **Market Price Volatility:**
   - The tool does not predict volatile seasonal spot prices or biomass auction rates, evaluating purely engineering suitability and logistical viability.
