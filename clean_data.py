"""
Data Cleaning Script for UIDAI Aadhaar Datasets
================================================
Standardizes state and district names to canonical forms.
"""

import pandas as pd
import glob
import os
import re

# ============================================================================
# STATE STANDARDIZATION MAPPING
# ============================================================================
STATE_MAPPING = {
    # West Bengal variants
    'west  bengal': 'west bengal',
    'west bangal': 'west bengal',
    'west bengli': 'west bengal',
    'westbengal': 'west bengal',
    
    # Chhattisgarh
    'chhatisgarh': 'chhattisgarh',
    
    # Odisha
    'orissa': 'odisha',
    
    # Uttarakhand
    'uttaranchal': 'uttarakhand',
    
    # Puducherry
    'pondicherry': 'puducherry',
    
    # Tamil Nadu
    'tamilnadu': 'tamil nadu',
    
    # Andaman & Nicobar Islands
    'andaman & nicobar islands': 'andaman and nicobar islands',
    
    # Jammu & Kashmir
    'jammu & kashmir': 'jammu and kashmir',
    
    # Dadra and Nagar Haveli (now merged with Daman & Diu)
    'dadra & nagar haveli': 'dadra and nagar haveli and daman and diu',
    'dadra and nagar haveli': 'dadra and nagar haveli and daman and diu',
    'the dadra and nagar haveli and daman and diu': 'dadra and nagar haveli and daman and diu',
    'daman & diu': 'dadra and nagar haveli and daman and diu',
    'daman and diu': 'dadra and nagar haveli and daman and diu',
    
    # Invalid city names -> Map to correct state (best effort)
    'balanagar': 'telangana',          # Balanagar is in Hyderabad, Telangana
    'darbhanga': 'bihar',              # Darbhanga is in Bihar
    'jaipur': 'rajasthan',             # Jaipur is in Rajasthan
    'nagpur': 'maharashtra',           # Nagpur is in Maharashtra
    'madanapalle': 'andhra pradesh',   # Madanapalle is in Andhra Pradesh
    'puttenahalli': 'karnataka',       # Puttenahalli is in Bengaluru, Karnataka
    'raja annamalai puram': 'tamil nadu',  # R.A. Puram is in Chennai, Tamil Nadu
    
    # Invalid numeric
    '100000': None,  # Will be marked as invalid
}

# ============================================================================
# DISTRICT STANDARDIZATION MAPPING
# ============================================================================
DISTRICT_MAPPING = {
    # Ahmedabad
    'ahmadabad': 'ahmedabad',
    
    # Ahmednagar
    'ahmadnagar': 'ahmednagar',
    'ahmed nagar': 'ahmednagar',
    'ahilyanagar': 'ahmednagar',  # Renamed in Maharashtra
    
    # Anantapur variants
    'ananthapur': 'anantapur',
    'ananthapuramu': 'anantapur',
    
    # Angul
    'anugul': 'angul',
    'anugul  *': 'angul',
    
    # Ashoknagar
    'ashok nagar': 'ashoknagar',
    
    # Trailing asterisks removal (generic patterns handled in clean_text)
    'auraiya *': 'auraiya',
    'bagalkot *': 'bagalkot',
    'baghpat *': 'baghpat',
    'bokaro *': 'bokaro',
    'chamarajanagar *': 'chamarajanagar',
    'chandauli *': 'chandauli',
    'chitrakoot *': 'chitrakoot',
    
    # Baghpat
    'bagpat': 'baghpat',
    
    # Banaskantha
    'banas kantha': 'banaskantha',
    
    # Barabanki
    'bara banki': 'barabanki',
    
    # Bardhaman
    'barddhaman': 'bardhaman',
    
    # Bulandshahr
    'bulandshahar': 'bulandshahr',
    
    # Buldhana
    'buldana': 'buldhana',
    
    # Chamarajanagar
    'chamrajanagar': 'chamarajanagar',
    'chamrajnagar': 'chamarajanagar',
    
    # Chhatrapati Sambhajinagar
    'chatrapati sambhaji nagar': 'chhatrapati sambhajinagar',
    
    # Chikmagalur - NEW
    'chickmagalur': 'chikmagalur',
    'chikkamagaluru': 'chikmagalur',
    
    # Chittorgarh
    'chittaurgarh': 'chittorgarh',
    
    # Cooch Behar
    'coochbehar': 'cooch behar',
    
    # Dadra and Nagar Haveli
    'dadra & nagar haveli': 'dadra and nagar haveli',
    
    # Davangere
    'davanagere': 'davangere',
    
    # Invalid entries
    '100000': None,
    '?': None,
    '5th cross': None,
    'akhera': None,
    
    # Raebareli
    'rae bareli': 'raebareli',
    'rai bareilly': 'raebareli',
    'raibarely': 'raebareli',
    
    'sahibganj': 'sahebganj',
    'sant kabir nagar': 'sant kabeer nagar',
    'sant ravidas nagar': 'sant ravidas nagar (bhadohi)',
    'sarangarh-bilaigarh': 'sarangarh bilaigarh',
    'sheopurkalan': 'sheopur',
    'shi yomi': 'shi-yomi',
    'siddharthnagar': 'siddharth nagar',
    'sri ganganagar': 'ganganagar',
    
    'y.s.r.': 'ysr kadapa',
    'y.s.r. kadapa': 'ysr kadapa',
    'ysr': 'ysr kadapa',
    
    # 24 Paraganas
    '24 paraganas north': 'north 24 parganas',
    '24 paraganas south': 'south 24 parganas',
    
    # Medinipur
    'pashchim medinipur': 'paschim medinipur',
    'east midnapore': 'purba medinipur',
    'east midnapur': 'purba medinipur',
    'west midnapore': 'paschim medinipur',
    
    'baleshwar': 'balasore',
    'kheri': 'lakhimpur kheri',
    'faizabad': 'ayodhya',
    'allahabad': 'prayagraj',
    
    # ====== NEW MAPPINGS FROM SECOND PASS ======
    
    # Gaurela-Pendra-Marwahi
    'gaurela-pendra-marwahi': 'gaurella pendra marwahi',
    
    # Haridwar
    'hardwar': 'haridwar',
    
    # Hassan
    'hasan': 'hassan',
    
    # Hazaribagh
    'hazaribag': 'hazaribagh',
    
    # Hooghly
    'hooghiy': 'hooghly',
    
    # Jagatsinghpur
    'jagatsinghapur': 'jagatsinghpur',
    
    # Jajpur
    'jajapur': 'jajpur',
    
    # Jalore
    'jalor': 'jalore',
    
    # Janjgir-Champa
    'janjgir - champa': 'janjgir-champa',
    'janjgir champa': 'janjgir-champa',
    
    # Jhunjhunu
    'jhunjhunun': 'jhunjhunu',
    
    # Ranga Reddy
    'k.v. rangareddy': 'rangareddy',
    'k.v.rangareddy': 'rangareddy',
    
    # Kanchipuram
    'kancheepuram': 'kanchipuram',
    
    # Kanyakumari
    'kanniyakumari': 'kanyakumari',
    
    # Karimnagar
    'karim nagar': 'karimnagar',
    
    # Kasaragod
    'kasargod': 'kasaragod',
    
    # Khordha
    'khorda': 'khordha',
    
    # Koderma
    'kodarma': 'koderma',
    
    # Kushinagar
    'kushi nagar': 'kushinagar',
    
    # Lahaul and Spiti
    'lahul and spiti': 'lahaul and spiti',
    
    # Singhbhum
    'east singhbum': 'east singhbhum',
    
    # Mahabubnagar
    'mahabub nagar': 'mahabubnagar',
    'mahaboobnagar': 'mahabubnagar',
    
    # Malerkotla
    'maler kotla': 'malerkotla',
    
    # Mayurbhanj
    'mayurabhanj': 'mayurbhanj',
    
    # Medak / Medchal
    'medchal malkajgiri': 'medchal-malkajgiri',
    
    # Mewat -> Nuh
    'mewat': 'nuh',
    
    # Mirzapur
    'mirzpur': 'mirzapur',
    
    # Moga
    'mojha': 'moga',
    
    # Muzaffarnagar
    'muzaffar nagar': 'muzaffarnagar',
    
    # Nagapattinam
    'nagapatnam': 'nagapattinam',
    
    # Nalanda
    'naladna': 'nalanda',
    
    # Narmada
    'narmadapuram': 'narmada',
    
    # Nilgiris
    'the nilgiris': 'nilgiris',
    
    # Palakkad
    'palghat': 'palakkad',
    
    # Panchkula
    'panchakula': 'panchkula',
    
    # Papum Pare
    'papumpare': 'papum pare',
    
    # Purnia
    'purnea': 'purnia',
    
    # Puruliya
    'purulia': 'puruliya',
    
    # Raichur
    'raichoor': 'raichur',
    
    # Ramgarh
    'ramghar': 'ramgarh',
    
    # Rupnagar
    'ropar': 'rupnagar',
    
    # Samastipur
    'samasthipur': 'samastipur',
    
    # Saran
    'saaran': 'saran',
    
    # Saraikela-Kharsawan
    'saraikela kharsawan': 'saraikela-kharsawan',
    'seraikella kharsawan': 'saraikela-kharsawan',
    
    # Sitapur
    'sitapurl': 'sitapur',
    
    # Sonipat
    'sonepat': 'sonipat',
    
    # Srikakulam
    'srikakulum': 'srikakulam',
    
    # Supaul
    'supoul': 'supaul',
    
    # Tiruchirapalli
    'tiruchirappalli': 'tiruchirappalli',
    'trichy': 'tiruchirappalli',
    
    # Tirunelveli
    'thirunelveli': 'tirunelveli',
    
    # Tiruvannamalai
    'thiruvannamalai': 'tiruvannamalai',
    
    # Virudhunagar
    'virudunagar': 'virudhunagar',
    
    # Vizianagaram
    'vizayanagaram': 'vizianagaram',
    
    # Warangal
    'warangal urban': 'warangal',
    'warangal rural': 'warangal',
    
    # ====== FINAL BATCH - TRUE DUPLICATES ======
    
    # Mahabubnagar
    'mahbubnagar': 'mahabubnagar',
    
    # Maharajganj
    'mahrajganj': 'maharajganj',
    
    # Malda/Maldah
    'maldah': 'malda',
    
    # Mamit
    'mammit': 'mamit',
    
    # Medchal-Malkajgiri (fix special character)
    'medchal?malkajgiri': 'medchal-malkajgiri',
    
    # Mohla-Manpur
    'mohalla-manpur-ambagarh chowki': 'mohla-manpur-ambagarh chouki',
    
    # Nabarangpur/Nabarangapur
    'nabarangapur': 'nabarangpur',
    
    # Nagarkurnool
    'nagar kurnool': 'nagarkurnool',
    
    # Nicobar/Nicobars
    'nicobars': 'nicobar',
    
    # North Tripura variations
    'north': None,  # Invalid standalone
    
    # Pakaur -> Pakur
    'pakaur': 'pakur',
    
    # Pali/Palli
    'palli': 'pali',
    
    # Ramanathapuram
    'ramanathpuram': 'ramanathapuram',
    
    # Senapati
    'senapat': 'senapati',
    
    # Shimla
    'shimoga': 'shivamogga',  # Renamed
    
    # South Tripura variations  
    'south': None,  # Invalid standalone
    
    # Sri Potti Sriramulu Nellore
    'sri potti sriramulu nellore': 'spsr nellore',
    's.p.s.r nellore': 'spsr nellore',
    
    # Subarnapur/Sonapur
    'subarnapur': 'sonepur',
    
    # Surguja
    'sarguja': 'surguja',
    
    # Thane
    'thana': 'thane',
    
    # Thiruvananthapuram
    'trivandrum': 'thiruvananthapuram',
    
    # Vikarabad
    'vikrabad': 'vikarabad',
    
    # Villupuram
    'viluppuram': 'villupuram',
    
    # Wanaparthy
    'wanaparthi': 'wanaparthy',
    
    # West Tripura variations
    'west': None,  # Invalid standalone
}



def clean_text(text):
    """Clean and standardize text"""
    if pd.isna(text):
        return None
    text = str(text).strip().lower()
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove trailing asterisks and special chars
    text = re.sub(r'\s*\*\s*$', '', text)
    return text


def standardize_state(state):
    """Standardize state name"""
    if pd.isna(state):
        return None
    cleaned = clean_text(state)
    if cleaned in STATE_MAPPING:
        return STATE_MAPPING[cleaned]
    return cleaned


def standardize_district(district):
    """Standardize district name"""
    if pd.isna(district):
        return None
    cleaned = clean_text(district)
    if cleaned in DISTRICT_MAPPING:
        return DISTRICT_MAPPING[cleaned]
    return cleaned


def clean_dataset(df, dataset_name):
    """Apply cleaning to a dataframe"""
    print(f"\n{'='*60}")
    print(f"Cleaning {dataset_name}")
    print(f"{'='*60}")
    
    original_rows = len(df)
    
    # Clean state
    if 'state' in df.columns:
        original_states = df['state'].nunique()
        df['state'] = df['state'].apply(standardize_state)
        # Remove rows with invalid states (None mapping)
        invalid_states = df['state'].isna().sum()
        df = df.dropna(subset=['state'])
        new_states = df['state'].nunique()
        print(f"States: {original_states} -> {new_states} unique")
        if invalid_states > 0:
            print(f"  Removed {invalid_states} rows with invalid states")
    
    # Clean district
    if 'district' in df.columns:
        original_districts = df['district'].nunique()
        df['district'] = df['district'].apply(standardize_district)
        # Remove rows with invalid districts (None mapping)
        invalid_districts = df['district'].isna().sum()
        df = df.dropna(subset=['district'])
        new_districts = df['district'].nunique()
        print(f"Districts: {original_districts} -> {new_districts} unique")
        if invalid_districts > 0:
            print(f"  Removed {invalid_districts} rows with invalid districts")
    
    final_rows = len(df)
    print(f"Rows: {original_rows:,} -> {final_rows:,} ({original_rows - final_rows} removed)")
    
    return df


def main():
    print("="*60)
    print("UIDAI DATA CLEANING PIPELINE")
    print("="*60)
    
    # Create output directory
    output_dir = 'dataset_cleaned'
    os.makedirs(output_dir, exist_ok=True)
    
    # Process Enrollment data
    enrol_files = glob.glob('dataset/api_data_aadhar_enrolment*.csv')
    if enrol_files:
        enrol_df = pd.concat([pd.read_csv(f) for f in enrol_files], ignore_index=True)
        enrol_df = clean_dataset(enrol_df, "ENROLLMENT")
        enrol_df.to_csv(f'{output_dir}/enrollment_cleaned.csv', index=False)
        print(f"Saved to {output_dir}/enrollment_cleaned.csv")
    
    # Process Demographic data
    demo_files = glob.glob('dataset/api_data_aadhar_demographic*.csv')
    if demo_files:
        demo_df = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)
        demo_df = clean_dataset(demo_df, "DEMOGRAPHIC")
        demo_df.to_csv(f'{output_dir}/demographic_cleaned.csv', index=False)
        print(f"Saved to {output_dir}/demographic_cleaned.csv")
    
    # Process Biometric data
    bio_files = glob.glob('dataset/api_data_aadhar_biometric*.csv')
    if bio_files:
        bio_df = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)
        bio_df = clean_dataset(bio_df, "BIOMETRIC")
        bio_df.to_csv(f'{output_dir}/biometric_cleaned.csv', index=False)
        print(f"Saved to {output_dir}/biometric_cleaned.csv")
    
    # Final validation
    print("\n" + "="*60)
    print("FINAL VALIDATION")
    print("="*60)
    
    # Load cleaned data and check counts
    all_states = set()
    all_districts = set()
    
    for f in glob.glob(f'{output_dir}/*.csv'):
        df = pd.read_csv(f)
        if 'state' in df.columns:
            all_states.update(df['state'].dropna().unique())
        if 'district' in df.columns:
            all_districts.update(df['district'].dropna().unique())
    
    print(f"\nCombined unique states: {len(all_states)}")
    print(f"Combined unique districts: {len(all_districts)}")
    print(f"\nExpected: ~36 states, ~800 districts")
    
    if len(all_districts) > 900:
        print("\n[WARNING] District count still high - may need additional mappings")
    else:
        print("\n[SUCCESS] Data cleaning complete!")


if __name__ == "__main__":
    main()
