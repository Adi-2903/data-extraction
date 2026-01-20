# %%
"""
================================================================================
DOMAIN ANALYSIS: DEMOGRAPHIC DEEP DIVE
================================================================================

PURPOSE:
--------
This module analyzes DEMOGRAPHIC UPDATE patterns to uncover:
- Migration corridors (where people move)
- Seasonal movement patterns (when people move)
- Update frequency (churner analysis)
- Regional mobility trends
- Migration directionality (emigration vs immigration hubs)

WHY DEMOGRAPHIC ANALYSIS MATTERS:
---------------------------------
Demographic updates in Aadhaar represent ADDRESS CHANGES. When citizens move,
they update their address. This data reveals:
1. Rural-to-urban migration corridors
2. Seasonal labor movement (harvest seasons, festivals)
3. Industrial hub inflows (factory/construction zones)
4. Economic distress signals (mass emigration from a region)

Unlike cross-domain analysis, this focuses purely on address/data corrections
to reveal hidden population movement patterns.

ANALYSES INCLUDED:
------------------
1. Migration Corridors - Which districts receive the most movers?
2. Seasonal Migration - When do people move most?
3. Update Frequency - Which states have most mobile populations?
4. Adult vs Minor Patterns - Workforce vs family migration
5. Migration Directionality Index (MDI) - Emigration vs immigration hubs

NOTEBOOK USAGE:
---------------
Each section is marked with '# %%' for Jupyter cell conversion.
Run: `jupytext --to notebook domain_demographic.py` to convert.

Author: UIDAI Hackathon 2026 Team
================================================================================
"""

# %%
# =============================================================================
# IMPORTS AND CONFIGURATION
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# UTF-8 encoding for emoji support
sys.stdout.reconfigure(encoding='utf-8')

# Visualization configuration
sns.set(style="whitegrid", palette="coolwarm")
plt.rcParams['figure.figsize'] = (14, 7)
plt.rcParams['font.size'] = 11

# Create output directory
os.makedirs('output/demographic', exist_ok=True)

print("="*70)
print("🌍 DEMOGRAPHIC DOMAIN ANALYSIS")
print("="*70)


# %%
# =============================================================================
# INTEGRATED ADVANCED FORMULAS
# =============================================================================
# WHY EMBEDDED HERE (instead of advanced_formulas.py):
# - Self-contained module for notebook conversion
# - No external dependencies beyond standard libraries
# - Each formula includes detailed docstring for understanding

def calculate_migration_directionality_index(df):
    """
    Migration Directionality Index (MDI): Identifies emigration vs immigration hubs.
    
    FORMULA:
    --------
    MDI = (Out_Migration_Proxy - In_Migration_Proxy) / (Out_Migration_Proxy + In_Migration_Proxy)
    
    WHERE:
    ------
    - Out_Migration_Proxy = Demographic updates / Enrollments
      (High ratio means many are LEAVING - updating address to new location)
    - In_Migration_Proxy = Enrollments / Demographic updates
      (High ratio means many are ARRIVING - new enrollees but few updates yet)
    
    INTERPRETATION:
    ---------------
    - MDI > +0.5 = Strong emigration source (people leaving)
    - MDI ≈ 0 = Balanced (similar in/out flows)
    - MDI < -0.5 = Strong immigration destination (people arriving)
    
    WHY THIS MATTERS:
    -----------------
    - Emigration sources: May indicate economic distress, need retention programs
    - Immigration hubs: Need scaled-up demographic update center capacity
    
    APPLICATION:
    ------------
    Target resource deployment to immigration hubs, retention in emigration sources.
    Example: "Delhi has MDI = -0.82 (massive immigration sink)"
    """
    district_summary = df.groupby('district').agg({
        'total_enrol': 'sum',
        'total_demo': 'sum'
    })
    
    # Proxy: High demo + Low enrol = Out-migration (updating address to new location)
    #        Low demo + High enrol = In-migration (new arrivals enrolling)
    
    out_migration_proxy = district_summary['total_demo'] / (district_summary['total_enrol'] + 1)
    in_migration_proxy = district_summary['total_enrol'] / (district_summary['total_demo'] + 1)
    
    # Normalize and calculate MDI
    mdi = (out_migration_proxy - in_migration_proxy) / (out_migration_proxy + in_migration_proxy + 0.001)
    
    return mdi.sort_values(ascending=False)


def interpret_mdi(mdi_value):
    """Interpret Migration Directionality Index with emoji indicators."""
    if mdi_value > 0.5:
        return "🔴 Strong emigration source - People leaving"
    elif mdi_value > 0:
        return "🟡 Slight emigration tendency"
    elif mdi_value > -0.5:
        return "🟡 Slight immigration tendency"
    else:
        return "🟢 Strong immigration destination - People arriving"


# %%
# =============================================================================
# DATA LOADING
# =============================================================================
from analysis import load_and_combine, clean_data

demographic_df = clean_data(load_and_combine('dataset/api_data_aadhar_demographic_*.csv'))
print(f"\n📊 Loaded {len(demographic_df):,} demographic update records")


# %%
# =============================================================================
# ANALYSIS 1: Migration Corridor Identification
# =============================================================================
# WHY MIGRATION CORRIDORS:
# Districts with HIGH demographic updates are receiving movers from elsewhere.
# These are "immigration hubs" - likely urban centers or industrial zones.
# Understanding corridors helps UIDAI pre-position resources.

print("\n" + "="*70)
print("🚂 ANALYSIS 1: MIGRATION CORRIDORS")
print("="*70)
print("Question: Which district pairs have strongest migration flows?")

# Calculate district-level update volume
district_updates = demographic_df.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum()
district_updates['total'] = district_updates.sum(axis=1)
district_updates = district_updates.sort_values('total', ascending=False)

# Top immigration destinations (high demographic updates)
top_destinations = district_updates.head(10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Top 10 update hubs
top_destinations['total'].plot(kind='barh', ax=ax1, color='coral', edgecolor='darkred')
ax1.set_title('Top 10 Migration Destination Districts\n(High Demographic Update Volume)', 
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Total Demographic Updates')
ax1.set_ylabel('District')
for i, v in enumerate(top_destinations['total']):
    ax1.text(v + top_destinations['total'].max()*0.01, i, f'{v:,.0f}', va='center')

# Age-wise breakdown for visualizations
age_comparison = top_destinations[['demo_age_5_17', 'demo_age_17_']].head(5)
age_comparison.plot(kind='bar', ax=ax2, stacked=False)
ax2.set_title('Age Distribution in Top 5 Migration Hubs', fontsize=14, fontweight='bold')
ax2.set_ylabel('Demographic Updates')
ax2.set_xlabel('District')
ax2.legend(['Age 5-17', 'Age 18+'])
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('output/demographic/migration_corridors.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/demographic/migration_corridors.png")

print(f"\n🔍 TOP 10 MIGRATION DESTINATION DISTRICTS:")
for idx, (district, row) in enumerate(top_destinations.iterrows(), 1):
    total_updates = row['total']
    adult_ratio = (row['demo_age_17_'] / total_updates) * 100 if total_updates > 0 else 0
    print(f"  {idx}. {district}: {total_updates:,} updates ({adult_ratio:.1f}% adults)")

# Calculate migration concentration
total_updates = district_updates['total'].sum()
top10_share = (top_destinations['total'].sum() / total_updates) * 100

print(f"\n📊 MIGRATION CONCENTRATION:")
print(f"  Top 10 districts handle {top10_share:.1f}% of all demographic updates")

if top10_share > 40:
    print(f"\n💡 INSIGHT: Migration is HIGHLY CONCENTRATED")
    print(f"   Recommendation: Deploy dedicated demographic update centers in top 10")


# %%
# =============================================================================
# ANALYSIS 2: Seasonal Migration Waves
# =============================================================================
# WHY SEASONAL ANALYSIS:
# Migration in India has strong seasonal patterns:
# - Post-harvest (Oct-Dec): Rural workers move to cities
# - Festival seasons: Return migration to villages
# - Academic year start: Student migration

print("\n" + "="*70)
print("📅 ANALYSIS 2: SEASONAL MIGRATION PATTERNS")
print("="*70)
print("Question: When do people move? Are there seasonal waves?")

if 'date' in demographic_df.columns:
    demographic_df['month'] = pd.to_datetime(demographic_df['date']).dt.month
    demographic_df['month_name'] = pd.to_datetime(demographic_df['date']).dt.month_name()
    
    # Monthly demographic update pattern
    monthly_updates = demographic_df.groupby('month_name')[['demo_age_5_17', 'demo_age_17_']].sum()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_updates = monthly_updates.reindex(month_order, fill_value=0)
    monthly_updates['total'] = monthly_updates.sum(axis=1)
    
    # Visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    # Total trend
    monthly_updates['total'].plot(kind='bar', ax=ax1, color='steelblue', edgecolor='navy')
    ax1.set_title('Demographic Updates by Month (Total)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Total Updates')
    ax1.set_xlabel('Month')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    ax1.axhline(y=monthly_updates['total'].mean(), color='red', linestyle='--', 
                label=f'Average: {monthly_updates["total"].mean():,.0f}')
    ax1.legend()
    
    # Stacked age distribution
    monthly_updates[['demo_age_5_17', 'demo_age_17_']].plot(kind='bar', stacked=True, ax=ax2, 
                                                              color=['lightgreen', 'lightcoral'])
    ax2.set_title('Demographic Updates by Age Group', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Updates')
    ax2.set_xlabel('Month')
    ax2.tick_params(axis='x', rotation=45)
    ax2.legend(['Age 5-17', 'Age 18+'])
    
    plt.tight_layout()
    plt.savefig('output/demographic/seasonal_migration.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: output/demographic/seasonal_migration.png")
    
    # Identify peak months
    peak_month = monthly_updates['total'].idxmax()
    peak_value = monthly_updates['total'].max()
    avg_value = monthly_updates['total'].mean()
    
    print(f"\n🔍 SEASONAL PATTERNS:")
    print(f"  Peak Month: {peak_month} ({peak_value:,} updates)")
    print(f"  Average per month: {avg_value:,.0f}")
    print(f"  Peak is {((peak_value/avg_value)-1)*100:.1f}% above average")
    
    # Identify seasonal clusters (post-harvest hypothesis)
    harvest_months = ['October', 'November', 'December']
    harvest_updates = monthly_updates.loc[harvest_months, 'total'].sum()
    harvest_pct = (harvest_updates / monthly_updates['total'].sum()) * 100
    
    if harvest_pct > 30:
        print(f"\n💡 INSIGHT: Oct-Nov-Dec account for {harvest_pct:.1f}% of updates")
        print(f"   HYPOTHESIS: Post-harvest rural-to-urban migration wave")
        print(f"   ACTION: Pre-position mobile update centers in Oct in urban hubs")


# %%
# =============================================================================
# ANALYSIS 3: Update Frequency (Churner Analysis)
# =============================================================================
print("\n" + "="*70)
print("🔄 ANALYSIS 3: UPDATE FREQUENCY & CHURNERS")
print("="*70)
print("Question: Which districts have high re-update rates (mobile populations)?")

# Calculate update intensity (proxy for population mobility)
state_updates = demographic_df.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum()
state_updates['total'] = state_updates.sum(axis=1)
state_updates = state_updates.sort_values('total', ascending=False)

# Top 15 states
top15_states = state_updates.head(15)

plt.figure(figsize=(14, 8))
top15_states['total'].plot(kind='barh', color='mediumseagreen', edgecolor='darkgreen')
plt.title('Top 15 States by Demographic Update Volume\n(Proxy for Population Mobility)',
          fontsize=16, fontweight='bold')
plt.xlabel('Total Demographic Updates')
plt.ylabel('State')
plt.grid(axis='x', alpha=0.3)

for i, v in enumerate(top15_states['total']):
    plt.text(v + top15_states['total'].max()*0.01, i, f'{v:,.0f}', va='center')

plt.tight_layout()
plt.savefig('output/demographic/update_frequency_states.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/demographic/update_frequency_states.png")

print(f"\n🔍 TOP 15 MOBILE STATES (High Update Frequency):")
for idx, (state, row) in enumerate(top15_states.iterrows(), 1):
    print(f"  {idx}. {state}: {row['total']:,} updates")

print(f"\n💡 INTERPRETATION:")
print(f"  States with high demographic updates likely have:")
print(f"    → High workforce mobility (migrant workers)")
print(f"    → Urban centers (people arriving from rural areas)")
print(f"    → Industrial zones (factory/construction hubs)")


# %%
# =============================================================================
# ANALYSIS 4: Adult vs Minor Update Patterns
# =============================================================================
# WHY ADULT VS MINOR:
# - Adult-dominated updates = workforce migration
# - Minor-included updates = family migration (more permanent)
# This helps distinguish temporary labor vs permanent resettlement.

print("\n" + "="*70)
print("👨‍👩‍👧‍👦 ANALYSIS 4: ADULT VS MINOR UPDATE PATTERNS")
print("="*70)

# Calculate adult vs minor ratio
state_updates['adult_ratio'] = (state_updates['demo_age_17_'] / 
                                 (state_updates['total'] + 1)) * 100

state_updates_sorted = state_updates.sort_values('adult_ratio', ascending=False).head(10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Adult ratio comparison
state_updates_sorted['adult_ratio'].plot(kind='barh', ax=ax1, color='purple', edgecolor='darkviolet')
ax1.set_title('Top 10 States by Adult Update Ratio\n(% of updates from 18+ age group)',
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Adult Update Percentage (%)')
ax1.set_ylabel('State')
ax1.axvline(x=50, color='red', linestyle='--', label='50% threshold')
ax1.legend()

for i, v in enumerate(state_updates_sorted['adult_ratio']):
    ax1.text(v + 1, i, f'{v:.1f}%', va='center')

# Absolute numbers comparison
top5_compare = state_updates.head(5)[['demo_age_5_17', 'demo_age_17_']]
top5_compare.plot(kind='bar', ax=ax2)
ax2.set_title('Age Distribution in Top 5 Update States', fontsize=14, fontweight='bold')
ax2.set_ylabel('Updates')
ax2.set_xlabel('State')
ax2.legend(['Age 5-17', 'Age 18+'])
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('output/demographic/adult_vs_minor_updates.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/demographic/adult_vs_minor_updates.png")

print(f"\n🔍 ADULT UPDATE RATIO ANALYSIS:")
avg_adult_ratio = state_updates['adult_ratio'].mean()
print(f"  National Average: {avg_adult_ratio:.1f}% adults")

for state, row in state_updates_sorted.head(5).iterrows():
    print(f"  {state}: {row['adult_ratio']:.1f}% adults")

print(f"\n💡 INSIGHT:")
if state_updates_sorted['adult_ratio'].iloc[0] > 70:
    print(f"  High adult ratio (>70%) suggests workforce migration")
    print(f"  ACTION: Focus on employment-linked demographic update incentives")


# %%
# =============================================================================
# ANALYSIS 5: Migration Directionality Index (MDI)
# =============================================================================
# WHY MDI:
# Simple update counts don't tell us DIRECTION of migration.
# MDI compares enrollments (new arrivals) vs demographic updates (address changes)
# to determine if a district is a SOURCE (people leaving) or SINK (people arriving).

print("\n" + "="*70)
print("↔️ ANALYSIS 5: MIGRATION DIRECTIONALITY INDEX (MDI)")
print("="*70)
print("Question: Which districts are emigration sources vs immigration destinations?")

# Load enrollment data for MDI calculation
enrolment_df = clean_data(load_and_combine('dataset/api_data_aadhar_enrolment_*.csv'))

# Merge enrollment and demographic for MDI
enrol_by_district = enrolment_df.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
enrol_by_district['total_enrol'] = enrol_by_district.sum(axis=1)

demo_by_district = demographic_df.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum()
demo_by_district['total_demo'] = demo_by_district.sum(axis=1)

mdi_data = pd.merge(enrol_by_district[['total_enrol']], demo_by_district[['total_demo']], 
                    left_index=True, right_index=True, how='outer').fillna(0)

# Calculate MDI using integrated formula
mdi_scores = calculate_migration_directionality_index(mdi_data)

# Top emigration sources (positive MDI)
emigration_sources = mdi_scores.nlargest(10)

# Top immigration destinations (negative MDI)
immigration_destinations = mdi_scores.nsmallest(10)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# Emigration sources
emigration_sources.plot(kind='barh', ax=ax1, color='indianred', edgecolor='darkred')
ax1.set_title('Top 10 Emigration Source Districts\n(MDI > 0: People Leaving)',
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Migration Directionality Index')
ax1.set_ylabel('District')
ax1.axvline(x=0, color='black', linestyle='-', linewidth=2)

# Immigration destinations
immigration_destinations.plot(kind='barh', ax=ax2, color='dodgerblue', edgecolor='darkblue')
ax2.set_title('Top 10 Immigration Destination Districts\n(MDI < 0: People Arriving)',
              fontsize=14, fontweight='bold')
ax2.set_xlabel('Migration Directionality Index')
ax2.set_ylabel('District')
ax2.axvline(x=0, color='black', linestyle='-', linewidth=2)

plt.tight_layout()
plt.savefig('output/demographic/migration_directionality.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Saved: output/demographic/migration_directionality.png")

print(f"\n🔍 MIGRATION FLOW ANALYSIS:")
print(f"\n  🔴 TOP 5 EMIGRATION SOURCES (People Leaving):")
for district, mdi in emigration_sources.head(5).items():
    interpretation = interpret_mdi(mdi)
    print(f"    {district}: MDI = {mdi:+.3f} - {interpretation}")

print(f"\n  🔵 TOP 5 IMMIGRATION DESTINATIONS (People Arriving):")
for district, mdi in immigration_destinations.head(5).items():
    interpretation = interpret_mdi(mdi)
    print(f"    {district}: MDI = {mdi:+.3f} - {interpretation}")

print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
print(f"  → Emigration Sources: Deploy retention programs, improve local economy")
print(f"  → Immigration Destinations: Scale demographic update center capacity")


# %%
# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("📋 DEMOGRAPHIC DOMAIN ANALYSIS SUMMARY")
print("="*70)

print(f"\n✅ COMPLETED 5 ANALYSES:")
print(f"  1. Migration Corridors → Top destination districts identified")
print(f"  2. Seasonal Patterns → Identified peak migration months")
print(f"  3. Update Frequency → High-mobility states ranked")
print(f"  4. Adult vs Minor → Workforce migration patterns")
print(f"  5. Migration Directionality → Emigration vs immigration districts")

print(f"\n📊 VISUALIZATIONS GENERATED: 5 charts in 'output/demographic/'")

print(f"\n💡 KEY ACTIONABLE INSIGHTS:")
print(f"  → Pre-position mobile centers in Oct-Nov (harvest migration)")
print(f"  → Deploy dedicated centers in top 10 migration destinations")
print(f"  → Focus workforce programs in high adult-update states")
print(f"  → Implement retention in emigration source districts")

print("\n" + "="*70)
print("✅ DEMOGRAPHIC DOMAIN ANALYSIS COMPLETE")
print("="*70)
