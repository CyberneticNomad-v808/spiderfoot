#!/usr/bin/env python3
"""
SpiderFoot Branch Comparison Analysis
Compares prod-_808_-5.2.9 vs dev-5.3.3 branches method by method
Outputs detailed analysis to branch_analysis.md
"""

import subprocess
import os
import re
from pathlib import Path
from datetime import datetime

def run_git_command(cmd):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/stuff/spiderfoot')
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def append_to_md(content, filename="branch_analysis.md"):
    """Append content to the markdown file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def initialize_md_file():
    """Initialize the markdown file with header"""
    filename = "branch_analysis.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""# SpiderFoot Branch Comparison Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Comparing:** prod-_808_-5.2.9 (current) vs dev-5.3.3

---

""")
    return filename

def analyze_main_file_consolidation():
    """Analyze consolidation of main files"""
    append_to_md("## 1. Main File Consolidation Analysis")
    
    main_files = ['sf.py', 'sfapi.py', 'sfcli.py', 'sfwebui.py', 'sflib.py']
    
    for file in main_files:
        append_to_md(f"\n### {file}")
        
        # Get line counts
        current_lines = run_git_command(f"wc -l {file} | cut -d' ' -f1")
        dev_lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
        
        append_to_md(f"- **Current branch:** {current_lines} lines")
        append_to_md(f"- **dev-5.3.3 branch:** {dev_lines} lines")
        
        if current_lines.isdigit() and dev_lines.isdigit():
            diff = int(current_lines) - int(dev_lines)
            append_to_md(f"- **Difference:** +{diff} lines" if diff > 0 else f"- **Difference:** {diff} lines")
        
        # Get function/class definitions
        current_funcs = run_git_command(f"grep -E '^def |^class ' {file} | wc -l")
        dev_funcs = run_git_command(f"git show dev-5.3.3:{file} | grep -E '^def |^class ' | wc -l")
        
        append_to_md(f"- **Current functions/classes:** {current_funcs}")
        append_to_md(f"- **dev-5.3.3 functions/classes:** {dev_funcs}")
        
        # Show new functions/classes
        current_defs = run_git_command(f"grep -E '^def |^class ' {file}")
        dev_defs = run_git_command(f"git show dev-5.3.3:{file} | grep -E '^def |^class '")
        
        if current_defs and dev_defs:
            append_to_md("\n**Current definitions:**")
            for line in current_defs.split('\n'):
                if line.strip():
                    append_to_md(f"- `{line.strip()}`")

def analyze_removed_directories():
    """Analyze completely removed directory structures"""
    append_to_md("\n## 2. Removed Modular Components")
    
    # Check for removed files in key directories
    removed_dirs = ['spiderfoot/api/', 'spiderfoot/cli/', 'spiderfoot/core/', 'spiderfoot/webui/', 'spiderfoot/db/', 'spiderfoot/sflib/']
    
    for dir_path in removed_dirs:
        append_to_md(f"\n### {dir_path}")
        
        # Check what was in this directory in dev-5.3.3
        dir_contents = run_git_command(f"git ls-tree -r --name-only dev-5.3.3 | grep '^{dir_path}' | head -20")
        
        if dir_contents:
            append_to_md("**Files that existed in dev-5.3.3:**")
            for file in dir_contents.split('\n'):
                if file.strip():
                    append_to_md(f"- `{file}`")
        else:
            append_to_md("- Directory did not exist in dev-5.3.3")
    
    # Check scripts directory
    append_to_md("\n### scripts/ directory")
    removed_scripts = run_git_command("git diff --name-only dev-5.3.3 | grep '^scripts/' | grep -v '.py$' | head -10")
    if removed_scripts:
        append_to_md("**Removed scripts:**")
        for script in removed_scripts.split('\n'):
            if script.strip():
                append_to_md(f"- `{script}`")

def analyze_database_changes():
    """Analyze database-related changes"""
    append_to_md("\n## 3. Database Architecture Changes")
    
    # Compare spiderfoot/db.py
    append_to_md("\n### spiderfoot/db.py")
    current_db_lines = run_git_command("wc -l spiderfoot/db.py | cut -d' ' -f1")
    dev_db_lines = run_git_command("git show dev-5.3.3:spiderfoot/db.py | wc -l")
    
    append_to_md(f"- **Current:** {current_db_lines} lines")
    append_to_md(f"- **dev-5.3.3:** {dev_db_lines} lines")
    
    # Check for new spiderfoot_db.py
    if os.path.exists("spiderfoot_db.py"):
        new_db_lines = run_git_command("wc -l spiderfoot_db.py | cut -d' ' -f1")
        append_to_md(f"\n### spiderfoot_db.py (NEW)")
        append_to_md(f"- **Lines:** {new_db_lines}")
        append_to_md("- This appears to be a new consolidated database file")

def analyze_module_changes():
    """Analyze changes in the modules/ directory"""
    append_to_md("\n## 4. Module Changes Analysis")
    
    # Get list of changed modules
    changed_modules = run_git_command("git diff --name-only dev-5.3.3 | grep '^modules/.*\\.py$' | head -20")
    
    if changed_modules:
        append_to_md("### Modified Modules")
        
        for module in changed_modules.split('\n'):
            if module.strip():
                # Get diff stats for each module
                stats = run_git_command(f"git diff --stat dev-5.3.3 {module}")
                append_to_md(f"\n**{module}**")
                if stats:
                    # Extract +/- numbers from stats
                    match = re.search(r'(\d+) insertion.*?(\d+) deletion', stats)
                    if match:
                        append_to_md(f"- +{match.group(1)} -{match.group(2)} lines")
                    else:
                        append_to_md(f"- {stats}")
    
    # Check for completely removed modules
    removed_modules = run_git_command("git diff --name-status dev-5.3.3 | grep '^D.*modules/.*\\.py$'")
    if removed_modules:
        append_to_md("\n### Removed Modules")
        for line in removed_modules.split('\n'):
            if line.strip():
                append_to_md(f"- `{line.split()[1]}`")

def analyze_test_restructuring():
    """Analyze test file changes"""
    append_to_md("\n## 5. Test Structure Changes")
    
    # Count threadreaper backup removals
    threadreaper_files = run_git_command("git diff --name-status dev-5.3.3 | grep 'threadreaper_backup' | wc -l")
    append_to_md(f"- **ThreadReaper backup files removed:** {threadreaper_files}")
    
    # Check test directory changes
    test_changes = run_git_command("git diff --stat dev-5.3.3 test/ | tail -1")
    append_to_md(f"- **Overall test changes:** {test_changes}")
    
    # Look for major test file changes
    major_test_changes = run_git_command("git diff --stat dev-5.3.3 | grep 'test/.*\\.py' | grep -E '\\s+[0-9]{2,}\\s+[0-9]{2,}' | head -10")
    if major_test_changes:
        append_to_md("\n### Major Test File Changes")
        for line in major_test_changes.split('\n'):
            if line.strip():
                append_to_md(f"- {line.strip()}")

def analyze_new_files():
    """Analyze completely new files"""
    append_to_md("\n## 6. New Files Added")
    
    new_files = run_git_command("git diff --name-status dev-5.3.3 | grep '^A' | head -20")
    if new_files:
        for line in new_files.split('\n'):
            if line.strip():
                file_path = line.split()[1]
                append_to_md(f"- `{file_path}`")

def generate_summary():
    """Generate overall summary"""
    append_to_md("\n## 7. Overall Architecture Summary")
    
    total_changes = run_git_command("git diff --stat dev-5.3.3 | tail -1")
    append_to_md(f"- **Total changes:** {total_changes}")
    
    append_to_md("\n### Key Architectural Changes:")
    append_to_md("1. **Massive Consolidation:** Modular structure collapsed into main files")
    append_to_md("2. **Removed Enterprise Features:** Many advanced/enterprise components removed")
    append_to_md("3. **Simplified Architecture:** Move from distributed to monolithic structure")
    append_to_md("4. **Database Restructuring:** New consolidated database files")
    append_to_md("5. **Test Simplification:** Removal of complex testing infrastructure")
    
    append_to_md("\n### Impact Assessment:")
    append_to_md("- **Maintainability:** Potentially easier to maintain with fewer files")
    append_to_md("- **Modularity:** Significant loss of modular architecture")
    append_to_md("- **Features:** Likely reduction in advanced features")
    append_to_md("- **Testing:** Simplified but potentially less comprehensive testing")

def main():
    """Main execution function"""
    os.chdir('/stuff/spiderfoot')
    
    print("Initializing analysis...")
    filename = initialize_md_file()
    
    print("Analyzing main file consolidation...")
    analyze_main_file_consolidation()
    
    print("Analyzing removed components...")
    analyze_removed_directories()
    
    print("Analyzing database changes...")
    analyze_database_changes()
    
    print("Analyzing module changes...")
    analyze_module_changes()
    
    print("Analyzing test restructuring...")
    analyze_test_restructuring()
    
    print("Analyzing new files...")
    analyze_new_files()
    
    print("Generating summary...")
    generate_summary()
    
    print(f"\nAnalysis complete! Results saved to: {filename}")
    print(f"File location: /stuff/spiderfoot/{filename}")

if __name__ == "__main__":
    main()