# %%
"""
================================================================================
DOMAIN ANALYSIS: BIOMETRIC DEEP DIVE
================================================================================

PURPOSE:
--------
This module analyzes BIOMETRIC UPDATE patterns to uncover:
- Compliance rates by age cohort (mandatory at age 5 and 15)
- Cohort retention tracking (% who update over time)
- Regional compliance variations
- Lifecycle completion paths
- COMPLIANCE URGENCY (districts with overdue mandatory updates)

WHY BIOMETRIC ANALYSIS MATTERS:
-------------------------------
Biometric updates are CRITICAL for Aadhaar system integrity:
1. Mandatory at age 5 (first fingerprints mature)
2. Mandatory at age 15 (fingerprints stabilize to adult form)
3. Citizens who skip these become "dormant" and face authentication failures

This analysis helps UIDAI:
- Identify non-compliant populations
- Prioritize outreach campaigns
- Predict capacity needs for mandatory updates

ANALYSES INCLUDED:
------------------
1. Compliance Rate by Age Cohort - Who is complying with mandatory updates?
2. State Compliance Leaderboard - Which states lead in biometric updates?
3. Lifecycle Progression Index (LPI) - Are citizens completing full journey?
4. Update Cascade Probability (UCP) - What % complete enrollment→demo→bio?
5. Temporal Biometric Trends - Monthly update patterns
6. COMPLIANCE URGENCY MAP (NEW) - Districts with overdue mandatory updates

NOTEBOOK USAGE:
---------------
Each section is marked with '# %%' for Jupyter cell conversion.
Run: `jupytext --to notebook domain_biometric.py` to convert.

Author: UIDAI Hackathon 2026 Team
================================================================================
"""

# %%
# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================
# WHY these imports:
# - pandas/numpy: Core data manipulation
# - matplotlib/seaborn: Static visualizations
# - plotly: Interactive compliance urgency map

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# UTF-8 encoding for emoji support
sys.stdout.reconfigure(encoding='utf-8')

# Visualization configuration
sns.set(style="whitegrid", palette="viridis")
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 11

# Create output directory
os.makedirs('output/biometric', exist_ok=True)

print("="*70)
print("🔐 BIOMETRIC DOMAIN ANALYSIS")
print("="*70)


# %%
# =============================================================================
# INTEGRATED ADVANCED FORMULAS
# =============================================================================
# WHY EMBEDDED HERE (instead of advanced_formulas.py):
# - Self-contained module for notebook conversion
# - No external dependencies beyond standard libraries
# - Each formula includes detailed docstring for understanding

def calculate_lifecycle_progression_index(df):
    """
    Lifecycle Progression Index (LPI): Tracks citizen journey completeness.
    
    FORMULA:
    --------
    LPI = (Biometric_Updates / Enrollments) × (Demographic_Updates / Enrollments)
    
    INTERPRETATION:
    ---------------
    - LPI > 0.5 = Healthy ecosystem (citizens progress through lifecycle)
    - LPI = 0.1-0.5 = Moderate (some progression)
    - LPI < 0.1 = Stagnant (one-time enrollees, never return)
    
    WHY THIS FORMULA:
    -----------------
    Multiplying the two ratios captures the JOINT probability that a citizen
    completes BOTH demographic AND biometric updates. A low LPI means most
    citizens enroll once and never return for updates.
    
    APPLICATION:
    ------------
    Identify districts where citizens "enroll and forget" vs engaged users.
    Example: "Rural districts have LPI = 0.08 (need re-engagement campaigns)"
    """
    district_summary = df.groupby('district').agg({
        'total_enrol': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum'
    })
    
    # Avoid division by zero
    district_summary['bio_ratio'] = district_summary['total_bio'] / (district_summary['total_enrol'] + 1)
    district_summary['demo_ratio'] = district_summary['total_demo'] / (district_summary['total_enrol'] + 1)
    
    district_summary['LPI'] = district_summary['bio_ratio'] * district_summary['demo_ratio']
    
    return district_summary['LPI'].sort_values(ascending=False)


def calculate_update_cascade_probability(df):
    """
    Update Cascade Probability (UCP): Predicts full lifecycle completion rate.
    
    FORMULA:
    --------
    UCP = P(Bio_Update | Demo_Update) × P(Demo_Update | Enrollment)
    
    WHY CONDITIONAL PROBABILITY:
    ----------------------------
    This is a Markov chain approach. Each step depends on the previous:
    - You can't do biometric update without first being enrolled
    - Demographic updates often precede biometric updates
    
    The final UCP tells us: "Given a new enrollment, what's the probability
    they complete the FULL lifecycle (enrollment → demo → bio)?"
    
    INTERPRETATION:
    ---------------
    UCP = 0.12 means "12% of new enrollments complete full lifecycle"
    
    APPLICATION:
    ------------
    Policy lever identification: Improving early demo update rate has cascading effect.
    Example: "If P(Demo|Enrol) increases from 0.3 to 0.5, UCP doubles!"
    """
    district_summary = df.groupby('district').agg({
        'total_enrol': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum'
    })
    
    # Calculate conditional probabilities
    # P(Demo | Enrol) - probability of demographic update given enrollment
    p_demo_given_enrol = district_summary['total_demo'] / (district_summary['total_enrol'] + 1)
    
    # P(Bio | Demo) - probability of biometric update given demographic update
    p_bio_given_demo = district_summary['total_bio'] / (district_summary['total_demo'] + 1)
    
    # Update Cascade Probability = joint probability of completing full lifecycle
    ucp = p_demo_given_enrol * p_bio_given_demo
    
    return {
        'mean_ucp': ucp.mean(),
        'median_ucp': ucp.median(),
        'p_demo_given_enrol': p_demo_given_enrol.mean(),
        'p_bio_given_demo': p_bio_given_demo.mean(),
        'district_ucp': ucp.sort_values(ascending=False)
    }


def interpret_lpi(lpi_value):
    """Interpret Lifecycle Progression Index with emoji indicators."""
    if lpi_value > 0.5:
        return "🟢 Healthy ecosystem - Citizens complete lifecycle"
    elif lpi_value > 0.1:
        return "🟡 Moderate progression"
    else:
        return "🔴 Stagnant - One-time enrollees only"


# %%
# =============================================================================
# DATA LOADING
# =============================================================================
from analysis import load_and_combine, clean_data

biometric_df = clean_data(load_and_combine('dataset/api_data_aadhar_biometric_*.csv'))
print(f"\n📊 Loaded {len(biometric_df):,} biometric update records")


# %%
# =============================================================================
# ANALYSIS 1: Compliance Rate by Age Cohort
# =============================================================================
# WHY COMPLIANCE ANALYSIS:
# - Age 5-17 biometric updates are MANDATORY (fingerprints mature)
# - Low compliance = citizens face authentication failures later
# - High compliance gap = potential for fraud or identity mismatch

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


# %%
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


# %%
# =============================================================================
# ANALYSIS 3: Lifecycle Progression Index (LPI)
# =============================================================================
# WHY LPI:
# The LPI measures how many citizens complete the FULL Aadhaar lifecycle:
# Enrollment → Demographic Update → Biometric Update
# A low LPI indicates "enroll and forget" behavior.

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

# Calculate LPI using integrated formula
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


# %%
# =============================================================================
# ANALYSIS 4: Update Cascade Probability (UCP)
# =============================================================================
print("\n" + "="*70)
print("🎯 ANALYSIS 4: UPDATE CASCADE PROBABILITY")
print("="*70)
print("Question: What's the probability a new enrollee completes full lifecycle?")

# Calculate UCP using integrated formula
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
improvement = ((improved_ucp - current_ucp) / (current_ucp + 0.0001)) * 100

print(f"\n  SCENARIO: Improve P(Demo|Enrol) from {current_p_demo:.2f} to {improved_p_demo:.2f}")
print(f"  Result: UCP increases from {current_ucp:.3f} to {improved_ucp:.3f}")
print(f"  Impact: +{improvement:.1f}% increase in lifecycle completion!")

print(f"\n✅ ACTIONABLE RECOMMENDATION:")
print(f"  → Focus on improving EARLY demographic update rates")
print(f"  → Small gains in Step 1 have CASCADING effects on final completion")


# %%
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


# %%
# =============================================================================
# ANALYSIS 6: BIOMETRIC COMPLIANCE URGENCY MAP (NEW)
# =============================================================================
# WHY URGENCY MAP?
# -----------------
# Not all non-compliance is equal. Some districts have:
#   - Large populations of children about to hit mandatory age thresholds
#   - Historical low compliance (systemic issues)
#   - Recent enrollment surge but no corresponding biometric updates
#
# The URGENCY SCORE prioritizes districts where intervention is MOST NEEDED.
#
# FORMULA:
# --------
# Urgency_Score = (Expected_Updates - Actual_Updates) × Population_Weight
#
# Where:
#   - Expected_Updates = Enrollments in 5-17 age × 0.6 (assume 60% due)
#   - Actual_Updates = Biometric updates in 5-17 age
#   - Population_Weight = District's share of total population

print("\n" + "="*70)
print("🚨 ANALYSIS 6: BIOMETRIC COMPLIANCE URGENCY MAP")
print("="*70)
print("Question: Which districts need IMMEDIATE biometric update campaigns?")

# Calculate urgency score per district
district_enrol = enrolment_df.groupby('district')['age_5_17'].sum()
district_bio = biometric_df_reload.groupby('district')['bio_age_5_17'].sum()

# Create urgency dataframe
urgency_df = pd.DataFrame({
    'enrolled_5_17': district_enrol,
    'bio_updates_5_17': district_bio
}).fillna(0)

# Calculate expected updates (assume 60% of enrolled 5-17 should have updated by now)
urgency_df['expected_updates'] = urgency_df['enrolled_5_17'] * 0.6

# Calculate compliance gap (expected - actual)
urgency_df['compliance_gap'] = urgency_df['expected_updates'] - urgency_df['bio_updates_5_17']
urgency_df['compliance_gap'] = urgency_df['compliance_gap'].clip(lower=0)  # No negative gaps

# Calculate population weight (district's share of total)
total_enrolled = urgency_df['enrolled_5_17'].sum()
urgency_df['population_weight'] = urgency_df['enrolled_5_17'] / (total_enrolled + 1)

# URGENCY SCORE = compliance gap × population weight (normalized)
urgency_df['urgency_score'] = urgency_df['compliance_gap'] * urgency_df['population_weight'] * 100

# Calculate compliance rate for context
urgency_df['compliance_rate'] = (urgency_df['bio_updates_5_17'] / 
                                  (urgency_df['expected_updates'] + 1)) * 100

# Sort by urgency
urgency_df = urgency_df.sort_values('urgency_score', ascending=False)

# Top 15 most urgent districts
top15_urgent = urgency_df.head(15)

print(f"\n🚨 TOP 15 HIGHEST URGENCY DISTRICTS:")
print(f"   (Need immediate biometric update campaigns)")
print("-" * 70)
for idx, (district, row) in enumerate(top15_urgent.iterrows(), 1):
    print(f"  {idx:2}. {district}")
    print(f"      Enrolled (5-17): {row['enrolled_5_17']:,.0f}")
    print(f"      Bio Updates: {row['bio_updates_5_17']:,.0f}")
    print(f"      Compliance Gap: {row['compliance_gap']:,.0f} overdue")
    print(f"      Urgency Score: {row['urgency_score']:.2f}")
    print()

# Visualization: Urgency Bar Chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Top 15 by urgency score
top15_urgent['urgency_score'].plot(kind='barh', ax=ax1, 
                                    color='crimson', edgecolor='darkred')
ax1.set_title('Top 15 Districts by Compliance Urgency Score\n(IMMEDIATE ACTION NEEDED)', 
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Urgency Score')
ax1.set_ylabel('District')
ax1.grid(axis='x', alpha=0.3)

# Bottom 15 by compliance rate (lowest compliance = most urgent)
bottom15_compliance = urgency_df[urgency_df['enrolled_5_17'] > 100].nsmallest(15, 'compliance_rate')
bottom15_compliance['compliance_rate'].plot(kind='barh', ax=ax2, 
                                             color='orangered', edgecolor='darkred')
ax2.set_title('Bottom 15 Districts by Compliance Rate\n(Systemic Non-Compliance)', 
              fontsize=14, fontweight='bold')
ax2.set_xlabel('Compliance Rate (%)')
ax2.set_ylabel('District')
ax2.axvline(x=50, color='red', linestyle='--', label='50% Threshold')
ax2.legend()
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('output/biometric/compliance_urgency_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✅ Saved: output/biometric/compliance_urgency_map.png")

# Generate interactive Plotly visualization
print("\nGenerating interactive urgency visualization...")

# Prepare data for Plotly treemap (shows hierarchy and size)
urgency_viz = urgency_df.head(50).copy()
urgency_viz['district'] = urgency_viz.index
urgency_viz = urgency_viz.reset_index(drop=True)

fig = px.treemap(
    urgency_viz,
    path=['district'],
    values='compliance_gap',
    color='urgency_score',
    color_continuous_scale='Reds',
    title='Biometric Compliance Urgency Map: Districts with Overdue Updates<br><sup>Size = Compliance Gap | Color = Urgency Score</sup>'
)
fig.update_layout(
    font=dict(size=12),
    margin=dict(t=80, l=25, r=25, b=25)
)
fig.write_html('output/biometric/interactive_urgency_treemap.html')
print("✅ Saved: output/biometric/interactive_urgency_treemap.html")

# Summary statistics
total_gap = urgency_df['compliance_gap'].sum()
avg_compliance = urgency_df['compliance_rate'].mean()

print(f"\n📊 URGENCY SUMMARY:")
print(f"  Total Compliance Gap (Overdue Updates): {total_gap:,.0f}")
print(f"  Average District Compliance Rate: {avg_compliance:.1f}%")
print(f"  Districts Below 50% Compliance: {len(urgency_df[urgency_df['compliance_rate'] < 50])}")

print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
print(f"  → Deploy mobile biometric vans to top 15 urgency districts")
print(f"  → Partner with schools in low-compliance areas")
print(f"  → Use SMS reminders targeting parents of 5-17 age group")


# %%
# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("📋 BIOMETRIC DOMAIN ANALYSIS SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED 6 ANALYSES:")
print(f"  1. Compliance Rates → Age-wise compliance gap analysis")
print(f"  2. State Leaderboard → Top performing states identified")
print(f"  3. Lifecycle Progression Index → Ecosystem health measured")
print(f"  4. Update Cascade Probability → Completion rate calculated")
print(f"  5. Temporal Trends → Monthly update patterns")
print(f"  6. Compliance Urgency Map (NEW) → Priority districts identified")

print(f"\n📊 VISUALIZATIONS GENERATED: 6+ charts in 'output/biometric/'")

print(f"\n💡 KEY ACTIONABLE INSIGHTS:")
print(f"  → {(100 - mandatory_compliance):.1f}% compliance gap in mandatory age group")
print(f"  → National LPI = {avg_lpi:.3f} (most enroll but don't update)")
print(f"  → Only {ucp_results['mean_ucp']*100:.1f}% complete full lifecycle")
print(f"  → {total_gap:,.0f} citizens have overdue biometric updates")
print(f"  → 10% improvement in early demo updates → +{improvement:.0f}% lifecycle completion")

print(f"\n🎯 STRATEGIC PRIORITIES:")
print(f"  1. Integrate biometric camps with school programs (mandatory age)")
print(f"  2. Deploy mobile vans to top 15 urgency districts")
print(f"  3. Re-engage dormant enrollees (improve LPI)")
print(f"  4. Focus on Step 1 demographic updates (cascading effect)")

print("\n" + "="*70)
print("✅ BIOMETRIC DOMAIN ANALYSIS COMPLETE")
print("="*70)
