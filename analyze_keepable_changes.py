#!/usr/bin/env python3
"""
Analysis of what changes can be kept vs what needs to be scratched
due to database architecture conflicts with dev-5.3.3
"""

import subprocess
import os

def run_git_command(cmd):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/stuff/spiderfoot')
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def analyze_keepable_changes():
    """Analyze what changes we can keep when upgrading to dev-5.3.3"""
    
    print("# Changes Analysis: What to Keep vs Scratch")
    print("\n## 🔴 MUST SCRATCH (Database Architecture Conflicts)")
    
    # Database files that conflict with dev-5.3.3 modular approach
    db_conflicts = [
        "spiderfoot/db.py",
        "spiderfoot_db.py", 
        "spiderfoot_db.py.backup.*",
        "claudes_decoys/db*.py*",
        "init-postgres-db.sh.donotuse"
    ]
    
    for item in db_conflicts:
        print(f"- {item} - Conflicts with modular db/ architecture in dev-5.3.3")
    
    print("\n## 🟢 CAN KEEP (Non-conflicting improvements)")
    
    # Check non-database changes
    keepable = run_git_command("git diff HEAD~10 --name-only | grep -v -E '(db|database|spiderfoot_db)'")
    
    if keepable:
        keepable_files = keepable.split('\n')
        
        # Categorize keepable changes
        categories = {
            'Documentation': [],
            'Docker/Deployment': [], 
            'Build/CI': [],
            'Configuration': [],
            'Modules': [],
            'Core Features': [],
            'Other': []
        }
        
        for file in keepable_files:
            if not file.strip():
                continue
                
            file = file.strip()
            
            if any(x in file.lower() for x in ['.md', 'readme', 'doc']):
                categories['Documentation'].append(file)
            elif any(x in file.lower() for x in ['docker', 'deploy', 'build']):
                categories['Docker/Deployment'].append(file)
            elif any(x in file.lower() for x in ['.yml', '.yaml', 'pipfile', '.sh']):
                categories['Build/CI'].append(file)
            elif any(x in file.lower() for x in ['config', '.env', '.json']):
                categories['Configuration'].append(file)
            elif file.startswith('modules/'):
                categories['Modules'].append(file)
            elif file.startswith('spiderfoot/'):
                categories['Core Features'].append(file)
            else:
                categories['Other'].append(file)
        
        for category, files in categories.items():
            if files:
                print(f"\n### {category}")
                for file in files[:10]:  # Limit output
                    print(f"- {file}")
                if len(files) > 10:
                    print(f"  ... and {len(files)-10} more")
    
    print("\n## 🤔 NEED EVALUATION (May conflict)")
    
    # Check for potential conflicts
    potential_conflicts = run_git_command("git diff HEAD~10 --name-only | grep -E '(sf\\.py|sfapi\\.py|sfcli\\.py|sfwebui\\.py)'")
    
    if potential_conflicts:
        print("Main files that were consolidated but may conflict with modular approach:")
        for file in potential_conflicts.split('\n'):
            if file.strip():
                print(f"- {file} - May need to be reverted to modular structure")
    
    print("\n## 📋 RECOMMENDED ACTION PLAN")
    print("1. **Keep all deployment/Docker improvements** - These add value")
    print("2. **Keep documentation enhancements** - Good for project")  
    print("3. **Keep module improvements** - If they don't conflict with dev-5.3.3 versions")
    print("4. **Scratch all database consolidation** - Replace with modular db/ architecture")
    print("5. **Evaluate main file changes** - May need to revert to support modular structure")
    print("6. **Keep build/CI improvements** - Infrastructure improvements are valuable")

if __name__ == "__main__":
    os.chdir('/stuff/spiderfoot')
    analyze_keepable_changes()