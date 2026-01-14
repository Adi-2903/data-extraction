"""
Advanced Formulas Library for Aadhaar Data Analysis
====================================================

This module contains 7 PhD-level mathematical formulas designed to uncover
hidden patterns in government enrollment data. Each formula is explained with:
- Mathematical definition
- Implementation
- Interpretation guidelines
- Real-world application

Author: UIDAI Hackathon 2026 Team
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import entropy


# =============================================================================
# FORMULA 1: Network Effect Score (NES)
# =============================================================================
def calculate_network_effect_score(df, district_col='district'):
    """
    Network Effect Score: Measures if enrollment success spreads to neighbors.
    
    Formula:
    --------
    NES = (Neighbor_Growth × Connectivity) / Own_Growth
    
    Where:
    - Neighbor_Growth = Average enrollment growth in adjacent districts
    - Connectivity = Number of neighboring districts (proxy: similar names)
    - Own_Growth = District's own enrollment growth rate
    
    Interpretation:
    ---------------
    NES > 1.5 = Strong network effect (success spreads to neighbors)
    NES = 1.0 = No network effect (independent growth)
    NES < 0.5 = Negative spillover (success doesn't transfer)
    
    Application:
    ------------
    Identify "seed districts" where investment yields regional impact.
    Example: If Punjab has NES = 2.1, success in one district boosts neighbors.
    """
    district_growth = df.groupby(district_col)['total_enrol'].sum().sort_index()
    
    # Calculate growth rate (simplified: use total as proxy)
    nes_scores = {}
    
    for district in district_growth.index:
        own_growth = district_growth[district]
        
        # Find "neighbors" (districts with similar first 3 letters as proxy)
        prefix = district[:3].lower()
        neighbors = [d for d in district_growth.index if d[:3].lower() == prefix and d != district]
        
        if len(neighbors) > 0 and own_growth > 0:
            neighbor_growth = district_growth[neighbors].mean()
            connectivity = len(neighbors)
            nes = (neighbor_growth * connectivity) / (own_growth + 1)
        else:
            nes = 0
        
        nes_scores[district] = nes
    
    return pd.Series(nes_scores).sort_values(ascending=False)


# =============================================================================
# FORMULA 2: Lifecycle Progression Index (LPI)
# =============================================================================
def calculate_lifecycle_progression_index(df):
    """
    Lifecycle Progression Index: Tracks citizen journey completeness.
    
    Formula:
    --------
    LPI = (Biometric_Updates / Enrollments) × (Demographic_Updates / Enrollments)
    
    Interpretation:
    ---------------
    LPI > 0.5 = Healthy ecosystem (citizens progress through lifecycle)
    LPI = 0.1-0.5 = Moderate (some progression)
    LPI < 0.1 = Stagnant (one-time enrollees, never return)
    
    Application:
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


# =============================================================================
# FORMULA 3: Spatial Autocorrelation (Moran's I)
# =============================================================================
def calculate_morans_i(df, metric='total_enrol', neighbors_threshold=3):
    """
    Moran's I: Measures spatial clustering of enrollment patterns.
    
    Formula:
    --------
    Moran_I = (N / W) × Σ(w_ij × (x_i - x̄) × (x_j - x̄)) / Σ(x_i - x̄)²
    
    Where:
    - N = Number of districts
    - W = Sum of spatial weights
    - w_ij = 1 if districts are neighbors, 0 otherwise
    - x_i = Metric value in district i
    
    Interpretation:
    ---------------
    I > +0.5 = Strong positive clustering (similar districts group together)
    I ≈ 0 = Random spatial pattern
    I < -0.5 = Strong negative clustering (dissimilar neighbors)
    
    Application:
    ------------
    Determine if regional policies work or if each district is independent.
    Example: "North India has I = 0.72 → Regional campaigns are effective"
    """
    district_metrics = df.groupby('district')[metric].sum().reset_index()
    
    # Create simple spatial weight matrix (based on alphabetical proximity as proxy)
    # In real implementation, would use actual geographic coordinates
    districts = district_metrics['district'].values
    values = district_metrics[metric].values
    N = len(districts)
    
    # Simplified spatial weights: adjacent alphabetically
    W = 0
    numerator = 0
    denominator = 0
    
    mean_val = values.mean()
    
    for i in range(N):
        for j in range(N):
            if i != j and abs(i - j) <= neighbors_threshold:  # Spatial proximity proxy
                w_ij = 1
                W += w_ij
                numerator += w_ij * (values[i] - mean_val) * (values[j] - mean_val)
        
        denominator += (values[i] - mean_val) ** 2
    
    if W > 0 and denominator > 0:
        morans_i = (N / W) * (numerator / denominator)
    else:
        morans_i = 0
    
    return morans_i


# =============================================================================
# FORMULA 4: System Load Entropy (Shannon Entropy)
# =============================================================================
def calculate_system_load_entropy(df):
    """
    System Load Entropy: Measures workload distribution across districts.
    
    Formula:
    --------
    SLE = -Σ(p_i × log(p_i))
    
    Where:
    - p_i = Proportion of total transactions handled by district i
    
    Interpretation:
    ---------------
    High entropy (≈ log(N)) = Evenly distributed load (good)
    Low entropy (≈ 1-2) = Concentrated in few districts (bottleneck risk)
    Max entropy = log(number of districts)
    
    Application:
    ------------
    Identify if system load is balanced or if metro hubs are overwhelmed.
    Example: "Entropy = 2.3 (out of 6.9) → Load concentrated in 5 metros"
    """
    district_load = df.groupby('district')['total_activity'].sum()
    
    # Calculate proportions
    proportions = district_load / district_load.sum()
    
    # Shannon entropy
    system_entropy = entropy(proportions, base=2)
    
    # Max possible entropy (uniform distribution)
    max_entropy = np.log2(len(district_load))
    
    # Normalized entropy (0 to 1)
    normalized_entropy = system_entropy / max_entropy if max_entropy > 0 else 0
    
    return {
        'entropy': system_entropy,
        'max_entropy': max_entropy,
        'normalized_entropy': normalized_entropy,
        'concentration': 1 - normalized_entropy  # Higher = more concentrated
    }


# =============================================================================
# FORMULA 5: Migration Directionality Index (MDI)
# =============================================================================
def calculate_migration_directionality_index(df):
    """
    Migration Directionality Index: Identifies emigration vs immigration hubs.
    
    Formula:
    --------
    MDI = (Out_Migration - In_Migration) / (Out_Migration + In_Migration)
    
    Where:
    - Out_Migration = Demographic updates without recent enrollment (leaving)
    - In_Migration = Enrollment without demographic updates (arriving)
    
    Interpretation:
    ---------------
    MDI > +0.5 = Strong emigration source (people leaving)
    MDI ≈ 0 = Balanced (similar in/out flows)
    MDI < -0.5 = Strong immigration destination (people arriving)
    
    Application:
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


# =============================================================================
# FORMULA 6: Update Cascade Probability (UCP)
# =============================================================================
def calculate_update_cascade_probability(df):
    """
    Update Cascade Probability: Predicts full lifecycle completion rate.
    
    Formula:
    --------
    UCP = P(Bio_Update | Demo_Update) × P(Demo_Update | Enrollment)
    
    Where conditional probabilities are estimated from historical data.
    
    Interpretation:
    ---------------
    UCP = 0.12 means "12% of new enrollments complete full lifecycle"
    
    Application:
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
    # P(Demo | Enrol)
    p_demo_given_enrol = district_summary['total_demo'] / (district_summary['total_enrol'] + 1)
    
    # P(Bio | Demo)
    p_bio_given_demo = district_summary['total_bio'] / (district_summary['total_demo'] + 1)
    
    # Update Cascade Probability
    ucp = p_demo_given_enrol * p_bio_given_demo
    
    return {
        'mean_ucp': ucp.mean(),
        'median_ucp': ucp.median(),
        'p_demo_given_enrol': p_demo_given_enrol.mean(),
        'p_bio_given_demo': p_bio_given_demo.mean(),
        'district_ucp': ucp.sort_values(ascending=False)
    }


# =============================================================================
# FORMULA 7: Fraud Ring Cohesion Score (FRCS)
# =============================================================================
def calculate_fraud_ring_cohesion_score(df, suspicious_clusters):
    """
    Fraud Ring Cohesion Score: Distinguishes mass camps from coordinated fraud.
    
    Formula:
    --------
    FRCS = (Cluster_Density × Temporal_Synchrony) / Expected_Random_Density
    
    Where:
    - Cluster_Density = Demographic updates per km² (using pincode as proxy)
    - Temporal_Synchrony = Proportion of updates on same date
    - Expected_Random_Density = Baseline for region
    
    Interpretation:
    ---------------
    FRCS > 5 = Likely coordinated fraud (refer to enforcement)
    FRCS = 2-5 = Suspicious (investigate)
    FRCS < 2 = Normal mass camp event
    
    Application:
    ------------
    Prioritize fraud investigation resources on high-cohesion clusters.
    Example: "Cluster #3 has FRCS = 12.4 → Immediate audit required"
    """
    frcs_scores = []
    
    for cluster_id in suspicious_clusters['cluster'].unique():
        if cluster_id == -1:  # Skip noise points
            continue
        
        cluster_data = suspicious_clusters[suspicious_clusters['cluster'] == cluster_id]
        
        # Cluster density (updates per unique pincode)
        cluster_density = len(cluster_data) / (cluster_data['pincode'].nunique() + 1)
        
        # Temporal synchrony (% on most common date)
        if 'date' in cluster_data.columns:
            most_common_date_count = cluster_data['date'].value_counts().iloc[0]
            temporal_synchrony = most_common_date_count / len(cluster_data)
        else:
            temporal_synchrony = 0.5  # Default
        
        # Expected random density (baseline = 1.0)
        expected_density = 1.0
        
        # Calculate FRCS
        frcs = (cluster_density * temporal_synchrony) / expected_density
        
        frcs_scores.append({
            'cluster_id': cluster_id,
            'size': len(cluster_data),
            'density': cluster_density,
            'synchrony': temporal_synchrony,
            'FRCS': frcs
        })
    
    return pd.DataFrame(frcs_scores).sort_values('FRCS', ascending=False)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def interpret_nes(nes_value):
    """Interpret Network Effect Score"""
    if nes_value > 1.5:
        return "🟢 Strong network effect - Success spreads to neighbors"
    elif nes_value > 0.8:
        return "🟡 Moderate network effect"
    else:
        return "🔴 No network effect - District operates independently"


def interpret_lpi(lpi_value):
    """Interpret Lifecycle Progression Index"""
    if lpi_value > 0.5:
        return "🟢 Healthy ecosystem - Citizens complete lifecycle"
    elif lpi_value > 0.1:
        return "🟡 Moderate progression"
    else:
        return "🔴 Stagnant - One-time enrollees only"


def interpret_mdi(mdi_value):
    """Interpret Migration Directionality Index"""
    if mdi_value > 0.5:
        return "🔴 Strong emigration source - People leaving"
    elif mdi_value > 0:
        return "🟡 Slight emigration tendency"
    elif mdi_value > -0.5:
        return "🟡 Slight immigration tendency"
    else:
        return "🟢 Strong immigration destination - People arriving"


def interpret_entropy(normalized_entropy):
    """Interpret System Load Entropy"""
    if normalized_entropy > 0.7:
        return "🟢 Well-distributed load across districts"
    elif normalized_entropy > 0.4:
        return "🟡 Moderately balanced"
    else:
        return "🔴 Highly concentrated - Bottleneck risk in few metros"


if __name__ == "__main__":
    print("Advanced Formulas Library for Aadhaar Analysis")
    print("=" * 50)
    print("\n7 PhD-Level Formulas Available:")
    print("1. Network Effect Score (NES)")
    print("2. Lifecycle Progression Index (LPI)")
    print("3. Spatial Autocorrelation (Moran's I)")
    print("4. System Load Entropy (Shannon Entropy)")
    print("5. Migration Directionality Index (MDI)")
    print("6. Update Cascade Probability (UCP)")
    print("7. Fraud Ring Cohesion Score (FRCS)")
    print("\nImport these functions into your analysis scripts!")
