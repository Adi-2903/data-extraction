import pandas as pd
import glob

print('='*60)
print('DATA QUALITY AUDIT - DISTRICT ANALYSIS')
print('='*60)

# Load enrollment data
enrol_files = glob.glob('dataset/api_data_aadhar_enrolment*.csv')
enrol_df = pd.concat([pd.read_csv(f) for f in enrol_files], ignore_index=True)
print(f'\n[ENROLLMENT DATA]:')
print(f'   Total Records: {len(enrol_df):,}')
print(f'   Columns: {list(enrol_df.columns)}')
if 'district' in enrol_df.columns:
    enrol_districts = enrol_df['district'].dropna().str.strip().str.lower().unique()
    print(f'   Unique Districts: {len(enrol_districts)}')
    print(f'   Sample: {list(enrol_districts[:10])}')

# Load demographic data
demo_files = glob.glob('dataset/api_data_aadhar_demographic*.csv')
demo_df = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)
print(f'\n[DEMOGRAPHIC DATA]:')
print(f'   Total Records: {len(demo_df):,}')
print(f'   Columns: {list(demo_df.columns)}')
if 'district' in demo_df.columns:
    demo_districts = demo_df['district'].dropna().str.strip().str.lower().unique()
    print(f'   Unique Districts: {len(demo_districts)}')

# Load biometric data
bio_files = glob.glob('dataset/api_data_aadhar_biometric*.csv')
bio_df = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)
print(f'\n[BIOMETRIC DATA]:')
print(f'   Total Records: {len(bio_df):,}')
print(f'   Columns: {list(bio_df.columns)}')
if 'district' in bio_df.columns:
    bio_districts = bio_df['district'].dropna().str.strip().str.lower().unique()
    print(f'   Unique Districts: {len(bio_districts)}')

print('\n' + '='*60)
print('DETAILED DISTRICT ANALYSIS')
print('='*60)

# Combine all districts
all_districts = set()
if 'district' in enrol_df.columns:
    all_districts.update(enrol_df['district'].dropna().str.strip().str.lower().unique())
if 'district' in demo_df.columns:
    all_districts.update(demo_df['district'].dropna().str.strip().str.lower().unique())
if 'district' in bio_df.columns:
    all_districts.update(bio_df['district'].dropna().str.strip().str.lower().unique())

print(f'\n[!] COMBINED UNIQUE DISTRICTS: {len(all_districts)}')
print(f'   Expected in India: 800-850')
print(f'   Difference: {len(all_districts) - 800} (if positive = potential duplicates/variants)')

# Check for potential duplicates (similar names)
sorted_districts = sorted(all_districts)
print(f'\n[LIST] All unique district names (sorted):')
for i, d in enumerate(sorted_districts[:50]):
    print(f'   {i+1}. {d}')
print(f'   ... and {len(sorted_districts) - 50} more')

# Look for common data quality issues
print('\n' + '='*60)
print('POTENTIAL DATA QUALITY ISSUES')
print('='*60)

# Check for numeric-looking districts
numeric_districts = [d for d in all_districts if d.replace(' ', '').isdigit()]
print(f'\n[WARN] Numeric districts: {len(numeric_districts)}')
if numeric_districts:
    print(f'   Examples: {numeric_districts[:10]}')

# Check for very short names (likely incomplete)
short_districts = [d for d in all_districts if len(d) <= 2]
print(f'\n[WARN] Very short names (<=2 chars): {len(short_districts)}')
if short_districts:
    print(f'   Examples: {short_districts[:10]}')

# Check for null/empty-like values
null_like = [d for d in all_districts if d in ['', 'null', 'none', 'na', 'nan', '-', 'undefined']]
print(f'\n[WARN] Null-like values: {len(null_like)}')

# State analysis
print('\n' + '='*60)
print('STATE ANALYSIS')
print('='*60)
if 'state' in enrol_df.columns:
    states = enrol_df['state'].dropna().str.strip().str.lower().unique()
    print(f'   Unique States in Enrollment: {len(states)}')
    print(f'   Sample: {list(states[:10])}')

