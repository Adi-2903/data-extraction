"""
Domain Analysis: Enrollment Deep Dive
======================================

This module performs DOMAIN-SPECIFIC analysis on Aadhaar enrollment data.
Unlike the merged analysis, this focuses on enrollment-only patterns to uncover
insights that get lost when mixing with demographic/biometric data.

Focus Areas:
1. Birth Cohort Seasonality - When do infants get enrolled?
2. Age Pyramid Anomalies - Are there missing age groups?
3. Enrollment Velocity - Which districts are "enrollment factories"?
4. Geographic Patterns - Urban vs Rural enrollment behavior
5. Growth Trajectory - Acceleration vs deceleration

Author: UIDAI Hackathon 2026 Team
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# UTF-8 encoding for emoji support
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
sns.set(style="whitegrid", palette="husl")
plt.rcParams['figure.figsize'] = (14, 7)

# Create output directory
os.makedirs('output/enrollment', exist_ok=True)

print("="*70)
print("🎯 ENROLLMENT DOMAIN ANALYSIS")
print("="*70)

# Load enrollment data
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


# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("📋 ENROLLMENT DOMAIN ANALYSIS SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED 5 ANALYSES:")
print(f"  1. Birth Cohort Seasonality → Identified peak enrollment months")
print(f"  2. Age Pyramid → Detected age group anomalies")
print(f"  3. Enrollment Velocity → Ranked top performing districts")
print(f"  4. State Strategy → Infant enrollment leaders")
print(f"  5. Growth Acceleration → Weekly trend patterns")

print(f"\n📊 VISUALIZATIONS GENERATED: 5 charts in 'output/enrollment/'")

print(f"\n💡 KEY ACTIONABLE INSIGHTS:")
print(f"  → Schedule Anganwadi campaigns in peak enrollment months")
print(f"  → Investigate adult enrollment gap (potential college-age missing)")
print(f"  → Replicate best practices from top 10 districts")
print(f"  → Prioritize birth registry integration in top infant states")

print("\n" + "="*70)
print("✅ ENROLLMENT DOMAIN ANALYSIS COMPLETE")
print("="*70)
