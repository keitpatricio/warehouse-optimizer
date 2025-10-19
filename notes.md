# AI-Powered Warehouse Optimization Project

## 1. What to Classify (Inputs to Operations Decisions)

### SKU-level
- **Velocity class (A/B/C/D)** → by predicted pick frequency.
- **Demand variability class (X/Y/Z)** → stable vs erratic demand.
- **Size/handling class (S/M/L; fragile/hazmat/temp)** → storage & aisle/level constraints.
- **Stockout risk (High/Med/Low)** → drives safety stock & service levels.

### Order-level
- **Order urgency class (expedite vs standard)** → wave/wave-less scheduling, put to light/voice priority.
- **Order similarity cluster (which SKUs tend to co-occur)** → batch picking & zone routing.

### Vendor-level
- **Reliability class (on-time vs late-prone)** → lead-time buffers, reorder triggers.

---

## 2. How Those Classes Drive Optimization Knobs

### Slotting / Layout (where to place SKUs)
- Put A-fast movers in golden zones (closest to dock, mid-level shelves).
- Keep Z-high variability near excess capacity or flexible zones.
- Separate fragile/hazmat to compliant areas via class constraints.
- Co-locate co-purchased clusters to shorten multi-line orders.

### Inventory Policies (how much to stock)
- Map risk class → service level (e.g., High risk → 99% service; Low → 95%).
- Map class → safety stock (σ × zα by class).
- Map class → reorder cycle (A/X frequent, B/Y moderate, C/Z infrequent).

### Picking & Scheduling
- Use order classes to design waves (fast lanes for urgent orders).
- Batch by similarity cluster to minimize travel.
- Assign picker skill/equipment based on handling class.

---

## 3. Practical ML → OR Pipeline

### Step A — Data & EDA
- Build features: daily picks, inter-arrival variability (CV), seasonality flags, cube/weight, co-pick matrices, vendor lead-time stats.
- Create labels:
  - Velocity class: top 20% = A, next 30% = B, etc.
  - Variability class: X/Y/Z from CV thresholds.
  - Stockout risk: past stockouts or simulated label from service failure.

### Step B — Classification Models (DeepLearning.AI Alignment)
- Tabular NN (Keras) for multi-label classification (Velocity, Variability, Risk).
- Loss: weighted cross-entropy (imbalances are common).
- Baselines: logistic/XGBoost for comparison.

### Step C — Optimization Models Driven by Predicted Classes
**Slotting MILP (class-based storage):**

Decision x_{i,l} = 1 if SKU i assigned to location l  
Minimize total travel time: ∑ demand_i * distance(l,dock) * x_{i,l}  
Subject to:  
- ∑_l x_{i,l} = 1  
- ∑_i size_i * x_{i,l} ≤ cap_l  
- Class zones: If class_i = A then x_{i,l} = 0 for locations outside golden zones  
- Handling constraints: fragile/hazmat location sets

**Safety Stock / Reorder:**

Map RiskClass → zα  
SS = zα * σ_L  
ROP = μ_L + SS

**Batch Picking / Waves:**

Build order similarity graph (from classification/cluster tags) and solve a set partitioning or VRP-lite problem to minimize travel.

### Step D — Simulation / Evaluation
- Discrete-event or Monte Carlo simulation.
- Measure KPI improvements: pick path, order cycle time, % SLA compliance, dock congestion.
- Visualize improvements in Streamlit.

---

## 4. Streamlit App Blueprint

### Sidebar
- Upload transactions/inventory CSV
- Train/Load classifier (Keras)
- Choose optimization: Slotting | Replenishment | Picking
- Configure constraints (zone sizes, aisle/shelf capacity, service levels)

### Tabs
1. **EDA:** demand histograms, ABC/XYZ scatter, co-pick heatmap  
2. **Classification:** metrics (ROC/PR), confusion matrix, SHAP bars  
3. **Optimization:** warehouse heatmap, inventory policy table, picking plan  
4. **Impact:** KPI deltas (distance, time, stockouts)

---

## 5. Minimal Tech Stack
- **ML:** `tensorflow`, `keras`, `scikit-learn`, `pandas`, `shap`
- **OR:** `pulp` or `ortools` (MILP), `networkx` for clustering
- **Viz/App:** `streamlit`, `plotly`
- *(Optional)* `simpy` for discrete-event simulation

---

## 6. Datasets
- **SAP-style / Vendor datasets (Kaggle):** vendor reliability, lead-time volatility → risk class and ROP.
- **Retail/Grocery sales (100k+):** compute pick frequency & variability → ABC/XYZ classes for slotting.
- **No location data?** Simulate a warehouse grid (aisle/shelf/bin) and enforce class-based zones.

---

## 7. Linking SAP Tables for Analysis

Below are the key SAP-style tables to download and how they connect logically.

### Core Tables
| Module | Table | Description | Join Key(s) |
|---------|--------|-------------|-------------|
| Sales | VBAK | Sales Document Header | `VBELN` (links to VBAP) |
| Sales | VBAP | Sales Document Item | `VBELN`, `MATNR`, `WERKS` |
| Materials | MARA | Material Master | `MATNR` |
| Inventory | MARD | Storage Location Data | `MATNR`, `WERKS`, `LGORT` |
| Movements | MSEG | Material Document Line Items | `MATNR`, `WERKS`, `LGORT` |
| Procurement | EKKO | Purchase Order Header | `EBELN` |
| Procurement | EKPO | Purchase Order Item | `EBELN`, `EBELP`, `MATNR`, `WERKS` |
| Procurement | EKBE | Purchase Order History | `EBELN`, `EBELP` |
| Vendor | LFA1 | Vendor Master | `LIFNR` |
| Reference | T001W | Plant/Warehouse Master | `WERKS` |

### Entity Relationships

**Sales & Distribution Chain:**  
`VBAK` → `VBAP` (via `VBELN`) → `MARA` (via `MATNR`) → `MSEG` (via `MATNR`, `WERKS`) → `MARD` (via `MATNR`, `WERKS`, `LGORT`) → `T001W` (via `WERKS`)

**Procurement Chain:**  
`EKKO` → `EKPO` (via `EBELN`) → `EKBE` (via `EBELN`, `EBELP`) → `LFA1` (via `LIFNR`) → `MARA` (via `MATNR`)

### Combined Flow (ER Overview)

```
CUSTOMER ORDER
  └── VBAK (Sales Header)
        └── VBAP (Sales Item)
              ├── MARA (Material Master)
              ├── MSEG (Movements → demand & variability)
              └── MARD (Stock Levels)
                    └── T001W (Warehouse/Plant)
PURCHASE ORDER
  └── EKKO (PO Header)
        └── EKPO (PO Items)
              ├── MARA (Materials)
              ├── LFA1 (Vendors)
              ├── EKBE (PO History)
              └── MSEG (Goods Receipt)
```

---

## 8. LinkedIn Story
> “We trained a classifier to predict SKU velocity & variability classes.
> Those classes fed a slotting optimization (MILP) and replenishment policy.
> Result: −32% avg pick distance, −18% late lines, +2–4 pts service level at same inventory.”

---

## 9. Starter Tasks This Week
- **Label engineering:** compute velocity (picks/day) & CV → ABC/XYZ labels.  
- **Classifier:** build 3–5 layer dense net (ReLU+dropout), multi-output (velocity, variability).  
- **Slotting prototype:** define golden, silver, bulk zones; run small MILP with class constraints.  
- **Streamlit skeleton:** tabs for EDA → Classification → Optimization → Impact.

### 10. Link to data set
Link to data set: 
https://www.kaggle.com/datasets/mustafakeser4/sap-dataset-bigquery-dataset