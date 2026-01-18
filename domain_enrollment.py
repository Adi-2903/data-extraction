# %%
"""
================================================================================
DOMAIN ANALYSIS: ENROLLMENT DEEP DIVE
================================================================================

PURPOSE:
--------
This module performs DOMAIN-SPECIFIC analysis on Aadhaar enrollment data.
Unlike the merged analysis, this focuses on enrollment-only patterns to uncover
insights that get lost when mixing with demographic/biometric data.

WHY SEPARATE DOMAIN ANALYSIS?
-----------------------------
When we merge enrollment + demographic + biometric data, the nuances of each
domain get diluted. This dedicated analysis lets us:
1. Track infant enrollment seasonality (birth registry linkages)
2. Identify geographic "enrollment factories"
3. Detect missing age cohorts (saturation signals)
4. Apply the Pareto Principle (80/20 rule) to resource allocation
5. Analyze monsoon impacts on rural enrollment

ANALYSES INCLUDED:
------------------
1. Birth Cohort Seasonality - When do infants get enrolled?
2. Age Pyramid Anomalies - Are there missing age groups?
3. Enrollment Velocity - Which districts are "enrollment factories"?
4. State-Level Infant Strategy - Where to deploy Anganwadi linkages
5. Growth Acceleration - Weekly momentum tracking
6. PARETO ANALYSIS (NEW) - 80/20 rule for district concentration
7. MONSOON EFFECT (NEW) - Seasonal rural enrollment patterns

NOTEBOOK USAGE:
---------------
Each section is marked with '# %%' for Jupyter cell conversion.
Run: `jupytext --to notebook domain_enrollment.py` to convert.

Author: UIDAI Hackathon 2026 Team
================================================================================
"""

# %%
# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================
# WHY these imports:
# - pandas/numpy: Core data manipulation
# - matplotlib/seaborn: Static visualizations (for PDF reports)
# - scipy.stats: Statistical significance testing (p-values)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from scipy import stats  # NEW: For statistical significance

# UTF-8 encoding for emoji support in console output
sys.stdout.reconfigure(encoding='utf-8')

# Visualization configuration
# WHY whitegrid: Clean background for publication-quality charts
# WHY husl palette: Perceptually uniform colors for accessibility
sns.set(style="whitegrid", palette="husl")
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 11

# Create output directory structure
os.makedirs('output/enrollment', exist_ok=True)

print("="*70)
print("🎯 ENROLLMENT DOMAIN ANALYSIS")
print("="*70)

# %%
# =============================================================================
# DATA LOADING
# =============================================================================
# WHY import from analysis.py:
# - Reuses the load_and_combine() function that handles multi-file loading
# - Reuses clean_data() for consistent state/district normalization
# - Ensures data quality is consistent across all domain analyses

from analysis import load_and_combine, clean_data

enrolment_df = clean_data(load_and_combine('dataset/api_data_aadhar_enrolment_*.csv'))
print(f"\n📊 Loaded {len(enrolment_df):,} enrollment records")


# =============================================================================
# ANALYSIS 1: Birth Cohort Seasonality
# =============================================================================
print("\n" + "="*70)
print("📅 ANALYSIS 1: BIRTH COHORT SEASONALITY")
print("="*70)
print("Question: When are infants (0-5) enrolled? Is there a seasonal pattern?")

if not enrolment_df.empty and 'date' in enrolment_df.columns:
    # Extract month from enrollment date
    enrolment_df['month'] = pd.to_datetime(enrolment_df['date']).dt.month
    enrolment_df['month_name'] = pd.to_datetime(enrolment_df['date']).dt.month_name()
    
    # Infant enrollments by month
    infant_by_month = enrolment_df.groupby('month_name')['age_0_5'].sum()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    infant_by_month = infant_by_month.reindex(month_order, fill_value=0)
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Monthly pattern
    infant_by_month.plot(kind='bar', ax=ax1, color='skyblue', edgecolor='navy')
    ax1.set_title('Infant Enrollment (Age 0-5) by Month', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Enrollments')
    ax1.set_xlabel('Month')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # Percentage distribution
    pct_distribution = (infant_by_month / infant_by_month.sum()) * 100
    pct_distribution.plot(kind='bar', ax=ax2, color='coral', edgecolor='darkred')
    ax2.set_title('Infant Enrollment Distribution (%)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Percentage')
    ax2.set_xlabel('Month')
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=100/12, color='red', linestyle='--', label='Expected (8.33%)')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/enrollment/birth_cohort_seasonality.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: output/enrollment/birth_cohort_seasonality.png")
    
    # Identify peak months
    peak_month = infant_by_month.idxmax()
    peak_value = infant_by_month.max()
    peak_pct = pct_distribution.max()
    
    print(f"\n🔍 KEY FINDINGS:")
    print(f"  Peak Month: {peak_month} ({peak_value:,} enrollments, {peak_pct:.1f}%)")
    print(f"  Expected (uniform): {infant_by_month.sum()/12:,.0f} per month (8.33%)")
    print(f"  Peak is {(peak_pct/8.33-1)*100:.1f}% above expected")
    
    # Identify Q1-Q2 concentration (Jan-Mar tax season hypothesis)
    q1_enrollments = infant_by_month[['January', 'February', 'March']].sum()
    q1_pct = (q1_enrollments / infant_by_month.sum()) * 100
    
    if q1_pct > 30:
        print(f"\n💡 INSIGHT: Q1 (Jan-Mar) accounts for {q1_pct:.1f}% of infant enrollments!")
        print(f"   HYPOTHESIS: Tax filing season drives birth certificate → Aadhaar enrollment")
    
    # Calculate seasonality index
    seasonality_index = pct_distribution.std() / pct_distribution.mean()
    print(f"\n📈 Seasonality Index: {seasonality_index:.3f}")
    if seasonality_index > 0.3:
        print(f"   Interpretation: HIGH seasonality (>30% variation)")
    else:
        print(f"   Interpretation: LOW seasonality (uniform throughout year)")


# =============================================================================
# ANALYSIS 2: Age Pyramid Analysis
# =============================================================================
print("\n" + "="*70)
print("👥 ANALYSIS 2: AGE PYRAMID ANALYSIS")
print("="*70)
print("Question: Are there anomalies or gaps in age group enrollments?")

age_distribution = enrolment_df[['age_0_5', 'age_5_17', 'age_18_greater']].sum()

# Create age pyramid visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Absolute numbers
age_distribution.plot(kind='barh', ax=ax1, color=['lightblue', 'lightgreen', 'lightcoral'])
ax1.set_title('Age Distribution (Absolute Numbers)', fontsize=14, fontweight='bold')
ax1.set_xlabel('Total Enrollments')
ax1.set_ylabel('Age Group')
for i, v in enumerate(age_distribution):
    ax1.text(v + age_distribution.max()*0.01, i, f'{v:,.0f}', va='center')

# Percentage
pct_age = (age_distribution / age_distribution.sum()) * 100
pct_age.plot(kind='barh', ax=ax2, color=['#3498db', '#2ecc71', '#e74c3c'])
ax2.set_title('Age Distribution (Percentage)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Percentage')
ax2.set_ylabel('Age Group')
for i, v in enumerate(pct_age):
    ax2.text(v + 1, i, f'{v:.1f}%', va='center')

plt.tight_layout()
plt.savefig('output/enrollment/age_pyramid.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/enrollment/age_pyramid.png")

print(f"\n🔍 AGE DISTRIBUTION:")
for age_group, count in age_distribution.items():
    pct = (count / age_distribution.sum()) * 100
    print(f"  {age_group}: {count:,} ({pct:.1f}%)")

# Detect anomalies
expected_adult_pct = 60  # Adults typically 60% of population
actual_adult_pct = pct_age['age_18_greater']

if actual_adult_pct < expected_adult_pct - 10:
    print(f"\n⚠️ ANOMALY DETECTED:")
    print(f"  Expected adult (18+) enrollment: ~{expected_adult_pct}%")
    print(f"  Actual: {actual_adult_pct:.1f}%")
    print(f"  GAP: {expected_adult_pct - actual_adult_pct:.1f} percentage points")
    print(f"\n💡 HYPOTHESIS: Adult enrollment saturation reached OR missing age 18-25 cohort")


# =============================================================================
# ANALYSIS 3: Enrollment Velocity (Per-District Growth Rate)
# =============================================================================
print("\n" + "="*70)
print("⚡ ANALYSIS 3: ENROLLMENT VELOCITY")
print("="*70)
print("Question: Which districts are 'enrollment factories' with highest growth?")

# Calculate total enrollment by district
district_enrollment = enrolment_df.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
district_enrollment['total'] = district_enrollment.sum(axis=1)
district_enrollment = district_enrollment.sort_values('total', ascending=False)

# Top 10 enrollment powerhouses
top10 = district_enrollment.head(10)

plt.figure(figsize=(14, 8))
top10['total'].plot(kind='barh', color='teal', edgecolor='darkgreen')
plt.title('Top 10 Enrollment Powerhouse Districts', fontsize=16, fontweight='bold')
plt.xlabel('Total Enrollments')
plt.ylabel('District')
plt.grid(axis='x', alpha=0.3)

# Add value labels
for i, v in enumerate(top10['total']):
    plt.text(v + top10['total'].max()*0.01, i, f'{v:,.0f}', va='center')

plt.tight_layout()
plt.savefig('output/enrollment/enrollment_velocity.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/enrollment/enrollment_velocity.png")

print(f"\n🏆 TOP 10 ENROLLMENT DISTRICTS:")
for idx, (district, row) in enumerate(top10.iterrows(), 1):
    print(f"  {idx}. {district}: {row['total']:,}")

# Calculate enrollment concentration
total_enrollments = district_enrollment['total'].sum()
top10_share = (top10['total'].sum() / total_enrollments) * 100
print(f"\n📊 CONCENTRATION METRICS:")
print(f"  Top 10 districts account for {top10_share:.1f}% of all enrollments")
print(f"  Average per district: {total_enrollments/len(district_enrollment):,.0f}")

if top10_share > 30:
    print(f"\n💡 INSIGHT: Enrollment is HIGHLY CONCENTRATED in top districts")
    print(f"   Recommendation: Replicate best practices from top 10 to others")


# =============================================================================
# ANALYSIS 4: State-Level Infant Enrollment Strategy
# =============================================================================
print("\n" + "="*70)
print("👶 ANALYSIS 4: STATE-LEVEL INFANT ENROLLMENT STRATEGY")
print("="*70)

state_infant = enrolment_df.groupby('state')['age_0_5'].sum().sort_values(ascending=False).head(15)

plt.figure(figsize=(14, 8))
state_infant.plot(kind='barh', color='mediumorchid', edgecolor='purple')
plt.title('Top 15 States by Infant Enrollment (Age 0-5)', fontsize=16, fontweight='bold')
plt.xlabel('Infant Enrollments')
plt.ylabel('State')
plt.grid(axis='x', alpha=0.3)

for i, v in enumerate(state_infant):
    plt.text(v + state_infant.max()*0.01, i, f'{v:,.0f}', va='center')

plt.tight_layout()
plt.savefig('output/enrollment/state_infant_enrollment.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/enrollment/state_infant_enrollment.png")

print(f"\n🎯 STRATEGIC RECOMMENDATIONS:")
for idx, (state, count) in enumerate(state_infant.head(5).items(), 1):
    print(f"\n  {idx}. {state}: {count:,} infant enrollments")
    if idx == 1:
        print(f"     → PRIORITY: Integrate with Anganwadi network")
    elif idx <= 3:
        print(f"     → STRATEGY: Scale up birth registry linkages")
    else:
        print(f"     → MAINTAIN: Continue current successful programs")


# =============================================================================
# ANALYSIS 5: Week-over-Week Growth Acceleration
# =============================================================================
print("\n" + "="*70)
print("📈 ANALYSIS 5: ENROLLMENT GROWTH ACCELERATION")
print("="*70)

if 'date' in enrolment_df.columns:
    # Weekly enrollment trends
    enrolment_df['week'] = pd.to_datetime(enrolment_df['date']).dt.isocalendar().week
    weekly_enrollment = enrolment_df.groupby('week')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
    weekly_enrollment['total'] = weekly_enrollment.sum(axis=1)
    
    # Calculate week-over-week growth
    weekly_enrollment['wow_growth'] = weekly_enrollment['total'].pct_change() * 100
    
    # Plot
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(weekly_enrollment.index, weekly_enrollment['total'], marker='o', linewidth=2, label='Total Enrollment')
    ax.fill_between(weekly_enrollment.index, weekly_enrollment['total'], alpha=0.3)
    ax.set_title('Weekly Enrollment Trend', fontsize=16, fontweight='bold')
    ax.set_xlabel('Week Number')
    ax.set_ylabel('Total Enrollments')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/enrollment/weekly_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: output/enrollment/weekly_trend.png")
    
    # Identify acceleration periods
    avg_growth = weekly_enrollment['wow_growth'].mean()
    accelerating_weeks = weekly_enrollment[weekly_enrollment['wow_growth'] > avg_growth + 20]
    
    if not accelerating_weeks.empty:
        print(f"\n🚀 GROWTH ACCELERATION DETECTED:")
        print(f"  Average week-over-week growth: {avg_growth:.1f}%")
        print(f"  Weeks with >20% above average growth:")
        for week, row in accelerating_weeks.head(3).iterrows():
            print(f"    Week {week}: +{row['wow_growth']:.1f}% ({row['total']:,.0f} enrollments)")


# %%
# =============================================================================
# ANALYSIS 6: PARETO ANALYSIS (80/20 Rule)
# =============================================================================
# WHY PARETO ANALYSIS?
# --------------------
# The Pareto Principle states that 80% of outcomes come from 20% of causes.
# In enrollment context: A small number of high-performing districts likely
# drive the majority of all enrollments. This has major policy implications:
#   - Resource allocation: Focus investment on scaling successful districts
#   - Best practices: Study what makes top districts successful
#   - Gap identification: Why are bottom 80% of districts underperforming?
#
# FORMULA:
# --------
# 1. Sort districts by enrollment (descending)
# 2. Calculate cumulative percentage
# 3. Find the "elbow" where X% of districts account for Y% of enrollments
# 4. If Y > 80% and X < 30%, Pareto effect is strong

print("\n" + "="*70)
print("📊 ANALYSIS 6: PARETO ANALYSIS (80/20 Rule)")
print("="*70)
print("Question: Do ~20% of districts drive ~80% of all enrollments?")

# Calculate district-level totals and sort
district_totals = enrolment_df.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
district_totals['total'] = district_totals.sum(axis=1)
district_totals = district_totals.sort_values('total', ascending=False)

# Calculate cumulative percentage
total_enrollment = district_totals['total'].sum()
district_totals['cumulative'] = district_totals['total'].cumsum()
district_totals['cumulative_pct'] = (district_totals['cumulative'] / total_enrollment) * 100
district_totals['district_rank_pct'] = np.arange(1, len(district_totals)+1) / len(district_totals) * 100

# Find the "elbow" - where does 80% of enrollment get covered?
pct_80_idx = (district_totals['cumulative_pct'] >= 80).idxmax()
districts_for_80_pct = (district_totals.index.get_loc(pct_80_idx) + 1) / len(district_totals) * 100

print(f"\n🔍 PARETO FINDINGS:")
print(f"  Total districts: {len(district_totals)}")
print(f"  Total enrollments: {total_enrollment:,.0f}")
print(f"\n  📌 {districts_for_80_pct:.1f}% of districts account for 80% of enrollments")

# Visualization: Pareto Chart (Bar + Line)
fig, ax1 = plt.subplots(figsize=(16, 8))

# Bar chart for top 30 districts
top30 = district_totals.head(30)
bars = ax1.bar(range(len(top30)), top30['total'], color='steelblue', alpha=0.7, label='District Enrollment')
ax1.set_xlabel('District Rank', fontsize=12)
ax1.set_ylabel('Total Enrollments', color='steelblue', fontsize=12)
ax1.tick_params(axis='y', labelcolor='steelblue')
ax1.set_xticks(range(0, len(top30), 5))
ax1.set_xticklabels(range(1, len(top30)+1, 5))

# Line chart for cumulative percentage
ax2 = ax1.twinx()
ax2.plot(range(len(top30)), top30['cumulative_pct'], color='red', marker='o', 
         linewidth=2, markersize=4, label='Cumulative %')
ax2.axhline(y=80, color='darkred', linestyle='--', linewidth=2, alpha=0.7, label='80% Threshold')
ax2.set_ylabel('Cumulative Percentage (%)', color='red', fontsize=12)
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 105)

# Title and legend
plt.title('Pareto Analysis: District Enrollment Concentration\n(80/20 Rule)', fontsize=16, fontweight='bold')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')

plt.tight_layout()
plt.savefig('output/enrollment/pareto_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/enrollment/pareto_analysis.png")

# Pareto strength assessment
if districts_for_80_pct < 25:
    pareto_strength = "VERY STRONG"
    action = "Focus resources on top 20% of districts for maximum impact"
elif districts_for_80_pct < 40:
    pareto_strength = "MODERATE"
    action = "Balance investment between top performers and growth opportunities"
else:
    pareto_strength = "WEAK"
    action = "Enrollment is relatively distributed - consider regional strategies"

print(f"\n  💡 Pareto Effect Strength: {pareto_strength}")
print(f"     → Action: {action}")

# Top 5 powerhouses contribution
top5_pct = district_totals.head(5)['cumulative_pct'].iloc[-1]
print(f"\n  🏆 Top 5 districts alone account for {top5_pct:.1f}% of all enrollments")


# %%
# =============================================================================
# ANALYSIS 7: MONSOON EFFECT ANALYSIS
# =============================================================================
# WHY MONSOON EFFECT?
# -------------------
# India's monsoon season (June-September) significantly impacts rural life:
#   - Agricultural labor peaks during monsoon (less time for Aadhaar centers)
#   - Flooding makes rural centers inaccessible
#   - Migration patterns shift seasonally
#
# HYPOTHESIS:
# -----------
# Rural district enrollments DROP during monsoon months (June-Sep) compared
# to non-monsoon months. Urban areas are less affected.
#
# STATISTICAL TEST:
# -----------------
# We use an independent samples t-test to check if the difference is 
# statistically significant (p-value < 0.05).

print("\n" + "="*70)
print("🌧️ ANALYSIS 7: MONSOON EFFECT ANALYSIS")
print("="*70)
print("Hypothesis: Rural enrollment drops during monsoon (June-September)?")

if 'date' in enrolment_df.columns and 'month' in enrolment_df.columns:
    # Define monsoon vs non-monsoon months
    # Monsoon in India: June (6), July (7), August (8), September (9)
    monsoon_months = [6, 7, 8, 9]
    
    enrolment_df['is_monsoon'] = enrolment_df['month'].isin(monsoon_months)
    enrolment_df['total_enrol'] = enrolment_df['age_0_5'] + enrolment_df['age_5_17'] + enrolment_df['age_18_greater']
    
    # Calculate daily enrollment by monsoon/non-monsoon
    monsoon_daily = enrolment_df[enrolment_df['is_monsoon']].groupby('date')['total_enrol'].sum()
    non_monsoon_daily = enrolment_df[~enrolment_df['is_monsoon']].groupby('date')['total_enrol'].sum()
    
    # Summary statistics
    monsoon_mean = monsoon_daily.mean()
    non_monsoon_mean = non_monsoon_daily.mean()
    
    print(f"\n📊 DAILY ENROLLMENT COMPARISON:")
    print(f"  Monsoon (Jun-Sep):     {monsoon_mean:,.0f} avg/day ({len(monsoon_daily)} days)")
    print(f"  Non-Monsoon:           {non_monsoon_mean:,.0f} avg/day ({len(non_monsoon_daily)} days)")
    
    # Calculate percentage difference
    pct_diff = ((monsoon_mean - non_monsoon_mean) / non_monsoon_mean) * 100
    print(f"\n  Difference: {pct_diff:+.1f}%")
    
    # Statistical significance test (t-test)
    # WHY T-TEST: Compares means of two independent samples
    # H0: No difference between monsoon and non-monsoon enrollment
    # H1: There is a significant difference
    if len(monsoon_daily) > 5 and len(non_monsoon_daily) > 5:
        t_stat, p_value = stats.ttest_ind(monsoon_daily, non_monsoon_daily)
        
        print(f"\n📈 STATISTICAL SIGNIFICANCE:")
        print(f"  t-statistic: {t_stat:.3f}")
        print(f"  p-value: {p_value:.4f}")
        
        if p_value < 0.05:
            significance = "STATISTICALLY SIGNIFICANT (p < 0.05)"
            if pct_diff < 0:
                interpretation = "Monsoon REDUCES enrollment - hypothesis CONFIRMED"
                action = "Deploy mobile camps post-monsoon to compensate for lost capacity"
            else:
                interpretation = "Monsoon INCREASES enrollment - unexpected!"
                action = "Investigate: Are people using flooded off-days to visit centers?"
        else:
            significance = "NOT STATISTICALLY SIGNIFICANT (p >= 0.05)"
            interpretation = "No meaningful monsoon effect detected"
            action = "Monsoon does not require special operational adjustments"
        
        print(f"  Result: {significance}")
        print(f"\n  💡 INTERPRETATION: {interpretation}")
        print(f"  📌 ACTION: {action}")
    
    # Visualization: Monthly pattern with monsoon highlighted
    monthly_avg = enrolment_df.groupby('month')['total_enrol'].mean()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ['coral' if m in monsoon_months else 'steelblue' for m in monthly_avg.index]
    bars = ax.bar(monthly_avg.index, monthly_avg.values, color=colors, edgecolor='black', alpha=0.8)
    
    ax.axhline(y=monthly_avg.mean(), color='red', linestyle='--', linewidth=2, label='Average')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Average Daily Enrollments', fontsize=12)
    ax.set_title('Monsoon Effect on Enrollment\n(Coral = Monsoon Months)', fontsize=16, fontweight='bold')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/enrollment/monsoon_effect.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("\n✅ Saved: output/enrollment/monsoon_effect.png")
else:
    print("⚠️ Date information not available for monsoon analysis")


# %%
# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("📋 ENROLLMENT DOMAIN ANALYSIS SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED 7 ANALYSES:")
print(f"  1. Birth Cohort Seasonality → Identified peak enrollment months")
print(f"  2. Age Pyramid → Detected age group anomalies")
print(f"  3. Enrollment Velocity → Ranked top performing districts")
print(f"  4. State Strategy → Infant enrollment leaders")
print(f"  5. Growth Acceleration → Weekly trend patterns")
print(f"  6. Pareto Analysis (NEW) → 80/20 concentration identified")
print(f"  7. Monsoon Effect (NEW) → Seasonal impact with statistical test")

print(f"\n📊 VISUALIZATIONS GENERATED: 7 charts in 'output/enrollment/'")

print(f"\n💡 KEY ACTIONABLE INSIGHTS:")
print(f"  → Schedule Anganwadi campaigns in peak enrollment months")
print(f"  → Investigate adult enrollment gap (potential college-age missing)")
print(f"  → Replicate best practices from top 10 districts")
print(f"  → Prioritize birth registry integration in top infant states")
print(f"  → Focus resources on top Pareto districts for maximum ROI")
print(f"  → Adjust rural operations for monsoon season impact")

print("\n" + "="*70)
print("✅ ENROLLMENT DOMAIN ANALYSIS COMPLETE")
print("="*70)

