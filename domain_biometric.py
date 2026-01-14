"""
Domain Analysis: Biometric Deep Dive
=====================================

This module analyzes BIOMETRIC UPDATE patterns to uncover:
- Compliance rates by age cohort
- Cohort retention tracking (% who update over time)
- Regional compliance variations
- Lifecycle completion paths

Focus on mandatory biometric updates at age 5 and 15.

Author: UIDAI Hackathon 2026 Team
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from advanced_formulas import calculate_lifecycle_progression_index, calculate_update_cascade_probability, interpret_lpi

# UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
sns.set(style="whitegrid", palette="viridis")
plt.rcParams['figure.figsize'] = (14, 7)

# Create output directory
os.makedirs('output/biometric', exist_ok=True)

print("="*70)
print("🔐 BIOMETRIC DOMAIN ANALYSIS")
print("="*70)

# Load biometric data
from analysis import load_and_combine, clean_data

biometric_df = clean_data(load_and_combine('dataset/api_data_aadhar_biometric_*.csv'))
print(f"\n📊 Loaded {len(biometric_df):,} biometric update records")


# =============================================================================
# ANALYSIS 1: Compliance Rate by Age Cohort
# =============================================================================
print("\n" + "="*70)
print("✅ ANALYSIS 1: AGE-WISE COMPLIANCE RATES")
print("="*70)
print("Question: Which age groups comply with mandatory biometric updates?")

# Calculate age-wise biometric updates
age_bio = biometric_df[['bio_age_5_17', 'bio_age_17_']].sum()

# Load enrollment data for comparison
enrolment_df = clean_data(load_and_combine('dataset/api_data_aadhar_enrolment_*.csv'))
age_enrol = enrolment_df[['age_5_17', 'age_18_greater']].sum()

# Create comparison dataframe
compliance_data = pd.DataFrame({
    'Enrolled': [age_enrol['age_5_17'], age_enrol['age_18_greater']],
    'Biometric_Updates': [age_bio['bio_age_5_17'], age_bio['bio_age_17_']]
}, index=['Age 5-17 (Mandatory)', 'Age 18+ (Voluntary)'])

# Calculate compliance rate (updates as % of enrollment)
compliance_data['Compliance_Rate_%'] = (compliance_data['Biometric_Updates'] / 
                                        (compliance_data['Enrolled'] + 1)) * 100

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Absolute numbers comparison
compliance_data[['Enrolled', 'Biometric_Updates']].plot(kind='bar', ax=ax1, 
                                                          color=['lightblue', 'coral'])
ax1.set_title('Enrollment vs Biometric Updates by Age Group', fontsize=14, fontweight='bold')
ax1.set_ylabel('Count')
ax1.set_xlabel('Age Group')
ax1.tick_params(axis='x', rotation=30)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Compliance rate
compliance_data['Compliance_Rate_%'].plot(kind='bar', ax=ax2, color=['green', 'orange'])
ax2.set_title('Biometric Update Compliance Rate', fontsize=14, fontweight='bold')
ax2.set_ylabel('Compliance Rate (%)')
ax2.set_xlabel('Age Group')
ax2.tick_params(axis='x', rotation=30)
ax2.axhline(y=100, color='red', linestyle='--', label='100% Compliance')
ax2.legend()

# Add value labels
for i, v in enumerate(compliance_data['Compliance_Rate_%']):
    ax2.text(i, v + compliance_data['Compliance_Rate_%'].max()*0.02, f'{v:.0f}%', 
             ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('output/biometric/compliance_by_age.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/biometric/compliance_by_age.png")

print(f"\n🔍 COMPLIANCE ANALYSIS:")
for age_group, row in compliance_data.iterrows():
    print(f"\n  {age_group}:")
    print(f"    Enrolled: {row['Enrolled']:,.0f}")
    print(f"    Biometric Updates: {row['Biometric_Updates']:,.0f}")
    print(f"    Compliance Rate: {row['Compliance_Rate_%']:.1f}%")

# Identify compliance gap
mandatory_compliance = compliance_data.loc['Age 5-17 (Mandatory)', 'Compliance_Rate_%']
voluntary_compliance = compliance_data.loc['Age 18+ (Voluntary)', 'Compliance_Rate_%']

if mandatory_compliance < 100:
    gap = 100 - mandatory_compliance
    print(f"\n⚠️ COMPLIANCE GAP DETECTED:")
    print(f"  Mandatory age group (5-17) is at {mandatory_compliance:.1f}% compliance")
    print(f"  Gap: {gap:.1f} percentage points below target")
    print(f"\n💡 HYPOTHESIS: School dropouts correlate with non-compliance")
    print(f"   ACTION: Integrate biometric camps with school vaccination drives")


# =============================================================================
# ANALYSIS 2: State-Level Compliance Leaderboard
# =============================================================================
print("\n" + "="*70)
print("🏆 ANALYSIS 2: STATE COMPLIANCE LEADERBOARD")
print("="*70)

# Calculate state-wise biometric updates
state_bio = biometric_df.groupby('state')[['bio_age_5_17', 'bio_age_17_']].sum()
state_bio['total'] = state_bio.sum(axis=1)
state_bio = state_bio.sort_values('total', ascending=False)

# Top 15 states
top15_bio = state_bio.head(15)

plt.figure(figsize=(14, 9))
top15_bio['total'].plot(kind='barh', color='mediumvioletred', edgecolor='darkviolet')
plt.title('Top 15 States by Biometric Update Volume', fontsize=16, fontweight='bold')
plt.xlabel('Total Biometric Updates')
plt.ylabel('State')
plt.grid(axis='x', alpha=0.3)

for i, v in enumerate(top15_bio['total']):
    plt.text(v + top15_bio['total'].max()*0.01, i, f'{v:,.0f}', va='center')

plt.tight_layout()
plt.savefig('output/biometric/state_compliance_leaderboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/biometric/state_compliance_leaderboard.png")

print(f"\n🏆 TOP 15 STATES (Biometric Update Volume):")
for idx, (state, row) in enumerate(top15_bio.iterrows(), 1):
    print(f"  {idx}. {state}: {row['total']:,} updates")

print(f"\n💡 STRATEGIC RECOMMENDATION:")
print(f"  → Benchmark best practices from top 5 states")
print(f"  → Replicate successful campaign strategies nationwide")


# =============================================================================
# ANALYSIS 3: Lifecycle Progression Index (LPI)
# =============================================================================
print("\n" + "="*70)
print("🔄 ANALYSIS 3: LIFECYCLE PROGRESSION INDEX (LPI)")
print("="*70)
print("Question: What % of citizens complete Enroll → Demo → Bio lifecycle?")

# Load all domains for LPI calculation
enrolment_df = clean_data(load_and_combine('dataset/api_data_aadhar_enrolment_*.csv'))
demographic_df = clean_data(load_and_combine('dataset/api_data_aadhar_demographic_*.csv'))
biometric_df_reload = clean_data(load_and_combine('dataset/api_data_aadhar_biometric_*.csv'))

# Aggregate to district level
enrol_dist = enrolment_df.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
enrol_dist['total_enrol'] = enrol_dist.sum(axis=1)

demo_dist = demographic_df.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum()
demo_dist['total_demo'] = demo_dist.sum(axis=1)

bio_dist = biometric_df_reload.groupby('district')[['bio_age_5_17', 'bio_age_17_']].sum()
bio_dist['total_bio'] = bio_dist.sum(axis=1)

# Merge into single dataframe
lifecycle_df = pd.DataFrame({
    'total_enrol': enrol_dist['total_enrol'],
    'total_demo': demo_dist['total_demo'],
    'total_bio': bio_dist['total_bio']
}).fillna(0)

# Calculate LPI using advanced formula
lpi_scores = calculate_lifecycle_progression_index(lifecycle_df)

# Top and bottom performers
top_lpi = lpi_scores.nlargest(10)
bottom_lpi = lpi_scores.nsmallest(10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Top LPI districts
top_lpi.plot(kind='barh', ax=ax1, color='limegreen', edgecolor='darkgreen')
ax1.set_title('Top 10 Districts by Lifecycle Progression Index\n(Citizens Complete Full Journey)',
              fontsize=14, fontweight='bold')
ax1.set_xlabel('LPI Score')
ax1.set_ylabel('District')
ax1.axvline(x=0.5, color='red', linestyle='--', label='Healthy Threshold (0.5)')
ax1.legend()

# Bottom LPI districts
bottom_lpi.plot(kind='barh', ax=ax2, color='orangered', edgecolor='darkred')
ax2.set_title('Bottom 10 Districts by Lifecycle Progression Index\n(One-Time Enrollees)',
              fontsize=14, fontweight='bold')
ax2.set_xlabel('LPI Score')
ax2.set_ylabel('District')
ax2.axvline(x=0.1, color='orange', linestyle='--', label='Stagnant Threshold (0.1)')
ax2.legend()

plt.tight_layout()
plt.savefig('output/biometric/lifecycle_progression_index.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/biometric/lifecycle_progression_index.png")

print(f"\n🔍 LIFECYCLE PROGRESSION ANALYSIS:")
print(f"\n  🟢 TOP 5 HEALTHY ECOSYSTEMS (High LPI):")
for district, lpi in top_lpi.head(5).items():
    interpretation = interpret_lpi(lpi)
    print(f"    {district}: LPI = {lpi:.3f} - {interpretation}")

print(f"\n  🔴 BOTTOM 5 STAGNANT ECOSYSTEMS (Low LPI):")
for district, lpi in bottom_lpi.head(5).items():
    interpretation = interpret_lpi(lpi)
    print(f"    {district}: LPI = {lpi:.3f} - {interpretation}")

# National average
avg_lpi = lpi_scores.mean()
print(f"\n📊 NATIONAL AVERAGE LPI: {avg_lpi:.3f}")

if avg_lpi < 0.2:
    print(f"\n💡 CRITICAL INSIGHT:")
    print(f"  National LPI is LOW ({avg_lpi:.3f}) → Most citizens enroll but never update!")
    print(f"  ACTION: Implement re-engagement campaigns targeting enrolled-but-dormant citizens")


# =============================================================================
# ANALYSIS 4: Update Cascade Probability (UCP)
# =============================================================================
print("\n" + "="*70)
print("🎯 ANALYSIS 4: UPDATE CASCADE PROBABILITY")
print("="*70)
print("Question: What's the probability a new enrollee completes full lifecycle?")

# Calculate UCP using advanced formula
ucp_results = calculate_update_cascade_probability(lifecycle_df)

print(f"\n🔍 UPDATE CASCADE PROBABILITY METRICS:")
print(f"\n  Step 1: P(Demographic Update | Enrollment) = {ucp_results['p_demo_given_enrol']:.3f}")
print(f"  Step 2: P(Biometric Update | Demographic Update) = {ucp_results['p_bio_given_demo']:.3f}")
print(f"\n  🎯 FINAL UCP (Full Lifecycle Completion): {ucp_results['mean_ucp']:.3f} ({ucp_results['mean_ucp']*100:.1f}%)")

print(f"\n💡 INTERPRETATION:")
print(f"  Only {ucp_results['mean_ucp']*100:.1f}% of new enrollees complete the FULL lifecycle")
print(f"  (Enrollment → Demographic Update → Biometric Update)")

print(f"\n🚀 POLICY LEVER ANALYSIS:")
current_ucp = ucp_results['mean_ucp']
current_p_demo = ucp_results['p_demo_given_enrol']

# Scenario: Improve P(Demo|Enrol) by 10 percentage points
improved_p_demo = min(current_p_demo + 0.10, 1.0)
improved_ucp = improved_p_demo * ucp_results['p_bio_given_demo']
improvement = ((improved_ucp - current_ucp) / current_ucp) * 100

print(f"\n  SCENARIO: Improve P(Demo|Enrol) from {current_p_demo:.2f} to {improved_p_demo:.2f}")
print(f"  Result: UCP increases from {current_ucp:.3f} to {improved_ucp:.3f}")
print(f"  Impact: +{improvement:.1f}% increase in lifecycle completion!")

print(f"\n✅ ACTIONABLE RECOMMENDATION:")
print(f"  → Focus on improving EARLY demographic update rates")
print(f"  → Small gains in Step 1 have CASCADING effects on final completion")


# =============================================================================
# ANALYSIS 5: Temporal Biometric Update Trends
# =============================================================================
print("\n" + "="*70)
print("📈 ANALYSIS 5: TEMPORAL BIOMETRIC UPDATE TRENDS")
print("="*70)

if 'date' in biometric_df.columns:
    biometric_df['month'] = pd.to_datetime(biometric_df['date']).dt.month
    biometric_df['month_name'] = pd.to_datetime(biometric_df['date']).dt.month_name()
    
    # Monthly biometric update pattern
    monthly_bio = biometric_df.groupby('month_name')[['bio_age_5_17', 'bio_age_17_']].sum()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_bio = monthly_bio.reindex(month_order, fill_value=0)
    monthly_bio['total'] = monthly_bio.sum(axis=1)
    
    # Visualization
    fig, ax = plt.subplots(figsize=(16, 7))
    
    monthly_bio[['bio_age_5_17', 'bio_age_17_']].plot(kind='bar', stacked=True, ax=ax,
                                                        color=['lightblue', 'lightcoral'])
    ax.set_title('Monthly Biometric Update Trends (Stacked by Age Group)',
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Biometric Updates')
    ax.set_xlabel('Month')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(['Age 5-17 (Mandatory)', 'Age 18+ (Voluntary)'])
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('output/biometric/monthly_biometric_trends.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: output/biometric/monthly_biometric_trends.png")
    
    # Identify peak months
    peak_month = monthly_bio['total'].idxmax()
    peak_value = monthly_bio['total'].max()
    
    print(f"\n🔍 TEMPORAL PATTERNS:")
    print(f"  Peak Month: {peak_month} ({peak_value:,} updates)")
    print(f"  Average: {monthly_bio['total'].mean():,.0f} per month")


# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("📋 BIOMETRIC DOMAIN ANALYSIS SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED 5 ANALYSES:")
print(f"  1. Compliance Rates → Age-wise compliance gap analysis")
print(f"  2. State Leaderboard → Top performing states identified")
print(f"  3. Lifecycle Progression Index → Ecosystem health measured")
print(f"  4. Update Cascade Probability → Completion rate calculated")
print(f"  5. Temporal Trends → Monthly update patterns")

print(f"\n📊 VISUALIZATIONS GENERATED: 5 charts in 'output/biometric/'")

print(f"\n💡 KEY ACTIONABLE INSIGHTS:")
print(f"  → {(100 - mandatory_compliance):.1f}% compliance gap in mandatory age group")
print(f"  → National LPI = {avg_lpi:.3f} (most enroll but don't update)")
print(f"  → Only {ucp_results['mean_ucp']*100:.1f}% complete full lifecycle")
print(f"  → 10% improvement in early demo updates → +{improvement:.0f}% lifecycle completion")

print(f"\n🎯 STRATEGIC PRIORITIES:")
print(f"  1. Integrate biometric camps with school programs (mandatory age)")
print(f"  2. Re-engage dormant enrollees (improve LPI)")
print(f"  3. Focus on Step 1 demographic updates (cascading effect)")

print("\n" + "="*70)
print("✅ BIOMETRIC DOMAIN ANALYSIS COMPLETE")
print("="*70)
