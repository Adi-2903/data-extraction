# Methodology

## 1. Data Pipeline

### 1.1 Data Ingestion

```python
# Load multiple CSV files matching patterns
enrolment_df = load_and_combine('dataset/api_data_aadhar_enrolment_*.csv')
demographic_df = load_and_combine('dataset/api_data_aadhar_demographic_*.csv')
biometric_df = load_and_combine('dataset/api_data_aadhar_biometric_*.csv')
```

**Files Processed:**
- 3 enrollment files → 1,006,007 records
- 5 demographic files → 2,071,698 records
- 4 biometric files → 1,861,108 records

### 1.2 Data Cleaning

| Step | Transformation | Rationale |
|------|---------------|-----------|
| Column normalization | Lowercase, strip whitespace | Consistency |
| Missing value handling | Fill numeric with 0 | Prevent calculation errors |
| Date parsing | Convert to datetime | Enable temporal analysis |
| Geographic standardization | Title case state/district | Accurate aggregation |

---

## 2. Analysis Framework

### 15-Phase Analysis Pipeline

| Phase | Technique | Tool |
|-------|-----------|------|
| 1-3 | Domain Deep Dive | pandas, seaborn |
| 4 | Master Cube Integration | pandas merge |
| 5 | Predictive Forecasting | statsmodels (Holt-Winters) |
| 6 | Anomaly Detection | sklearn (Isolation Forest) |
| 7 | District Clustering | sklearn (K-Means) |
| 8 | Cohort Analysis | pandas groupby |
| 9 | Statistical Significance | scipy.stats |
| 10 | Composite Scoring | Custom formulas |
| 11-13 | Visualization | Plotly, matplotlib |
| 14-15 | Policy Synthesis | Custom generators |

---

## 3. Feature Engineering

### Derived Metrics Created

```python
# Saturation Index: Post-enrollment activity level
Saturation_Index = (total_demo + total_bio) / (total_enrol + 1)

# Efficiency Score: Operational efficiency
efficiency_score = total_activity / (total_enrol + total_activity)

# Lifecycle Progression Index (LPI)
LPI = (bio_rate / enrol_rate) × (demo_rate / enrol_rate)

# Health Score: Composite district metric
Health_Score = 0.4 × Compliance + 0.3 × Activity + 0.3 × Quality
```

---

## 4. Statistical Methods

### 4.1 Time Series Forecasting

**Algorithm:** Holt-Winters Exponential Smoothing

```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model = ExponentialSmoothing(
    daily_series, 
    trend='add', 
    seasonal='add',
    seasonal_periods=7  # Weekly seasonality
)
forecast = model.fit().forecast(30)  # 30-day prediction
```

**Result:** Projected Q1 2026 average daily load: 977,211 transactions

### 4.2 Anomaly Detection

**Algorithm:** Isolation Forest

```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.05, random_state=42)
anomalies = model.fit_predict(features)
```

**Result:** Detected 121 geographic fraud clusters, 7 date-specific spikes

### 4.3 District Clustering

**Algorithm:** K-Means

- 4 clusters identified:
  1. Growth Zones (high enrollment, low updates)
  2. Mature Hubs (low enrollment, high updates)
  3. Balanced (moderate both)
  4. Dormant (low both)

### 4.4 Statistical Testing

**Test:** Independent t-test for monsoon effect

```python
from scipy.stats import ttest_ind

t_stat, p_value = ttest_ind(monsoon_daily, non_monsoon_daily)
# p < 0.05 → Statistically significant difference
```

---

## 5. Visualization Strategy

### Static Charts
- matplotlib + seaborn for publication-quality graphs
- Saved as PNG (150 DPI)

### Interactive Dashboards
- Plotly for interactive charts
- Saved as HTML for browser viewing

### Geographic Maps
- Plotly choropleth with India GeoJSON
- Interactive state-level coloring

---

## 6. Tools & Libraries

| Category | Libraries |
|----------|-----------|
| Data Processing | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Machine Learning | sklearn |
| Time Series | statsmodels |
| Statistics | scipy.stats |
| Export | python-docx, json |

---

*Next: [3_KEY_INSIGHTS.md](./3_KEY_INSIGHTS.md) - What we discovered*
