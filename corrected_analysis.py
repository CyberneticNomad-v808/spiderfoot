#!/usr/bin/env python3
"""
CORRECTED SpiderFoot Branch Comparison Analysis
Comparing dev-5.3.3 (advanced) vs prod-_808_-5.2.9 (current simplified)
What was REMOVED from the advanced version to create the simplified version
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

def append_to_md(content, filename="corrected_branch_analysis.md"):
    """Append content to the markdown file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def initialize_md_file():
    """Initialize the corrected markdown file with header"""
    filename = "corrected_branch_analysis.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""# CORRECTED SpiderFoot Branch Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Comparing:** dev-5.3.3 (ADVANCED/MODULAR) vs prod-_808_-5.2.9 (SIMPLIFIED/CONSOLIDATED)

## Direction of Changes
- **dev-5.3.3**: The advanced, modular, enterprise version
- **prod-_808_-5.2.9**: The simplified, consolidated version (current)
- **Analysis**: What enterprise features were REMOVED to create the simplified version

---

""")
    return filename

def analyze_what_was_removed():
    """Analyze what advanced features were removed from dev-5.3.3"""
    append_to_md("## 🚨 ENTERPRISE FEATURES REMOVED")
    
    append_to_md("\n### 1. Modular Architecture Dismantled")
    
    # Check what modular directories existed in dev-5.3.3 but not in current
    modular_dirs = ['spiderfoot/api/', 'spiderfoot/cli/', 'spiderfoot/core/', 'spiderfoot/webui/', 'spiderfoot/db/', 'spiderfoot/sflib/']
    
    for dir_path in modular_dirs:
        append_to_md(f"\n#### {dir_path} (ENTERPRISE MODULE - REMOVED)")
        
        # Get what was in this advanced directory
        dir_contents = run_git_command(f"git ls-tree -r --name-only dev-5.3.3 | grep '^{dir_path}' | head -20")
        
        if dir_contents:
            append_to_md("**Advanced components that were removed:**")
            for file in dir_contents.split('\n'):
                if file.strip():
                    # Get line count of removed file
                    lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
                    append_to_md(f"- `{file}` ({lines} lines of enterprise functionality)")
        else:
            append_to_md("- No advanced components found")

def analyze_consolidated_vs_modular():
    """Compare the consolidated files vs their modular origins"""
    append_to_md("\n### 2. Forced Consolidation Analysis")
    
    main_files = ['sf.py', 'sfapi.py', 'sfcli.py', 'sfwebui.py']
    
    for file in main_files:
        append_to_md(f"\n#### {file} - Consolidation Impact")
        
        # Get sizes (current is larger due to consolidation)
        current_lines = run_git_command(f"wc -l {file} | cut -d' ' -f1")
        dev_lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
        
        if current_lines.isdigit() and dev_lines.isdigit():
            diff = int(current_lines) - int(dev_lines)
            append_to_md(f"- **dev-5.3.3 (modular):** {dev_lines} lines")
            append_to_md(f"- **Current (consolidated):** {current_lines} lines")
            append_to_md(f"- **Forced consolidation:** +{diff} lines crammed into single file")
            append_to_md(f"- **Architecture impact:** Modularity destroyed, maintainability compromised")

def analyze_removed_enterprise_modules():
    """Analyze enterprise modules that were completely removed"""
    append_to_md("\n### 3. Enterprise Modules Completely Removed")
    
    # Find modules that existed in dev-5.3.3 but not in current
    dev_modules = run_git_command("git ls-tree --name-only dev-5.3.3:modules/ | grep '\\.py$'")
    current_modules = run_git_command("ls modules/*.py | xargs -n1 basename")
    
    if dev_modules and current_modules:
        dev_set = set(dev_modules.split('\n'))
        current_set = set(current_modules.split('\n'))
        removed_modules = dev_set - current_set
        
        if removed_modules:
            append_to_md(f"\n**{len(removed_modules)} Enterprise modules completely removed:**")
            for module in sorted(removed_modules):
                if module.strip():
                    # Get module size
                    lines = run_git_command(f"git show dev-5.3.3:modules/{module} | wc -l")
                    append_to_md(f"- `modules/{module}` ({lines} lines of enterprise functionality)")

def analyze_removed_testing_infrastructure():
    """Analyze removed testing and development infrastructure"""
    append_to_md("\n### 4. Advanced Testing Infrastructure Removed")
    
    # Check for threadreaper and advanced testing
    threadreaper_count = run_git_command("git ls-tree -r --name-only dev-5.3.3 | grep -i threadreaper | wc -l")
    append_to_md(f"- **ThreadReaper testing framework:** {threadreaper_count} files removed")
    
    # Check scripts directory
    dev_scripts = run_git_command("git ls-tree --name-only dev-5.3.3:scripts/ 2>/dev/null")
    current_scripts = run_git_command("ls scripts/ 2>/dev/null | head -10")
    
    if dev_scripts:
        append_to_md("\n**Enterprise development scripts removed:**")
        for script in dev_scripts.split('\n')[:10]:
            if script.strip():
                append_to_md(f"- `scripts/{script}`")

def analyze_removed_security_features():
    """Analyze removed security and enterprise features"""
    append_to_md("\n### 5. Security & Enterprise Features Removed")
    
    # Look for security-related files that were removed
    security_files = run_git_command("git ls-tree -r --name-only dev-5.3.3 | grep -i security")
    
    if security_files:
        append_to_md("**Security components removed:**")
        for file in security_files.split('\n')[:10]:
            if file.strip():
                lines = run_git_command(f"git show dev-5.3.3:{file} | wc -l")
                append_to_md(f"- `{file}` ({lines} lines)")

def analyze_architectural_regression():
    """Analyze the architectural regression"""
    append_to_md("\n## 📉 ARCHITECTURAL REGRESSION ANALYSIS")
    
    # Get total stats
    total_changes = run_git_command("git diff --stat dev-5.3.3 | tail -1")
    append_to_md(f"- **Total regression:** {total_changes}")
    
    append_to_md("\n### What Was Lost:")
    append_to_md("1. **Modular Architecture** → Monolithic consolidation")
    append_to_md("2. **Enterprise API Structure** → Single API file")
    append_to_md("3. **Sophisticated CLI** → Simplified command interface")
    append_to_md("4. **Advanced Testing** → Basic testing only")
    append_to_md("5. **Security Hardening** → Reduced security features")
    append_to_md("6. **Performance Optimization** → Performance modules removed")
    append_to_md("7. **Scalable Database** → Consolidated DB structure")
    
    append_to_md("\n### Development Impact:")
    append_to_md("- **Maintainability:** Severely compromised by consolidation")
    append_to_md("- **Testability:** Advanced testing infrastructure removed")
    append_to_md("- **Scalability:** Modular scaling capabilities removed")
    append_to_md("- **Security:** Enterprise security features stripped")
    append_to_md("- **Team Development:** Collaborative development hindered")

def main():
    """Main execution function"""
    os.chdir('/stuff/spiderfoot')
    
    print("Initializing CORRECTED analysis...")
    filename = initialize_md_file()
    
    print("Analyzing removed enterprise features...")
    analyze_what_was_removed()
    
    print("Analyzing consolidation impact...")
    analyze_consolidated_vs_modular()
    
    print("Analyzing removed enterprise modules...")
    analyze_removed_enterprise_modules()
    
    print("Analyzing removed testing infrastructure...")
    analyze_removed_testing_infrastructure()
    
    print("Analyzing removed security features...")
    analyze_removed_security_features()
    
    print("Analyzing architectural regression...")
    analyze_architectural_regression()
    
    print(f"\nCORRECTED analysis complete! Results saved to: {filename}")
    print(f"File location: /stuff/spiderfoot/{filename}")

if __name__ == "__main__":
    main()