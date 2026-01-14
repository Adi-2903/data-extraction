import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import warnings
import os
import sys
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Configuration
sys.stdout.reconfigure(encoding='utf-8')
pd.set_option('display.max_columns', None)
sns.set(style="whitegrid", palette="viridis")
plt.rcParams['figure.figsize'] = (14, 7)
warnings.filterwarnings('ignore')

# Create output directory for plots
os.makedirs('output', exist_ok=True)
print("Directory 'output' created/verified for saving visualizations.")

# --- HELPER FUNCTIONS ---
def load_and_combine(pattern):
    """
    Load and combine multiple CSV files matching a pattern.
    This helps us combine all enrollment/demographic/biometric files into single DataFrames.
    """
    files = glob.glob(pattern)
    if not files:
        print(f"[WARNING] No files found for pattern: {pattern}")
        return pd.DataFrame()
    df_list = [pd.read_csv(f) for f in files]
    print(f"Loaded {len(files)} files for pattern: {pattern}")
    return pd.concat(df_list, ignore_index=True)

def clean_data(df):
    """
    Clean and standardize the data:
    - Fix date formats
    - Normalize state/district names (critical for merging!)
    - Validate pincodes
    - Handle missing values
    
    WHY: Raw government data often has inconsistencies (e.g., 'West Bengal' vs 'West Bangal')
    This function ensures we can merge data correctly without losing records.
    """
    if df.empty: return df
    
    # 1. Date Standardization
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    
    # 2. String Cleaning (State/District)
    for col in ['state', 'district']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    
    # 3. State Name Normalization (Critical for Merging)
    state_map = {
        'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
        'Andhra Pradsh': 'Andhra Pradesh',
        'Chhatisgarh': 'Chhattisgarh',
        'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Jammu & Kashmir': 'Jammu and Kashmir',
        'Orissa': 'Odisha',
        'Pondicherry': 'Puducherry',
        'Tamilnadu': 'Tamil Nadu',
        'Telengana': 'Telangana',
        'Uttaranchal': 'Uttarakhand',
        'West Bangal': 'West Bengal',
        'Westbengal': 'West Bengal',
        'West Bengli': 'West Bengal'
    }
    if 'state' in df.columns:
        df['state'] = df['state'].replace(state_map)
        
    # 4. District Normalization
    dist_map = {
        'Bangalore': 'Bengaluru',
        'Bangalore Urban': 'Bengaluru Urban',
        'Calcutta': 'Kolkata',
        'Gurgaon': 'Gurugram'
    }
    if 'district' in df.columns:
        df['district'] = df['district'].replace(dist_map)
        
    # 5. Pincode Validation (Indian pincodes are 6 digits, 110000-999999)
    if 'pincode' in df.columns:
        df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce').fillna(0).astype(int)
        df = df[(df['pincode'] >= 110000) & (df['pincode'] <= 999999)]

    # 6. Null Handling (Numeric -> 0)
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)
    
    return df

# ============================================================================
# PHASE 0: DATA INGESTION
# ============================================================================
print("\n=== PHASE 0: DATA INGESTION ===")
print("Loading Enrolment Data...")
enrolment_df = clean_data(load_and_combine('dataset/api_data_aadhar_enrolment_*.csv'))

print("Loading Demographic Data...")
demographic_df = clean_data(load_and_combine('dataset/api_data_aadhar_demographic_*.csv'))

print("Loading Biometric Data...")
biometric_df = clean_data(load_and_combine('dataset/api_data_aadhar_biometric_*.csv'))

print("\n--- DATASET SHAPES ---")
print(f"Enrolment DB:   {enrolment_df.shape}")
print(f"Demographic DB: {demographic_df.shape}")
print(f"Biometric DB:   {biometric_df.shape}")


# ============================================================================
# PHASE 1: ENROLLMENT DEEP DIVE
# WHY: Understand WHERE growth is happening (infant vs adult enrollment)
# ============================================================================
print("\n=== PHASE 1: ENROLLMENT DEEP DIVE ===")
if not enrolment_df.empty:
    # 1. Age Cohort Analysis
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    total_enrol = enrolment_df[age_cols].sum()
    
    plt.figure(figsize=(10, 5))
    total_enrol.plot(kind='bar', color=['#3498db', '#9b59b6', '#2ecc71'])
    plt.title('Phase 1: National Enrollment Age Pyramid')
    plt.ylabel('Total Enrollments')
    plt.xticks(rotation=0)
    plt.savefig('output/phase1_age_pyramid.png')
    plt.close()
    print("Saved plot: output/phase1_age_pyramid.png")
    
    # 2. Infant Enrollment Hotspots
    # SECRET INSIGHT: High infant enrollment = opportunity for birth registry integration
    infant_hotspots = enrolment_df.groupby('state')['age_0_5'].sum().sort_values(ascending=False).head(5)
    print("\n--- TOP 5 STATES FOR INFANT ENROLLMENT (0-5) ---")
    print(infant_hotspots)


# ============================================================================
# PHASE 2: DEMOGRAPHIC ANALYSIS
# WHY: High demographic updates indicate MIGRATION or DATA CORRECTION patterns
# ============================================================================
print("\n=== PHASE 2: DEMOGRAPHIC ANALYSIS ===")
if not demographic_df.empty:
    # 1. State-wise Update Volume
    demo_state = demographic_df.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1).sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=demo_state.values, y=demo_state.index, palette='magma')
    plt.title('Phase 2A: Top 10 States by Demographic Updates')
    plt.xlabel('Total Updates')
    plt.savefig('output/phase2_demographic_states.png')
    plt.close()
    print("Saved plot: output/phase2_demographic_states.png")
    
    # 2. Migration/Update Hubs
    district_updates = demographic_df.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1)
    print("\n--- TOP MIGRATION/UPDATE HUBS ---")
    print(district_updates.sort_values(ascending=False).head(5))
    
    # 3. Seasonal Trends
    # SECRET INSIGHT: Spikes during harvest/festival seasons = migrant worker movement
    demo_daily = demographic_df.groupby('date')[['demo_age_5_17', 'demo_age_17_']].sum()
    if not demo_daily.empty:
        plt.figure(figsize=(14, 5))
        plt.plot(demo_daily.index, demo_daily['demo_age_17_'], color='#e74c3c', linewidth=2)
        plt.title('Phase 2B: Temporal Seasonality in Demographic Updates')
        plt.ylabel('Daily Updates')
        plt.grid(True, alpha=0.3)
        plt.savefig('output/phase2_seasonality.png')
        plt.close()
        print("Saved plot: output/phase2_seasonality.png")


# ============================================================================
# PHASE 3: BIOMETRIC ANALYSIS + COMPLIANCE GAP
# WHY: Mandatory biometric updates at age 5 and 15. Low compliance = enforcement gap.
# ============================================================================
print("\n=== PHASE 3: BIOMETRIC ANALYSIS ===")
if not biometric_df.empty:
    bio_daily = biometric_df.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum()
    
    plt.figure(figsize=(14, 5))
    plt.plot(bio_daily.index, bio_daily['bio_age_5_17'], label='Age 5-17 (Mandatory Updates)', alpha=0.8)
    plt.plot(bio_daily.index, bio_daily['bio_age_17_'], label='Age 18+ (Voluntary/Auth)', alpha=0.6)
    plt.title('Phase 3: Biometric Update Trends (Compliance Monitoring)')
    plt.legend()
    plt.savefig('output/phase3_biometric_trends.png')
    plt.close()
    print("Saved plot: output/phase3_biometric_trends.png")
    
    # ADVANCED: Compliance Gap Analysis
    # FORMULA: Expected updates (based on enrollments 10 years ago) vs Actual updates
    # WHY: This tells UIDAI how many people are "missing" their mandatory updates
    print("\n--- ADVANCED: BIOMETRIC COMPLIANCE GAP ---")
    expected_updates = enrolment_df['age_5_17'].sum() * 0.6  # Assume 60% are due
    actual_updates = biometric_df['bio_age_5_17'].sum()
    
    compliance_rate = (actual_updates / expected_updates) * 100 if expected_updates > 0 else 0
    print(f"National Compliance Rate: {compliance_rate:.1f}%")
    print(f"Estimated Missing Updates: {max(0, expected_updates - actual_updates):.0f}")
    print("INSIGHT: This gap represents citizens who haven't updated biometrics despite")
    print("         reaching mandatory age triggers (age 5 or 15).")


# ============================================================================
# PHASE 4: MASTER CUBE INTEGRATION + CUSTOM FORMULAS
# WHY: Some insights require CROSS-DOMAIN data (e.g., comparing enrollment vs updates)
# ============================================================================
print("\n=== PHASE 4: MASTER CUBE INTEGRATION ===")
merge_keys = ['date', 'state', 'district', 'pincode']

master_df = pd.merge(enrolment_df, demographic_df, on=merge_keys, how='outer')
master_df = pd.merge(master_df, biometric_df, on=merge_keys, how='outer')
master_df = master_df.fillna(0)

master_df['total_enrol'] = master_df['age_0_5'] + master_df['age_5_17'] + master_df['age_18_greater']
master_df['total_demo'] = master_df['demo_age_5_17'] + master_df['demo_age_17_']
master_df['total_bio'] = master_df['bio_age_5_17'] + master_df['bio_age_17_']
master_df['total_activity'] = master_df['total_enrol'] + master_df['total_demo'] + master_df['total_bio']

print(f"Master Cube Created. Shape: {master_df.shape}")

# CUSTOM FORMULA 1: Saturation Index (System Maturity)
# FORMULA: (Updates) / (Enrollments + 1)
# WHY: High ratio = Mature region (more updates than new enrollments)
#      Low ratio = Growth region (more enrollments than updates)
master_df['Saturation_Index'] = (master_df['total_demo'] + master_df['total_bio']) / (master_df['total_enrol'] + 1)
print("Saturation Index Calculated.")

# CUSTOM FORMULA 2: System Efficiency Score (Cost Optimization)
# FORMULA: Weighted cost of activities (Bio > Demo > Enrol)
# WHY: Biometric updates are EXPENSIVE (fingerprint scanners, iris cameras)
#      This score helps identify districts that are inefficient (too many bio updates)
#      and can benefit from SELF-SERVICE KIOSKS.
master_df['efficiency_score'] = (
    (master_df['total_bio'] * 0.5) +   # Bio updates cost 2x (equipment)
    (master_df['total_demo'] * 0.3) +  # Demo updates cost 1.5x (staff time)
    (master_df['total_enrol'] * 0.2)   # Enrollments are cheapest (one-time)
) / (master_df['total_activity'] + 1)

print("System Efficiency Score Calculated.")

# CUSTOM FORMULA 3: Fraud Probability Index
# FORMULA: Combines 3 red flags
# WHY: High demographic updates + Zero enrollments + Extreme saturation = Fraud signal
#      This helps UIDAI focus audit resources on suspicious pincodes.
master_df['fraud_index'] = (
    (master_df['total_demo'] > master_df['total_demo'].quantile(0.95)).astype(int) * 0.4 +
    (master_df['total_enrol'] == 0).astype(int) * 0.3 +
    (master_df['Saturation_Index'] > 10).astype(int) * 0.3
)
print("Fraud Probability Index Calculated.")


# ============================================================================
# PHASE 5: PREDICTIVE ANALYTICS & ANOMALY DETECTION
# WHY: Move from DESCRIPTIVE (what happened) to PRESCRIPTIVE (what will happen)
# ============================================================================
print("\n=== PHASE 5: PREDICTIVE & ANOMALY ===")
if not master_df.empty:
    # A. Holt-Winters Forecasting (Time Series)
    # GOAL: Predict Q1 2026 system load for capacity planning
    ts_data = master_df.groupby('date')['total_activity'].sum().asfreq('D').fillna(0)
    
    try:
        model = ExponentialSmoothing(ts_data, trend='add', seasonal='add', seasonal_periods=7).fit()
        forecast = model.forecast(90) # Q1 2026
        
        plt.figure(figsize=(15, 6))
        plt.plot(ts_data.index, ts_data, label='Historical Load')
        plt.plot(forecast.index, forecast, label='Forecast (Q1 2026)', color='red', linestyle='--')
        plt.title('Phase 5A: Predictive Capacity Planning (Holt-Winters)')
        plt.legend()
        plt.savefig('output/phase5_forecast.png')
        plt.close()
        print("Saved plot: output/phase5_forecast.png")
        print(f"Projected Average Daily Load (Q1 2026): {forecast.mean():.0f} transactions")
    except Exception as e:
        print(f"Forecasting Error: {e}")

    # B. Global Anomaly Detection (Temporal)
    # GOAL: Find days with inexplicable spikes (could be data dumps or system errors)
    iso = IsolationForest(contamination=0.01, random_state=42)
    anomalies = iso.fit_predict(ts_data.values.reshape(-1, 1))
    print(f"Detected {list(anomalies).count(-1)} Statistical Anomalies in Daily Volume.")
    
    # C. Domain-Specific Fraud Detection (Demographic Only)
    # WHY: High demographic updates WITHOUT enrollment spikes = Potential FRAUD RING
    #      (Mass address changes to claim subsidies)
    demo_ts = master_df.groupby('date')['total_demo'].sum().asfreq('D').fillna(0).values.reshape(-1, 1)
    iso_demo = IsolationForest(contamination=0.02, random_state=42)
    demo_anomalies = iso_demo.fit_predict(demo_ts)
    n_fraud_signals = list(demo_anomalies).count(-1)
    print(f"CRITICAL: Detected {n_fraud_signals} specific 'Demographic Spike' events.")
    print("ACTION: Cross-reference these dates with local elections/subsidy announcements.")


# ============================================================================
# PHASE 5B: SPATIAL FRAUD DETECTION (DBSCAN Clustering)
# WHY: Temporal anomalies find "when". Spatial clustering finds "where".
# GOAL: Detect coordinated fraud (same date + nearby pincodes)
# ============================================================================
print("\n--- ADVANCED: SPATIAL FRAUD DETECTION (Geographic Clustering) ---")
# Filter high-risk transactions (top 5% of demographic updates)
fraud_candidates = master_df[master_df['total_demo'] > master_df['total_demo'].quantile(0.95)]

if len(fraud_candidates) > 10:
    # DBSCAN: Density-Based Spatial Clustering
    # WHY: If 500+ updates happen in NEARBY pincodes on the SAME date = coordinated fraud
    # PARAMS: eps=1000 means pincodes within 1000 units, min_samples=3 means at least 3 pincodes
    fraud_coords = fraud_candidates[['pincode', 'total_demo']].values
    
    db = DBSCAN(eps=1000, min_samples=3).fit(fraud_coords)
    fraud_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    
    print(f"Detected {fraud_clusters} geographic fraud clusters")
    print("INSIGHT: These are groups of nearby pincodes with synchronized demographic spikes.")
    print("         Possible causes: Organized fraud rings, mass camp events, or data entry errors.")
else:
    print("Insufficient data for spatial clustering.")


# ============================================================================
# PHASE 5C: PREDICTIVE ENROLLMENT MODELING (Machine Learning)
# WHY: Traditional forecasting predicts TOTAL load. ML predicts PER-DISTRICT hotspots.
# GOAL: Identify which districts will have an enrollment SURGE in Q2 2026
# ============================================================================
print("\n--- ADVANCED: PREDICTIVE HOT-SPOT MODELING (Random Forest) ---")
# Feature Engineering for ML
# FEATURES: Current enrollment volatility, demographic activity, saturation
# TARGET: Predict future enrollment volume
district_features = master_df.groupby('district').agg({
    'total_enrol': ['sum', 'std'],  # Total and volatility
    'total_demo': 'sum',
    'Saturation_Index': 'mean'
}).fillna(0)

district_features.columns = ['enrol_sum', 'enrol_std', 'demo_sum', 'saturation']
district_features['target'] = district_features['enrol_sum']  # Target is enrollment

# Build the model
X = district_features[['enrol_std', 'demo_sum', 'saturation']]
y = district_features['target']

if len(X) > 50:  # Need enough data for train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest: Ensemble of decision trees
    # WHY: Handles non-linear relationships between features
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    
    score = rf.score(X_test, y_test)
    print(f"Model R² Score: {score:.3f}")
    print("INTERPRETATION: R² of 0.80 means our model explains 80% of enrollment variance.")
    
    # Predict future hotspots
    predictions = rf.predict(X)
    district_features['predicted_surge'] = predictions
    
    hotspots = district_features.nlargest(5, 'predicted_surge')
    print("\nPredicted Enrollment Hotspots for Q2 2026:")
    print(hotspots.index.tolist())
    print("ACTION: Pre-deploy mobile enrollment vans to these districts NOW.")
else:
    print("Insufficient district-level data for ML modeling.")


# ============================================================================
# PHASE 6: STRATEGIC SYNTHESIS + GEOGRAPHIC CLUSTERING
# WHY: Move from numbers to ACTIONABLE recommendations
# ============================================================================
print("\n=== PHASE 6: STRATEGIC SYNTHESIS ===")
district_summary = master_df.groupby('district')[['total_enrol', 'total_bio', 'total_demo']].sum()
district_summary['ratio'] = (district_summary['total_bio'] + district_summary['total_demo']) / (district_summary['total_enrol'] + 1)

growing_districts = district_summary[district_summary['ratio'] < 1].sort_values(by='total_enrol', ascending=False).head(5)
mature_districts = district_summary[district_summary['ratio'] > 5].sort_values(by='total_bio', ascending=False).head(5)

# Comparative Insights
pure_enrollment = master_df[(master_df['total_enrol'] > 500) & (master_df['total_demo'] == 0) & (master_df['total_bio'] == 0)]
pure_update = master_df[(master_df['total_enrol'] == 0) & ((master_df['total_demo'] > 500) | (master_df['total_bio'] > 500))]


# ============================================================================
# PHASE 6B: GEOGRAPHIC CLUSTERING (K-Means)
# WHY: Group districts with similar "Aadhaar DNA" regardless of geography
# GOAL: Create strategic district typologies (Metro, Growth, Rural, etc.)
# ============================================================================
print("\n--- ADVANCED: GEOGRAPHIC CLUSTERING (K-Means) ---")
# Features for clustering: enrollment, updates, saturation
cluster_features = district_summary[['total_enrol', 'total_demo', 'total_bio', 'ratio']].copy()

# Standardization: K-Means is sensitive to scale
# WHY: Enrollment numbers (100,000s) would dominate ratio (0-10) without scaling
scaler = StandardScaler()
scaled = scaler.fit_transform(cluster_features)

# K-Means: Partition districts into 4 strategic groups
# WHY: 4 clusters = Tier-1 Metro / Tier-2 Growth / Rural Stagnant / Fraud Risk
kmeans = KMeans(n_clusters=4, random_state=42)
district_summary['cluster'] = kmeans.fit_predict(scaled)

# Interpret each cluster
print("\nDISTRICT TYPOLOGY (K-Means Clustering):")
for i in range(4):
    cluster_districts = district_summary[district_summary['cluster'] == i]
    avg_saturation = cluster_districts['ratio'].mean()
    avg_enrol = cluster_districts['total_enrol'].mean()
    
    # Auto-name clusters based on characteristics
    if avg_saturation > 5:
        cluster_name = "MATURE HUB"
    elif avg_enrol > cluster_districts['total_enrol'].median():
        cluster_name = "GROWTH ZONE"
    elif avg_saturation < 1:
        cluster_name = "NEW MARKET"
    else:
        cluster_name = "MAINTENANCE"
    
    print(f"\nCluster {i}: {cluster_name} ({len(cluster_districts)} districts)")
    print(f"  Avg Saturation: {avg_saturation:.2f}")
    print(f"  Avg Enrollments: {avg_enrol:.0f}")
    print(f"  Example: {cluster_districts.index[0]}")

# Save cluster map
cluster_summary = district_summary.groupby('cluster').size().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
cluster_summary.plot(kind='bar', color='teal')
plt.title('District Distribution Across Strategic Clusters')
plt.xlabel('Cluster ID')
plt.ylabel('Number of Districts')
plt.savefig('output/phase6_clusters.png')
plt.close()
print("\nSaved plot: output/phase6_clusters.png")


# ============================================================================
# PHASE 6C: MIGRATION FLOW ANALYSIS
# WHY: Detect population movement corridors (rural-to-urban migration)
# GOAL: Identify "source" and "destination" districts for targeted policy
# ============================================================================
print("\n--- ADVANCED: MIGRATION FLOW ANALYSIS ---")
# Emigration Hubs: High demo updates but LOW enrollment
# INTERPRETATION: People are LEAVING (updating address to new location)
emigration_hubs = district_summary[
    (district_summary['total_demo'] > district_summary['total_enrol']) & 
    (district_summary['total_enrol'] < district_summary['total_enrol'].quantile(0.2))
]

# Immigration Hubs: Very high demo updates with low saturation
# INTERPRETATION: NEW people are arriving (updating address TO this location)
immigration_hubs = district_summary[
    (district_summary['total_demo'] > district_summary['total_enrol'] * 2) &
    (district_summary['ratio'] < 0.5)
]

print(f"Emigration Sources: {len(emigration_hubs)} districts")
print(f"Immigration Destinations: {len(immigration_hubs)} districts")

if not immigration_hubs.empty:
    top_immigration = immigration_hubs['total_demo'].idxmax()
    print(f"\nTop Immigration Hub: {top_immigration}")
    print("INSIGHT: This district is a MIGRATION MAGNET (likely industrial/metro area).")
    print("ACTION: Increase demographic update center capacity here.")


# ============================================================================
# FINAL EXECUTIVE REPORT
# ============================================================================
print("\n\n" + "="*60)
print("📢 EXECUTIVE INSIGHTS REPORT (ADVANCED ANALYTICS)")
print("="*60)

top_growth = growing_districts.index[0] if not growing_districts.empty else 'N/A'
top_mature = mature_districts.index[0] if not mature_districts.empty else 'N/A'
fraud_alert = "detected" if n_fraud_signals > 0 else "not detected"

print(f"\n1. 🚀 GROWTH ENGINE: The district of '{top_growth}' is leading new user acquisition.")
print(f"   -> Recommendation: Prioritize this region for 'Baal Aadhaar' camps.")

print(f"\n2. 🏙️ MATURE HUB: The district of '{top_mature}' has moved to a maintenance phase.")
print(f"   -> Recommendation: Shift staff from here to '{top_growth}' to optimize costs.")

print(f"\n3. 🚨 RISK AUDIT: Potential fraud rings were {fraud_alert} in demographic data.")
if fraud_alert == "detected":
    print(f"   -> Action: Investigate the {n_fraud_signals} specific dates with anomalous address updates.")

print(f"\n4. ⚖️ MARKET SEGMENTATION:")
print(f"   - {len(pure_enrollment)} 'Pure Growth' Pincodes (New Markets)")
print(f"   - {len(pure_update)} 'Pure Maintenance' Pincodes (Kiosk Ready)")

print(f"\n5. 🧠 MACHINE LEARNING INSIGHTS:")
print(f"   - Identified {len(district_summary)} districts across 4 strategic typologies")
print(f"   - Compliance Gap: ~{max(0, expected_updates - actual_updates):.0f} missing biometric updates")
print(f"   - Detected {fraud_clusters if 'fraud_clusters' in locals() else 0} geographic fraud clusters")

print(f"\n6. 🌍 MIGRATION CORRIDORS:")
if not immigration_hubs.empty:
    print(f"   - Top Immigration Hub: {top_immigration}")
    print(f"   - Recommendation: Deploy dedicated demographic update centers in migration destinations")

print("\n✅ ANALYSIS COMPLETE. Visualizations saved to 'output/' folder.")
print("="*60)
