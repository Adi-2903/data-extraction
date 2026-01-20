import subprocess
import os
import sys
import time

def run_step(step_name, command):
    print(f"\n>>> [STEP] {step_name}")
    print(f"Running: {command}")
    start_time = time.time()
    try:
        # Use sys.executable to ensure we use the same python environment
        result = subprocess.run([sys.executable] + command.split(), check=True, text=True)
        end_time = time.time()
        print(f"--- [OK] {step_name} completed in {end_time - start_time:.2f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"!!! [ERROR] {step_name} failed with exit code {e.returncode}")
        return False

def main():
    print("======================================================================")
    print("   AADHAR-MANTHAN: AADHAAR INTELLIGENCE PIPELINE (MASTER) ")
    print("======================================================================")
    
    steps = [
        ("Data Cleaning", "clean_data.py"),
        ("Analytical Engine", "analysis.py"),
        ("Senior Analyst (Strategic Reasoning)", "senior_analyst_agent.py"),
        ("Submission Generation", "generate_ultimate_submission.py")
    ]
    
    for name, script in steps:
        if not run_step(name, script):
            print("\n!!! PIPELINE HALTED due to error.")
            sys.exit(1)
            
    print("\n======================================================================")
    print("   PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"   Final Document: submission/UIDAI_Hackathon_ULTIMATE.docx")
    print("======================================================================")

if __name__ == "__main__":
    main()
