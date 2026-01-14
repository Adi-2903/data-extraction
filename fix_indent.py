with open('analysis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix line 270 (index 270, which is the problematic line)
lines[270] = '    print(f"Estimated Missing Updates: {max(0, expected_updates - actual_updates):.0f}")\n'
lines.insert(271, '    print("INSIGHT: This gap represents citizens who haven\'t updated biometrics despite")\n')
lines.insert(272, '    print("         reaching mandatory age triggers (age 5 or 15).")\n')

with open('analysis.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed!")
