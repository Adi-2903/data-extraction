# 🆔 UIDAI Hackathon 2026 - Aadhaar Analytics

> **Track:** Data Extraction & Pattern Mining  
> **Team:** Last Commit

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Records Analyzed** | 4,937,073 |
| **Enrollments** | 5,435,484 |
| **Demographic Updates** | 49,295,185 |
| **Biometric Updates** | 69,763,095 |
| **Districts Covered** | 890 |
| **States Covered** | 36 |

---

## 🎯 Key Discoveries

### 1. Ghost Enrollees Crisis 🚨
> **92% of citizens enroll and never return** (Lifecycle Progression Index = 0.08)

This represents **₹50 crores wasted annually** on re-enrollment vs re-engagement.

### 2. Pareto Effect
> **37% of districts drive 80% of all enrollments**

Top Districts: Thane (43,688), Sitamarhi (42,232), Bahraich (39,338)

### 3. Migration Corridors
> **49.3 million demographic updates** reveal clear migration patterns

Top Hubs: Thane (447K), Pune (438K), South 24 Parganas (401K)

### 4. Age Distribution Anomaly
> **65% of enrollments are infants (0-5 years)** - Adults only 3.1%!

Focus: Baal Aadhaar campaigns in UP, MP, Maharashtra

### 5. State Dominance
> **UP + Maharashtra = 20% of all biometric updates**

UP: 9.6M biometric, 8.5M demographic updates

---

## 📁 Project Structure

```
gove hackathon/
├── dataset/                       # Raw CSV files (12 files, ~220MB)
│   ├── api_data_aadhar_enrolment_*.csv (3 files)
│   ├── api_data_aadhar_demographic_*.csv (5 files)
│   └── api_data_aadhar_biometric_*.csv (4 files)
│
├── dataset_cleaned/               # Cleaned CSV files (3 files)
│   ├── enrollment_cleaned.csv
│   ├── demographic_cleaned.csv
│   └── biometric_cleaned.csv
│
├── data_cleaning/                 # Data cleaning workspace
│   ├── clean_data.py              # Cleaning script with mappings
│   └── data_cleaning_pipeline.ipynb  # Jupyter notebook
│
├── output/                        # Generated Visualizations
│   ├── insights.json              # Extracted statistics
│   ├── *.png                      # 18+ static charts
│   ├── *.html                     # 5 interactive dashboards
│   ├── enrollment/                # Enrollment-specific charts
│   ├── demographic/               # Demographic charts
│   └── biometric/                 # Biometric charts
│
├── submission/                    # Hackathon submission docs
│   ├── 1_PROBLEM_STATEMENT.md
│   ├── 2_METHODOLOGY.md
│   ├── 3_KEY_INSIGHTS.md
│   ├── 4_RECOMMENDATIONS.md
│   ├── 5_SDG_ALIGNMENT.md
│   ├── POLICY_BRIEF.txt
│   └── UIDAI_Hackathon_Submission.docx
│
├── analysis.py                    # Main 15-phase analysis (1449 lines)
├── app.py                         # Streamlit Dashboard (1443 lines)
├── clean_data.py                  # Data cleaning script (550 lines)
├── domain_enrollment.py           # Enrollment deep-dive (572 lines)
├── domain_demographic.py          # Demographic analysis (496 lines)
├── domain_biometric.py            # Biometric analysis (670 lines)
├── extract_insights.py            # Insights extractor (607 lines)
├── generate_submission_doc.py     # Document generator
│
├── analysis_notebook.ipynb        # Jupyter notebook version
├── DOMAIN_INSIGHTS.md             # Detailed findings
├── SUBMISSION_DOCUMENT.md         # Full submission doc
├── BEGINNERS_GUIDE.md             # Methodology explainer
└── requirements.txt               # Dependencies
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full analysis (15 phases)
python analysis.py

# Extract insights to JSON
python extract_insights.py

# Launch interactive Streamlit dashboard
streamlit run app.py

# Or open static HTML dashboards
start output/india_choropleth.html
start output/interactive_ghost_sankey.html
```

---

## 📈 Visualizations Generated

### Static Charts (25+)
- Age pyramids, seasonality patterns, correlations
- Saved as PNG in `output/` and subdirectories

### Interactive Dashboards (5)
| Dashboard | Purpose |
|-----------|---------|
| `output/india_choropleth.html` | State-level enrollment map |
| `output/interactive_ghost_sankey.html` | Attrition funnel (92% drop!) |
| `output/interactive_strategy_map.html` | Resource deployment |
| `output/animated_enrollment_timeline.html` | Growth animation |
| **Streamlit:** `streamlit run app.py` | Full analytics dashboard |

---

## 💡 Strategic Recommendations

| Priority | Action | Impact | Cost |
|----------|--------|--------|------|
| 🔴 HIGH | Re-engage 92% dormant enrollees | +233% lifecycle completion | ₹30 Cr savings |
| 🔴 HIGH | Mobile vans to urgency districts | +15% compliance | ₹3.5 Cr |
| 🔴 HIGH | School-based biometric camps | +20% compliance | ₹1.2 Cr |
| 🟡 MEDIUM | Pre-position for Oct-Dec surge | -30% wait time | ₹0.8 Cr |
| 🟡 MEDIUM | Self-service kiosks in mature hubs | -40% cost | ₹2.5 Cr |

**Total Projected Annual Savings: ₹65 Crores**

---

## 🧮 Novel Formulas Developed

| Formula | Purpose |
|---------|---------|
| **LPI** (Lifecycle Progression Index) | Citizen journey completeness |
| **UCP** (Update Cascade Probability) | Predicts full lifecycle completion |
| **MDI** (Migration Directionality Index) | Emigration vs immigration hubs |
| **Saturation Index** | Post-enrollment activity levels |
| **Health Score** | Composite district performance |

---

## 🌍 SDG Alignment

- **SDG 16.9:** Legal identity for all
- **SDG 1.3:** Social protection systems
- **SDG 10.2:** Inclusion of all

---

## 🛠️ Technologies Used

| Category | Tools |
|----------|-------|
| Data Processing | pandas, numpy |
| Visualization | matplotlib, seaborn, plotly |
| Dashboard | streamlit |
| Machine Learning | sklearn (Random Forest, K-Means, DBSCAN, Isolation Forest) |
| Time Series | statsmodels (Holt-Winters) |
| Statistics | scipy.stats |

---

## 📄 Key Files for Judges

| File | Purpose |
|------|---------|
| `DOMAIN_INSIGHTS.md` | All 31+ insights with explanations |
| `SUBMISSION_DOCUMENT.md` | Complete hackathon submission |
| `output/interactive_ghost_sankey.html` | **Proves the Problem** (92% attrition) |
| `output/interactive_strategy_map.html` | **Proves the Solution** |
| `output/phase5_forecast.png` | **Proves the Urgency** |
| `submission/UIDAI_Hackathon_Submission.docx` | Word document for PDF |

---

## 👥 Team

**Last Commit**

---

*Generated on January 19, 2026*
