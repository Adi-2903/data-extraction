# Script to move Data Quality block to after Master Cube

with open('analysis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the Data Quality block (after Phase 3, before Phase 4)
quality_start = None
quality_end = None
phase4_start = None

for i, line in enumerate(lines):
    if 'PHASE 4.2: DATA QUALITY' in line:
        quality_start = i - 2  # Include the separator lines
    elif quality_start is not None and 'PHASE 4: MASTER CUBE' in line:
        quality_end = i - 2
        phase4_start = i
        break

if quality_start and quality_end:
    # Extract the block
    quality_block = lines[quality_start:quality_end]
    
    # Remove it from original position
    del lines[quality_start:quality_end]
    
    # Find where to insert (after "Fraud Probability Index Calculated.")
    insert_pos = None
    for i, line in enumerate(lines):
        if 'print("Fraud Probability Index Calculated.")' in line:
            insert_pos = i + 1
            break
    
    if insert_pos:
        # Insert with proper spacing
        lines.insert(insert_pos, '\n')
        lines.insert(insert_pos + 1, '\n')
        for j, block_line in enumerate(quality_block):
            lines.insert(insert_pos + 2 + j, block_line)
        
        print(f"Moved Data Quality block from line {quality_start} to line {insert_pos}")
    
    # Write back
    with open('analysis.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("Done!")
else:
    print("Could not find blocks")
