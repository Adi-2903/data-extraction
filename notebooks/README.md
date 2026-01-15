# Notebooks Quick Start Guide

## 📁 Notebook Structure

```
notebooks/
├── 00_data_loading_utilities.ipynb     # Foundation
├── 01_enrollment_analysis.ipynb        # 5 enrollment charts
├── 02_demographic_analysis.ipynb       # 5 demographic charts
├── 03_biometric_analysis.ipynb         # 4 biometric charts
├── 04_cross_domain_integration.ipynb   # Master cube + correlations
├── 05_predictive_ml_modeling.ipynb     # 5 ML algorithms
└── 06_executive_summary.ipynb          # Judge-ready summary
```

## 🚀 How to Run

### Quick Start (For Judges):
```bash
# Start with the executive summary
jupyter notebook notebooks/06_executive_summary.ipynb
```

### Full Analysis Pipeline:
```bash
# Run in order:
jupyter notebook notebooks/00_data_loading_utilities.ipynb  # First
jupyter notebook notebooks/01_enrollment_analysis.ipynb
jupyter notebook notebooks/02_demographic_analysis.ipynb
jupyter notebook notebooks/03_biometric_analysis.ipynb
jupyter notebook notebooks/04_cross_domain_integration.ipynb
jupyter notebook notebooks/05_predictive_ml_modeling.ipynb
jupyter notebook notebooks/06_executive_summary.ipynb       # Demo-ready
```

## 📊 What Each Notebook Does

| Notebook | Purpose | Charts | Can Run Alone? |
|----------|---------|--------|----------------|
| **00** | Load & clean data | 0 | ✅ Yes |
| **01** | Enrollment insights | 5 | ✅ Yes (needs 00) |
| **02** | Migration patterns | 5 | ✅ Yes (needs 00) |
| **03** | Biometric compliance | 4 | ✅ Yes (needs 00) |
| **04** | Cross-domain analysis | 3 | ⚠️ Needs all 3 domains |
| **05** | ML predictions | 3 | ⚠️ Needs 04 (master_df) |
| **06** | Executive summary | 1 | ✅ Yes (standalone) |

## 💡 Tips

- **For quick demo**: Run notebook 06 only (executive summary)
- **For domain focus**: Run 00 + your domain (e.g., 00 + 01 for enrollment)
- **For complete pipeline**: Run all 7 in sequence
- **For merging**: Copy-paste cells sequentially (see implementation_plan.md)

## 🔧 Troubleshooting

**Issue**: "Module not found"
- **Solution**: Make sure you're in the project root directory

**Issue**: "File not found"
- **Solution**: Check paths are relative to notebooks/ directory (use `../dataset/`)

**Issue**: Notebooks 01-03 don't run
- **Solution**: Run notebook 00 first to load data

## 📝 Note on Implementation

**Design Choice**: Notebooks 01-05 use `%run` to execute existing `.py` scripts instead of duplicating code. This ensures:
- ✅ Single source of truth
- ✅ Easy maintenance
- ✅ Consistent results
- ✅ Faster development

If you want fully self-contained notebooks (copy-pasted code), refer to `implementation_plan.md` for the merge strategy.
